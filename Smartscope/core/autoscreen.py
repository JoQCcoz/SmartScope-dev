
import os
# import sys
# from django.conf import settings
# import multiprocessing
import logging

logger = logging.getLogger(__name__)


from .interfaces.microscope import Detector, AtlasSettings
from .interfaces.microscope_methods import select_microscope_interface
# from Smartscope.server.api.models import 
from .models import Microscope,ScreeningSession, Detector
from .api_interface.rest_api_interface import get_single
import .flagfiles
from .grid.grid_status import GridStatus

from Smartscope.core.status import status
from Smartscope.core.db_manipulations import update

from Smartscope.lib.logger import add_log_handlers

from .run_grid import run_grid


def autoscreen(session_id:str):
    '''
    major procedure: autoscreen
    '''
    session: ScreeningSession = get_single(object_id=session_id,output_type=ScreeningSession)
    microscope: Microscope = get_single(object_id=session.microscope_id,output_type=Microscope)
    detector: Detector = get_single(object_id=session.microscope_id,output_type=Detector)
    # add_log_handlers(directory=session.directory, name='run.out')
    # logger.debug(f'Main Log handlers:{logger.handlers}')
    # process = create_process(session)
    flagfiles.check_stop_file(session.stop_file)
    flagfiles.check_scope_locked(microscope.lock_file)
    flagfiles.write_session_lock(session, microscope.lockFile)

    try:
        grids = list(session.autoloadergrid_set.all().order_by('position'))
        # logger.info(f'Process: {process}')
        logger.info(f'Session: {session}')
        logger.info(f"Grids: {', '.join([grid.__str__() for grid in grids])}")
        scopeInterface, additional_settings = select_microscope_interface(microscope)

        with scopeInterface(
                additional_settings=additional_settings
                microscope = microscope,
                detector= detector,
                atlas_settings= AtlasSettings.model_validate(detector)
            ) as scope:
            # processing_queue = multiprocessing.JoinableQueue()
            # child_process = multiprocessing.Process(
            #     target=processing_worker_wrapper,
            #     args=(session.directory, processing_queue,)
            # )
            # child_process.start()
            logger.debug(f'Main Log handlers:{logger.handlers}')

            # RUN grid
            for grid in grids:
                status = run_grid(grid, session, scope)
            status = 'complete'
    except Exception as e:
        logger.exception(e)
        status = 'error'
        if 'grid' in locals():
            update.grid = grid
            update(grid, status=GridStatus.ERROR)
    except KeyboardInterrupt:
        logger.info('Stopping Smartscope.py autoscreen')
        status = 'killed'
    finally:
        os.remove(microscope.lockFile)
        # update(process, status=status)
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


