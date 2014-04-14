"""
These magic methods only get resolved if set on the class:
"""

class C(object):
    def __init__(self, f):
        self.__str__ = f
        self.__repr__ = f
        # TODO __lt__, etc

c1 = C(lambda: "test")
print str(c1) == c1.__str__()
print repr(1) == c1.__repr__()
print

class D(object):
    def __init__(self, f):
        self._f = f

    def __repr__(self):
        return self._f()

d1 = D(lambda: "test")
print str(d1) == d1.__str__()
print repr(1) == d1.__repr__()
print

"""
class E(object):
    pass

E.__repr__ = lambda self: "set"
print E()
"""

class F(object):
    def __sub__(self, rhs):
        return 2

f = F()
# TODO the type analyzer doesnt get this right
# hax to make it work:
print F.__sub__(f, f)
f.__nonzero__ = lambda: 0
f.__sub__ = lambda rhs: 1
print bool(f)
print f - f

