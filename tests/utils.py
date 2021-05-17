from contextlib import contextmanager
import os
import shutil
import tempfile
import uuid


@contextmanager
def setup_tempdir(cleanup=True):
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        if cleanup:
            shutil.rmtree(temp_dir)


@contextmanager
def tmp_file(content, cleanup=True):
    with setup_tempdir(cleanup=cleanup) as dirpath:
        _, filepath = tempfile.mkstemp(suffix=".yaml", prefix=str(uuid.uuid4()), dir=dirpath)
        with open(filepath, "r+") as fd:
            fd.write(content)
        try:
            yield dirpath, filepath
        finally:
            if cleanup:
                os.remove(filepath)
