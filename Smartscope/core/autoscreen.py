
import os
# import sys
# from django.conf import settings
# import multiprocessing
import logging

logger = logging.getLogger(__name__)


from .interfaces.microscope import Detector, AtlasSettings, Microscope
from .interfaces.microscope_methods import select_microscope_interface
# from Smartscope.server.api.models import 
from smartscope_connector import models
from smartscope_connector.api_interface import rest_api_interface as restAPI
from . import flagfiles
from .grid.grid_status import GridStatus

from Smartscope.core.status import status
# from Smartscope.core.db_manipulations import update

from Smartscope.lib.logger import add_log_handlers

from .run_grid import run_grid


def autoscreen(session_id:str):
    '''
    major procedure: autoscreen
    '''
    session: models.ScreeningSession = restAPI.get_single(object_id=session_id,output_type=models.ScreeningSession)
    microscope: models.Microscope = restAPI.get_single(object_id=session.microscope_id,output_type=models.Microscope)
    detector: models.Detector = restAPI.get_single(object_id=session.detector_id,output_type=models.Detector)
    # add_log_handlers(directory=session.directory, name='run.out')
    logger.debug(f'Main Log handlers:{logger.handlers}')
    # process = create_process(session)
    flagfiles.check_stop_file(session.stop_file)
    flagfiles.check_scope_locked(microscope.lock_file)
    flagfiles.write_session_lock(session.uid, microscope.lock_file)

    try:
        grids = restAPI.get_many(models.AutoloaderGrid, session_id=session.uid)
        # logger.info(f'Process: {process}')
        logger.info(f'Session: {session}')
        logger.info(f"Grids: {', '.join([grid.__str__() for grid in grids])}")
        scope_interface = select_microscope_interface(microscope)
        
        with scope_interface(
                microscope = Microscope.model_validate(microscope,from_attributes=True),
                detector= Detector.model_validate(detector,from_attributes=True),
                atlas_settings= AtlasSettings.model_validate(detector,from_attributes=True)
            ) as scope:
            # processing_queue = multiprocessing.JoinableQueue()
            # child_process = multiprocessing.Process(
            #     target=processing_worker_wrapper,
            #     args=(session.directory, processing_queue,)
            # )
            # child_process.start()
            # logger.debug(f'Main Log handlers:{logger.handlers}')
            
            # RUN grid
            for grid in grids:
                status = run_grid(grid, session, microscope, scope)
            # status = 'complete'
    except Exception as e:
        logger.exception(e)
        status = 'error'
        if grid in locals():
            restAPI.update(grid, status=GridStatus.ERROR)
    except KeyboardInterrupt:
        logger.info('Stopping Smartscope.py autoscreen')
        status = 'killed'
    finally:
        flagfiles.remove_scope_lock_file(microscope.lock_file)
        # restAPI.update(process, status=status)
        logger.debug('Wrapping up')
        # processing_queue.put('exit')
        # child_process.join()
        logger.debug('Process joined')



# def create_process(session):
#     process = session.process_set.first()

#     if process is None:
#         process = Process(session_id=session, PID=os.getpid(), status='running')
#         process = process.save()
#         return process

#     return update(process, PID=os.getpid(), status='running')


