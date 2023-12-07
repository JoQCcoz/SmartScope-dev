from typing import List
import numpy as np
# from django.db import transaction
import cv2

# from django.contrib.contenttypes.models import ContentType
# from django.db.models.query import prefetch_related_objects

from Smartscope.core.models.target_label import Selector
from Smartscope.lib.image.montage import Montage
from Smartscope.core.settings.worker import PLUGINS_FACTORY
from Smartscope.lib.image_manipulations import save_image, to_8bits, auto_contrast

import logging
logger = logging.getLogger(__name__)


# def generate_equal_clusters(targets, n_groups, extra_fields=dict()):
#     if len(targets) == 0:
#         return targets
#     split_targets = np.array_split(targets, n_groups)
#     for ind, bucket in enumerate(split_targets):
#         for target in bucket:
#             extra_updates = dict()
#             for field, attribute in extra_fields.items():
#                 extra_updates[field] = getattr(target,attribute)
#             target.selectors.append(**extra_updates, label=ind, method_name='cluster_by_field')
#     return targets


def cluster_by_field(parent, field='area', method_name='cluster_by_field',**kwargs):
    for ind,target in enumerate(parent.targets):
        value = getattr(target, field)
        parent.targets[ind].selectors.append(Selector(value=value, method_name=method_name))
    return parent


def gray_level_selector(parent,montage:Montage, save=True,method_name='gray_level_selector', **kwargs): 
    logger.debug(f'Initial targets = {len(parent.targets)}')
    if montage is None:
        montage = Montage(**parent.__dict__, working_dir=parent.grid_id.directory)
        montage.create_dirs()
    # if save:
    #     img = cv2.bilateralFilter(auto_contrast(montage.image.copy()), 30, 75, 75)
    for ind,target in enumerate(parent.targets):
        finder = list(target.finders.all())[0]
        x, y = finder.x, finder.y
        median = np.mean(montage.image[y - target.radius:y + target.radius, x - target.radius:x + target.radius])
        parent.targets[ind].selectors.append.append(Selector(value=median, method_name=method_name))
        # if save:
        #     cv2.circle(img, (x, y), target.radius, target.median, 10)

    # if save:
    #     save_image(img, 'gray_level_selector', extension='png', destination=parent.directory, resize_to=1024)

    return parent


def selector_wrapper(selectors, selection, *args, **kwargs):
    logger.info(f'Running selectors {selectors} on {selection}')
    for method in selectors:
        method = PLUGINS_FACTORY[method]
        outputs = method.run(selection, method_name=method.name, *args, **kwargs)
        return outputs
