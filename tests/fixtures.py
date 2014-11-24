'''
py.test fixtures from pyscaffold
licenses under new BSD
copyright Blue Yonder

Created on Mon Nov 24 17:28:06 2014
'''

import pytest
import os
import stat
import tempfile
from shutil import rmtree


def set_writeable(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


@pytest.yield_fixture()
def tempdir():
    old_path = os.getcwd()
    new_path = tempfile.mkdtemp()
    os.chdir(new_path)
    yield
    os.chdir(old_path)
    rmtree(new_path, onerror=set_writeable)
