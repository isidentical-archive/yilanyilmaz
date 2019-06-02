import pkgutil
from pathlib import Path


def packages(directory):
    packages = {}
    for module in pkgutil.iter_modules([directory.name]):
        if module.ispkg:
            packages[module.name] = (Path(directory.name) / module.name).glob("**/*.py")

    return packages
