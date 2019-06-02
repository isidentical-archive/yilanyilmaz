import ast
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Tuple

import astpretty


@contextmanager
def restart(obj, attr):
    original = getattr(obj, attr)
    try:
        setattr(obj, attr, original)
        yield
    finally:
        setattr(obj, attr, original)


class PatternVisitor(ast.NodeVisitor):
    patterns = {}

    def __init_subclass__(cls):
        cls.__bases__[0].patterns[cls.__doc__] = cls()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._seen_patterns = defaultdict(int)

    def visit(self, tree):
        with restart(self, "_seen_patterns"):
            super().visit(tree)
            return self._seen_patterns

    def dispatch(self, tree):
        for _, pattern in self.patterns.items():
            seen_patterns = pattern.visit(tree)
            print(seen_patterns)

    def check_name(self, node, name):
        if "." in name:
            name, *attrs = name.split(".")
            for attr in attrs:
                if not (isinstance(node, ast.Attribute) and node.attr == attr):
                    return False
                node = node.value

        return isinstance(node, ast.Name) and node.id == name

    def obtain_args(self, args):
        for arg in args:
            if isinstance(arg, ast.Constant):
                yield arg.value
            elif isinstance(arg, ast.Name):
                yield arg.id
            elif isinstance(arg, ast.Attribute):
                arg_repr = []
                while isinstance(arg, ast.Attribute):
                    arg_repr.append(arg.attr)
                    arg = arg.value
                arg_repr.extend(self.obtain_args([arg]))
                yield ".".join(reversed(arg_repr))
            elif isinstance(arg, ast.Call):
                func = next(self.obtain_args([arg.func]))
                args = map(str, self.obtain_args(arg.args))
                yield f"{func}({', '.join(args)})"


class NamedTupleUsage(PatternVisitor):
    """Check Named Tuple similarity"""

    @dataclass(unsafe_hash=True)
    class NamedTuple:
        name: str
        fields: Tuple[str, ...]

    def visit_Call(self, node):
        if not (
            self.check_name(node.func, "namedtuple")
            or self.check_name(node.func, "collections.namedtuple")
        ):
            return self.generic_visit(node)

        name, *fields = tuple(self.obtain_args(node.args))
        pattern = self.NamedTuple(name, tuple(fields))
        self._seen_patterns[pattern] += 1


if __name__ == "__main__":
    t = PatternVisitor()
    t.dispatch(ast.parse("a = namedtuple('x', y, 32, y.x.ad, f(y.x, 12, 'ayz'))"))
