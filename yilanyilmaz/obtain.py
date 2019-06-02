import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path


class Sources(Enum):
    GIT = auto()
    PYPI = auto()


@dataclass
class Source:
    dir: tempfile.TemporaryDirectory
    type: Sources


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

    shutil.rmtree(src)


def _obtain_from_git(tempdir, repo):
    process = subprocess.run(["git", "clone", repo, tempdir.name])
    process.check_returncode()
    return tempdir


def _obtain_from_pypi(tempdir, repo):
    process = subprocess.run(["pip", "install", "--target", tempdir.name, repo])
    process.check_returncode()
    return tempdir


def obtain(source: Sources, repo: str) -> tempfile.TemporaryDirectory:
    tempdir = tempfile.TemporaryDirectory()
    if source is Sources.GIT:
        _obtain_from_git(tempdir, repo)
    elif source is Sources.PYPI:
        _obtain_from_pypi(tempdir, repo)
    else:
        return NotImplemented

    return Source(tempdir, source)
