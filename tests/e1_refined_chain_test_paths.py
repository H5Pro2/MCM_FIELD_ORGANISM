from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory


PROJECT_UPSTREAM = Path("reports/e1_frozen_state_transfer_s1dn_once_v1.json")


@contextmanager
def unused_refined_chain_paths():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        upstream = root / PROJECT_UPSTREAM.name
        shutil.copyfile(PROJECT_UPSTREAM, upstream)
        yield root, upstream


def make_unused_refined_chain_paths():
    temporary = TemporaryDirectory()
    root = Path(temporary.name)
    upstream = root / PROJECT_UPSTREAM.name
    shutil.copyfile(PROJECT_UPSTREAM, upstream)
    return temporary, root, upstream
