'''
'''
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

from .finders import find_targets
from .run_io import get_file_and_process, load_montage

import smartscope_connector.models as models
from smartscope_connector.Datatypes.querylist import QueryList
from smartscope_connector.api_interface import rest_api_interface as restAPI

from Smartscope.core.selectors import selector_wrapper
from Smartscope.core.status import status
from Smartscope.core.protocols import load_protocol
from Smartscope.core.data_manipulations import add_targets, select_n_areas, filter_targets
# from Smartscope.core.db_manipulations import update, select_n_areas, add_targets, group_holes_for_BIS
from Smartscope.lib.image_manipulations import export_as_png
from Smartscope.lib.image.montage import Montage

class RunSquare:

    @staticmethod
    def process_square_image(square, grid, microscope):
        protocol = load_protocol().square.targets
        params = restAPI.get_single(object_id=grid.params_id,output_type=models.GridCollectionParams)
        
        is_bis = params.bis_max_distance > 0
        montage = None
        if square.status == status.ACQUIRED:
            logger.info(f'Processing {square}')
            montage = get_file_and_process(
                raw=square.raw,
                name=square.name,
                directory=microscope.scope_path
            )
            export_as_png(montage.image, montage.png)
            square = restAPI.update(square,
                status=status.PROCESSED,
                shape_x=montage.shape_x,
                shape_y=montage.shape_y,
                pixel_size=montage.pixel_size
            )

        if square.status == status.PROCESSED:
            if not 'montage' in locals():
                montage = load_montage(square.name)
            targets, finder_method, classifier_method, _ = find_targets(montage, protocol.finders)
            logger.debug(f'Ready to add {len(targets)} targets')
            targets = add_targets(
                targets=targets,
                model=models.HoleModel,
                finder=finder_method,
                classifier=classifier_method,
                square_id=square.uid,
                grid_id=grid.uid
            )
            targets = restAPI.post_many(instances=targets, output_type=models.HoleModel, route_suffixes=['add_targets'])
            square = restAPI.update(square,
                status=status.TARGETS_PICKED,
                shape_x=montage.shape_x,
                shape_y=montage.shape_y,
                pixel_size=montage.pixel_size
            )

        if square.status == status.TARGETS_PICKED:
            logger.debug(f'Square has {len(square.targets)} targets')
            square = selector_wrapper(protocol.selectors, square, n_groups=5, montage=montage)
            outputs = restAPI.post_many(instances=QueryList(square.targets), output_type=models.HoleModel, route_suffixes=['add_targets'], label_types='selectors')
            square = restAPI.update(square, status=status.TARGETS_SELECTED)
            square.targets = outputs
            if is_bis:
                holes = group_holes_for_BIS(
                    filter_targets(square),
                    max_radius=params.bis_max_distance,
                    min_group_size=params.min_bis_group_size
                )
                logger.debug(holes)
                holes = QueryList(holes)
                restAPI.update_many(instances=holes, selected=True, status=status.QUEUED)
            logger.info(f'Picking holes on {square}')

            selection = select_n_areas(square, params.holes_per_square, is_bis=is_bis)
            logger.debug(selection)
            selection = QueryList(selection)
            restAPI.update_many(instances=selection, selected=True, status=status.QUEUED)
            square = restAPI.update(square, status=status.TARGETS_SELECTED)
        if square.status == status.TARGETS_SELECTED:
            square = restAPI.update(square,
                status=status.COMPLETED,
                completion_time=timezone.now()
            )
        if square.status == status.COMPLETED:
            logger.info(f'Square {square.name} analysis is complete')

