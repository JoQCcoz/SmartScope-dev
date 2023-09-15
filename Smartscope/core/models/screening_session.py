from pathlib import Path
from pydantic import Field
from datetime import datetime
from .base_model import SmartscopeBaseModel
from pydantic import field_validator
from Smartscope.lib.image.smartscope_storage import SmartscopeStorage
from Smartscope.core.settings import worker
from Smartscope import __version__ as SmartscopeVersion

class ScreeningSession(SmartscopeBaseModel):
    # from .microscope import Microscope
    # from .detector import Detector
    uid: str = Field(alias='session_id')
    session:str
    group: str
    date: datetime
    version: str
    microscope_id: str
    detector_id: str
    working_dir: str

    class Meta:
        api_route = 'sessions'

    @field_validator('detector_id', mode='before')
    @classmethod
    def detector_id_validator(cls,v) -> str:
        if isinstance(v,str):
            return v
        return str(v)
    
    # @property
    # def directory(self):
    #     return Path(worker.AUTOSCREENDIR, self.working_dir)


    @property
    def stop_file(self):
        return Path(worker.TEMPDIR, f'{self.uid}.stop')
    
    # @property
    # def progress(self):
    #     statuses= self.autoloadergrid_set.all().values_list('status', flat=True)
    #     completed = list(filter(lambda x: x == 'complete',statuses))
    #     return len(completed), len(statuses), int(len(completed)/len(statuses)*100)

    # @property
    # def currentGrid(self):
    #     return self.autoloadergrid_set.all().order_by('position')\
    #         .exclude(status='complete').first()

    # @property
    # def storage(self):
    #     return os.path.join(settings.AUTOSCREENSTORAGE, self.working_dir)

