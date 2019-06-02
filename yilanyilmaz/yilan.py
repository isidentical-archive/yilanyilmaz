import ast
import inspect
import tokenize
from contextlib import contextmanager, suppress
from difflib import SequenceMatcher
from enum import IntEnum
from functools import wraps
from itertools import chain
from pprint import pprint

from yilanyilmaz.handlers import PatternVisitor
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
    def __init__(self, code_generator, missing_files, *pkgs):
        self.rate = 100
        self.code_generator = code_generator
        self.missing_files = missing_files
        self.pkgs = pkgs

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

            dump1 = ast.dump(tree1)
            dump2 = ast.dump(tree2)

            if dump1 == dump2:
                continue

            coper = zip(self.pkgs[0].pkgs.keys(), self.pkgs[1].pkgs.keys())
            for original, copy in coper:
                dump2 = dump2.replace(copy, original)

            _internal_rate -= 1 - SequenceMatcher(None, dump1, dump2).ratio()

            pp = PatternVisitor()
            patterns1 = pp.dispatch(tree1)
            patterns2 = pp.dispatch(tree2)
            ratio = pp.compare(patterns1, patterns2)
            _internal_rate += ratio

        return _internal_rate


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
        return Result(zipped_modules, missings, pkg1, pkg2)

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
