import os
import shutil
import tempfile
from contextlib import contextmanager
from app.core.logging_config import logger

@contextmanager
def create_temp_workspace():
    """
    Creates an isolated temporary directory for code execution and ensures
    it is deleted upon exiting the context block, even if exceptions occur.
    """
    temp_dir = tempfile.mkdtemp(prefix="code_exec_")
    try:
        yield temp_dir
    finally:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.error(f"Failed to clean up temp workspace {temp_dir}: {e}")
