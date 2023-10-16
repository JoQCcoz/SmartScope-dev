import logging
from Smartscope.core.models import AtlasModel, AutoloaderGrid
from ..api_interface import rest_api_interface as restAPI
from ..status import status

logger = logging.getLogger(__name__)

class RunAtlas:
    
    @staticmethod
    def get_atlas(grid:AutoloaderGrid):
        logger.info(f'Getting atlas for grid {grid.name}')
        atlas = restAPI.get_many(output_type=AtlasModel, grid_id=grid.uid).first()

        if atlas is not None:
            logger.info(f'Found atlas')
            return atlas
        logger.info(f'Creating atlas')
        atlas = AtlasModel(
            name=f'{grid.name}_atlas',
            grid_id=grid.uid)
        return restAPI.post_single(instance=atlas)
    
    @staticmethod
    def queue_atlas(atlas):
        logger.info(f'Initial status: {atlas.status}')
        if atlas.status != status.NULL:
            return atlas
        return restAPI.update(atlas, status=status.STARTED)
        
        
