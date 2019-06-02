from yilanyilmaz.matcher import match
from yilanyilmaz.obtain import Sources


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
