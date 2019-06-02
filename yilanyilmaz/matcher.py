from yilanyilmaz.meta import packages
from yilanyilmaz.obtain import Sources, obtain


def match(match_type, repo):
    source = obtain(match_type, repo)
    source.pkgs = packages(source.dir)
    return source
