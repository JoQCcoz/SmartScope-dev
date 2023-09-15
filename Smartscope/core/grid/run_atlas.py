from Smartscope.core.models import AtlasModel, AutoloaderGrid
from ..api_interface import rest_api_interface as restAPI
from ..status import status



class RunAtlas:
    
    @staticmethod
    def get_atlas(grid:AutoloaderGrid):
        atlas = restAPI.get_many(output_type=AtlasModel, grid_id=grid.uid).first()
        if atlas is not None:
            return atlas

        atlas = AtlasModel(
            name=f'{grid.name}_atlas',
            grid_id=grid.uid)
        return atlas
    
    @staticmethod
    def queue_atlas(atlas):
        if atlas.status != status.NULL:
            return atlas
        return restAPI.update(atlas, status=status.STARTED)
        
        
