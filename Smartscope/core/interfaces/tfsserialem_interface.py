import serialem as sem
from typing import Callable, Optional
import functools
import time
import logging
from .serialem_interface import SerialemInterface

logger = logging.getLogger(__name__)

class Aperture:
    CONDENSER_1:int=0
    CONDENSER_2:int=1
    CONDENSER_3:int=2
    OBJECTIVE:int = 3

def change_aperture_temporarily(function: Callable, aperture:Aperture, aperture_size:Optional[int], *args, **kwargs):
    def wrapper(*args, **kwargs):
        inital_aperture_size = sem.ReportApertureSize(aperture)
        if inital_aperture_size == aperture_size or aperture_size is None:
            return function(*args, **kwargs) 
        sem.SetApertureSize(aperture,aperture_size)
        function(*args, **kwargs)
        sem.SetApertureSize(aperture,inital_aperture_size)
    return wrapper    

def remove_objective_aperture(function: Callable, *args, **kwargs):
    def wrapper(*args, **kwargs):
        sem.RemoveAperture(2)
        function(*args, **kwargs)
        sem.ReInsertAperture(2)
    return wrapper

class TFSSerialemInterface(SerialemInterface):

    def checkDewars(self, wait=30):
        while True:
            if sem.AreDewarsFilling() == 0:
                return
            logger.info(f'LN2 is refilling, waiting {wait}s')
            time.sleep(wait)

    def checkPump(self, wait=30):
        while True:
            if sem.IsPVPRunning() == 0:
                return
            logger.info(f'Pump is Running, waiting {wait}s')
            time.sleep(wait)

    def atlas(self, size, file=''):
        if self.microscope.apertureControl:
            return change_aperture_temporarily(
                function=remove_objective_aperture(
                    super().atlas(size,file)
                    ), 
                aperture=Aperture.CONDENSER_2,
                aperture_size=self.atlas_settings.atlas_c2_aperture
            )
        return super().atlas(size, file)