import os
from enum import Enum
from typing import Sequence, Tuple

from yilanyilmaz.obtain import Sources


class Stage(Enum):
    ALPHA = "a"
    BETA = "b"
    FINAL = None


@dataclass
class Version:
    major: int
    minor: int
    bugfx: int
    stage: Stage = Stage.FINAL
    stver: int = None


@dataclass
class Metadata:
    name: str
    version: Version
    packages: Sequence[os.PathLike]

    @classmethod
    def from_source(cls, source):
        if source.type is Sources.GIT:
            cls._git(source.dir)
        elif source.type is Sources.PYPI:
            cls._pypi(source.dir)

    @classmethod
    def _git(cls, directory):
        pass

    @classmethod
    def _pypi(cls, directory):
        pass
