import ast
import inspect
import tokenize
from contextlib import suppress
from enum import IntEnum
from functools import wraps
from itertools import chain
from pprint import pprint

from yilanyilmaz.matcher import match
from yilanyilmaz.obtain import Sources


class Rates(IntEnum):
    MISSING_FILE = 1


def rate(meth):
    meth.rate_mark = True

    @wraps(meth)
    def wrapper(*args, **kwargs):
        self = args[0]
        result = meth(*args, **kwargs)
        self.rate += result
        return result

    return wrapper


class Result:
    def __init__(self, code_generator, missing_files):
        self.rate = 100
        self.code_generator = code_generator
        self.missing_files = missing_files

        for _, member in inspect.getmembers(self):
            if hasattr(member, "rate_mark"):
                member()

    @rate
    def missing_files(self):
        total_files_length = len(self.code_generator) + len(self.missing_files)
        return -(
            len(self.missing_files) * Rates.MISSING_FILE * (total_files_length / 100)
        )

    @rate
    def ast_comp(self):
        _internal_rate = 0
        for file1, file2 in self.code_generator:
            with tokenize.open(file1) as f:
                tree1 = ast.parse(f.read())
            with tokenize.open(file2) as f:
                tree2 = ast.parse(f.read())

            print(tree1)
            print(tree2)


class YilanYilmaz:
    def compare(self, pkg1, pkg2):
        pkg1, pkg1_type = pkg1
        pkg2, pkg2_type = pkg2

        pkg1_type = getattr(Sources, pkg1_type.upper())
        pkg2_type = getattr(Sources, pkg2_type.upper())

        pkg1 = match(pkg1_type, pkg1)
        pkg2 = match(pkg2_type, pkg2)

        pkg1._codes = chain.from_iterable(pkg1.pkgs.values())
        pkg2._codes = chain.from_iterable(pkg2.pkgs.values())

        zipped_modules, missings = self.module_zip_together(pkg1._codes, pkg2._codes)
        return Result(zipped_modules, missings)

    def module_zip_together(self, modules1, modules2):
        modules1_bases = {}
        modules2_bases = {}

        modules1_parts = set(
            map(
                lambda file: modules1_bases.__setitem__(
                    file.parts[-1], "/".join(file.parts[:-1])
                )
                or file.parts[-1],
                modules1,
            )
        )
        modules2_parts = set(
            map(
                lambda file: modules2_bases.__setitem__(
                    file.parts[-1], "/".join(file.parts[:-1])
                )
                or file.parts[-1],
                modules2,
            )
        )
        undefined_files = modules1_parts - modules2_parts
        return (
            [
                (f"{modules1_bases[file]}/{file}", f"{modules2_bases[file]}/{file}")
                for file in modules1_parts & modules2_parts
            ],
            undefined_files,
        )


if __name__ == "__main__":
    yy = YilanYilmaz()
    p1 = ("arkhe", "pypi")
    p2 = ("https://github.com/isidentical/Arkhe.git", "git")
    print(yy.compare(p1, p2).rate)
