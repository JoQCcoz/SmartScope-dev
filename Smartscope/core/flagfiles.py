from pathlib import Path

class MicroscopeBusyError(Exception):

    def __init__(self, lock_file, session):
        self.message = f"""
        The requested microscope is busy.
        Lock file {lock_file} found
        Session id: {session} is currently running.
        If you are sure that the microscope is not running,
        remove the lock file and restart.
        Exiting.
        """
        return super().__init__(self.message)

def check_scope_locked(file:Path) -> None:
    if not file.exists():
        return 
    raise MicroscopeBusyError(file, file.read_text())

def write_session_lock(session:str, lockFile:Path) -> None:
    with open(lockFile, 'w') as f:
        f.write(session)

def check_stop_file(stop_file:Path) -> None:
    if not stop_file.exists():
        return
    stop_file.unlink()
    raise KeyboardInterrupt(f'Stop file {stop_file} found.')