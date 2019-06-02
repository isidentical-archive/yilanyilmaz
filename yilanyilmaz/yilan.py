import ast
import tokenize
from contextlib import suppress

from yilanyilmaz.matcher import match
from yilanyilmaz.obtain import Sources

class Code:
    """ Python AST representation of multiple modules """
    
    def __init__(self, *files):
        self.handled_files = {}
        for file in files:
            with suppress(Exception):
                with tokenize.open(file) as f:
                    ast_repr = ast.parse(f.read())
                
                self.handled_files[file] = ast_repr

class YilanYilmaz:
    def compare(self, pkg1, pkg2):
        pkg1, pkg1_type = pkg1
        pkg2, pkg2_type = pkg2

        pkg1_type = getattr(Sources, pkg1_type.upper())
        pkg2_type = getattr(Sources, pkg2_type.upper())

        pkg1 = match(pkg1_type, pkg1)
        pkg2 = match(pkg2_type, pkg2)

if __name__ == "__main__":
    yy = YilanYilmaz()
    p1 = ("arkhe", "pypi")
    p2 = ("https://github.com/isidentical/Arkhe.git", "git")
    yy.compare(p1, p2)
