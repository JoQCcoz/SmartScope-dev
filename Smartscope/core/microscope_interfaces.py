from pathlib import PureWindowsPath
from Smartscope.lib.Datatypes.microscope import MicroscopeInterface
import serialem as sem
import time
import logging
import math
import numpy as np
from Smartscope.lib.Finders.basic_finders import find_square
from Smartscope.lib.image_manipulations import generate_hole_ref


from Smartscope.lib.file_manipulations import generate_fake_file

logger = logging.getLogger(__name__)


class CartridgeLoadingError(Exception):
    pass


class GatanSerialemInterface(MicroscopeInterface):

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

    def eucentricHeight(self, tiltTo=10, increments=-5):
        logger.info(f'Doing eucentric height')
        offsetZ = 51
        iteration = 0
        while abs(offsetZ) > 50 and iteration != 3:
            iteration += 1
            logger.info(f'Staring iteration {iteration}')
            alignments = []
            stageZ = sem.ReportStageXYZ()[2]
            sem.TiltTo(tiltTo)
            currentAngle = int(sem.ReportTiltAngle())
            sem.Search()
            loop = 0
            while currentAngle > 0:
                loop += 1
                sem.TiltBy(increments)
                currentAngle = int(sem.ReportTiltAngle())
                sem.Search()
                sem.AlignTo('B', 1)
                alignments.append(sem.ReportAlignShift()[5] / math.sin(math.radians(abs(increments) * loop)))

            logger.debug(alignments)
            offsetZ = sum(alignments) / (len(alignments) * 1000)
            totalZ = stageZ + offsetZ
            if abs(totalZ) < 200:
                logger.info(f'Moving by {offsetZ} um')

                sem.MoveStage(0, 0, offsetZ)
                time.sleep(0.2)
            else:
                logger.info('Eucentric alignement would send the stage too far, stopping Eucentricity.')
                break

    def atlas(self, mag, c2, spotsize, tileX, tileY, file='', center_stage_x=0, center_stage_y=0):
        logger.debug(f'Atlas mag:{mag}, c2perc:{c2}, spotsize:{spotsize}, tileX:{tileX}, tileY:{tileY}')
        sem.TiltTo(0)
        sem.MoveStageTo(center_stage_x, center_stage_y)
        sem.SetLowDoseMode(0)
        sem.SetMag(int(mag))
        sem.SetPercentC2(float(c2))
        sem.SetSpotSize(int(spotsize))
        if self.energyfilter:
            sem.SetSlitIn(0)
        self.eucentricHeight()
        sem.OpenNewMontage(tileX, tileY, file)
        self.checkDewars()
        self.checkPump()
        logger.info('Starting Atlas acquisition')
        sem.Montage()
        sem.CloseFile()
        sem.SetLowDoseMode(1)
        logger.info('Atlas acquisition finished')

    def square(self, stageX, stageY, stageZ, file=''):
        sem.SetLowDoseMode(1)
        logger.info(f'Starting Square acquisition of: {file}')
        logger.debug(f'Moving stage to: X={stageX}, Y={stageY}, Z={stageZ}')
        time.sleep(0.2)
        sem.MoveStageTo(stageX, stageY, stageZ)
        stageX, stageY, stageZ = self.realign_to_square()
        sem.Eucentricity(1)
        self.checkDewars()
        self.checkPump()
        sem.MoveStageTo(stageX, stageY)
        time.sleep(0.2)
        sem.Search()
        sem.OpenNewFile(file)
        sem.Save()
        sem.CloseFile()
        logger.info('Square acquisition finished')
        return stageX, stageY, stageZ

    def realign_to_square(self):
        while True:
            logger.info('Running square realignment')
            sem.Search()
            square = np.asarray(sem.bufferImage('A'))
            _, square_center, _ = find_square(square)
            im_center = (square.shape[1] // 2, square.shape[0] // 2)
            diff = square_center - np.array(im_center)
            logger.info(f'Found square center: {square_center}. Image-shifting by {diff} pixels')
            sem.ImageShiftByPixels(int(diff[0]), -int(diff[1]))
            sem.ResetImageShift()
            if max(diff) < max(square.shape) // 4:
                logger.info('Done.')
                sem.Search()
                break
            logger.info('Iterating.')
        return sem.ReportStageXYZ()

    def align(self):
        sem.View()
        sem.CropCenterToSize('A', self.hole_crop_size, self.hole_crop_size)
        sem.AlignTo('T')
        return sem.ReportAlignShift()

    def make_hole_ref(self, hole_size_in_um):

        # sem.View()
        # img = np.asarray(sem.bufferImage('A'))
        # dtype = img.dtype
        # shape_x, shape_y, _, _, pixel_size, _ = sem.ImageProperties('A')
        # logger.debug(f'\nImage dtype: {dtype}\nPixel size: {pixel_size}')
        # ref = generate_hole_ref(hole_size_in_um, pixel_size * 10, out_type=dtype)
        # self.hole_crop_size = int(min([shape_x, shape_y, ref.shape[0] * 1.5]))
        # sem.PutImageInBuffer(ref, 'T', ref.shape[0], ref.shape[1])
        sem.ReadOtherFile(0, 'T', 'reference/holeref.mrc')  # Will need to change in the future for more flexibility
        shape_x, _, _, _, _, _ = sem.ImageProperties('T')
        self.hole_crop_size = int(shape_x)
        self.has_hole_ref = True

    def lowmagHole(self, stageX, stageY, stageZ, tiltAngle, hole_size_in_um, file='', aliThreshold=500):

        sem.TiltTo(tiltAngle)

        sem.AllowFileOverwrite(1)
        sem.SetImageShift(0, 0)
        sem.MoveStageTo(stageX, stageY, stageZ)
        time.sleep(0.2)
        if hole_size_in_um is not None:
            if not self.has_hole_ref:
                self.make_hole_ref(hole_size_in_um=hole_size_in_um)
            # sem.ReadOtherFile(0, 'T', 'reference/holeref.mrc')  # Will need to change in the future for more flexibility
            aligned = self.align()
            holeshift = math.sqrt(aligned[4]**2 + aligned[5]**2)
            if holeshift > aliThreshold:
                if tiltAngle == 0:
                    sem.ResetImageShift()
                else:
                    iShift = sem.ReportImageShift()
                    sem.MoveStage(iShift[4], iShift[5] * math.cos(math.radians(tiltAngle)))
                    time.sleep(0.2)
                # sem.LimitNextAutoAlign(hole_size_in_um * 0.4)
                aligned = self.align()
        self.checkDewars()
        self.checkPump()
        sem.View()
        sem.OpenNewFile(file)
        sem.Save()
        sem.CloseFile()

    def focusDrift(self, def1, def2, step, drifTarget):
        self.rollDefocus(def1, def2, step)
        sem.SetTargetDefocus(self.state.defocusTarget)
        sem.AutoFocus()
        self.state.currentDefocus = sem.ReportDefocus()
        if drifTarget > 0:
            sem.DriftWaitTask(drifTarget, 'A', 300, 10, -1, 'T', 1)

    def highmag(self, isX, isY, tiltAngle, file='', frames=True):

        sem.ImageShiftByMicrons(isX - self.state.imageShiftX, isY - self.state.imageShiftY, 0)
        self.state.imageShiftX = isX
        self.state.imageShiftY = isY
        sem.SetDefocus(self.state.currentDefocus - isY * math.sin(math.radians(tiltAngle)))

        if not frames:
            sem.EarlyReturnNextShot(-1)
            sem.Preview()
            sem.OpenNewFile(file)
            sem.Save()
            sem.CloseFile()
            return None

        sem.EarlyReturnNextShot(0)

        sem.Preview()  # Seems possible to change this to Record in 4.0, needs testing
        frames = sem.ReportLastFrameFile()
        if isinstance(frames, tuple):  # Workaround since the output of the ReportFrame command changed in 4.0, need to test ans simplify
            frames = frames[0]
        logger.debug(f"Frames: {frames},")
        return frames.split('\\')[-1]

    def connect(self, directory: str):
        logger.info(
            f'Initiating connection to SerialEM at: {self.ip}:{self.port}\n\t If no more messages show up after this one and the External Control notification is not showing up on the SerialEM interface, there is a problem. \n\t The best way to solve it is generally by closing and restarting SerialEM.')
        sem.ConnectToSEM(self.port, self.ip)
        sem.SetDirectory(directory)
        sem.ClearPersistentVars()
        sem.AllowFileOverwrite(1)

    def setup(self, saveframes, zerolossDelay, framesName=None):
        if saveframes:
            logger.info('Saving frames enabled')
            sem.SetDoseFracParams('P', 1, 1, 0)
            movies_directory = PureWindowsPath(self.frames_directory).as_posix().replace('/', '\\')
            logger.info(f'Saving frames to {movies_directory}')
            sem.SetFolderForFrames(movies_directory)
            if framesName is not None:
                sem.SetFrameBaseName(0, 1, 0, framesName)
        else:
            logger.info('Saving frames disabled')
            sem.SetDoseFracParams('P', 1, 0, 1)

        if self.energyfilter and zerolossDelay > 0:
            sem.RefineZPL(zerolossDelay * 60, 1)
        sem.KeepCameraSetChanges('P')
        sem.SetLowDoseMode(1)

    def disconnect(self, close_valves=True):
        logger.info("Closing Valves and disconnecting from SerialEM")
        if close_valves:
            try:
                sem.SetColumnOrGunValve(0)
            except:
                logger.warning("Could not close the column valves, still disconnecting from SerialEM")
        sem.Exit(1)

    def loadGrid(self, position):
        if self.loader_size > 1:
            slot_status = sem.ReportSlotStatus(position)
            if slot_status == -1:
                raise ValueError(f'SerialEM return an error when reading slot {position} of the autoloader.')
            if slot_status == 1:
                logger.info(f'Autoloader position is occupied')
                logger.info(f'Loading grid {position}')
                sem.Delay(5)
                sem.SetColumnOrGunValve(0)
                sem.LoadCartridge(position)
            logger.info(f'Grid {position} is loaded')
            sem.Delay(5)
            if sem.ReportSlotStatus(position) != 0:
                raise CartridgeLoadingError('Cartridge did not load properly. Stopping')
        sem.SetColumnOrGunValve(1)


class FalconSerialemInterface(GatanSerialemInterface):

    def square(self, stageX, stageY, stageZ, file=''):
        sem.SetLowDoseMode(1)
        logger.info(f'Starting Square acquisition of: {file}')
        logger.debug(f'Moving stage to: X={stageX}, Y={stageY}, Z={stageZ}')
        time.sleep(0.2)
        sem.MoveStageTo(stageX, stageY, stageZ)
        sem.Eucentricity()
        self.checkDewars()
        self.checkPump()
        sem.MoveStageTo(stageX, stageY)
        time.sleep(0.2)
        sem.Search()
        sem.OpenNewFile(file)
        sem.Save()
        sem.CloseFile()
        logger.info('Square acquisition finished')

    def highmag(self, isX, isY, tiltAngle, file='', frames=True):

        sem.ImageShiftByMicrons(isX - self.state.imageShiftX, isY - self.state.imageShiftY, 0)
        self.state.imageShiftX = isX
        self.state.imageShiftY = isY
        sem.SetDefocus(self.state.currentDefocus - isY * math.sin(math.radians(tiltAngle)))

        sem.Preview()
        sem.OpenNewFile(file)
        sem.Save()
        sem.CloseFile()
        if not frames:
            return None

        frames = sem.ReportLastFrameFile()
        if isinstance(frames, tuple):  # Workaround since the output of the ReportFrame command changed in 4.0, need to test ans simplify
            frames = frames[0]
        logger.debug(f"Frames: {frames},")
        return frames.split('\\')[-1]


class FakeScopeInterface(MicroscopeInterface):

    def checkDewars(self, wait=30) -> None:
        pass

    def checkPump(self, wait=30):
        pass

    def eucentricHeight(self, tiltTo=10, increments=-5) -> float:
        pass

    def atlas(self, mag, c2, spotsize, tileX, tileY, file='', center_stage_x=0, center_stage_y=0):
        generate_fake_file(file, 'atlas', destination_dir=self.scope_path)

    def square(self, stageX, stageY, stageZ, file=''):
        generate_fake_file(file, 'square', sleeptime=15, destination_dir=self.scope_path)

    def align():
        pass

    def lowmagHole(self, stageX, stageY, stageZ, tiltAngle, hole_size_in_um, file='', is_negativestain=False, aliThreshold=500):
        generate_fake_file(file, 'lowmagHole', sleeptime=10, destination_dir=self.scope_path)

    def focusDrift(self, def1, def2, step, drifTarget):
        pass

    def highmag(self, isX, isY, tiltAngle, file='', frames=True):
        # if frames:
        #     generate_fake_file(file.replace('raw', 'movies').replace('mrc', 'tif'), 'highmagframes', sleeptime=7, destination_dir=self.scope_path)
        generate_fake_file(file, 'highmag', sleeptime=7, destination_dir=self.scope_path)

    def connect(self, directory: str):
        logger.info('Connecting to fake scope.')

    def setup(self, saveframes, zerolossDelay, framesName=None):
        pass

    def disconnect(self, close_valves=True):
        logger.info('Disconnecting from fake scope.')

    def loadGrid(self, position):
        pass
