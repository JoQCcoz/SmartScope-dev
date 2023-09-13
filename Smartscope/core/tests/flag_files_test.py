import pytest
from pathlib import Path
from ..flagfiles import write_session_lock, check_scope_locked, MicroscopeBusyError

def test_write_session_lock():
    lock_file_path = Path('/tmp/test.lock')
    contents = 'mysession'
    lock_file_path.unlink(missing_ok=True)
    write_session_lock(contents,lockFile=lock_file_path)
    assert lock_file_path.exists()
    assert lock_file_path.read_text() == contents
    lock_file_path.unlink()

def test_check_scope_locked():
    lock_file_path = Path('/tmp/test.lock')
    contents = 'mysession'
    lock_file_path.unlink(missing_ok=True)
    write_session_lock(contents,lockFile=lock_file_path)
    
    with pytest.raises(MicroscopeBusyError, match=contents):
        check_scope_locked(lock_file_path)
    
    lock_file_path.unlink()

    assert check_scope_locked(lock_file_path) is None

    
