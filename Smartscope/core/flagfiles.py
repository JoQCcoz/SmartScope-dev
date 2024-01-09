from pathlib import Path
from .settings import worker

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
    

def get_scope_locked_file(file) -> Path:
    return Path(worker.TEMPDIR, file)

def check_scope_locked(file) -> None:
    file = get_scope_locked_file(file)
    if not file.exists():
        return 
    raise MicroscopeBusyError(file, file.read_text())

def remove_scope_lock_file(file) -> None:
    file = get_scope_locked_file(file)
    if not file.exists():
        raise FileNotFoundError(f'Lock file {file} not found.')   
    file.unlink()
    

def write_session_lock(session_id:str, lockFile:Path) -> None:

    with open(get_scope_locked_file(lockFile), 'w') as f:
        f.write(session_id)

def check_stop_file(stop_file:Path) -> None:
    if not stop_file.exists():
        return
    stop_file.unlink()
    raise KeyboardInterrupt(f'Stop file {stop_file} found.')