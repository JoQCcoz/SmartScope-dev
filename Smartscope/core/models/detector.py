from pydantic import Field
from .base_model import SmartscopeBaseModel
from .microscope import Microscope

DETECTOR_CHOICES = (
    ('K2', 'Gatan K2'),
    ('K3', 'Gatan K3'),
    ('Ceta', 'FEI Ceta'),
    ('Falcon3', 'TFS Falcon 3'),
    ('Falcon4', 'TFS Falcon 4')
)

class Detector(SmartscopeBaseModel):


    name: str
    uid :int = Field(alias='id')
    microscope_id:str
    detector_model: str
    atlas_mag: int
    atlas_max_tiles_X: int
    atlas_max_tiles_Y: int
    spot_size: int
    c2_perc: float
    atlas_c2_aperture: int
    # atlas_to_search_offset_x: float
    # atlas_to_search_offset_y: float
    # frame_align_cmd = models.CharField(max_length=30, default='alignframes')
    gain_rot: int = 0
    gain_flip: bool = True
    energy_filter: bool = False
    frames_windows_directory: str = 'movies'
    frames_directory: str = '/mnt/scope/movies/'

    class Meta(SmartscopeBaseModel.Meta):
        api_route = 'detectors'

