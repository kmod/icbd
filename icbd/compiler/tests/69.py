"""
instance equality
"""

class C(object):
    def __init__(self, x):
        self.x = x

c1 = C(1)
c2 = C(1)
c3 = C(2)
print c1 == c2
print c2 == c3
print

class D(object):
    def __init__(self, x):
        self.x = x

    def __eq__(self, rhs):
        return self.x == rhs.x

d1 = D(1)
d2 = D(1)
d3 = D(2)
print d1 == d2
print d2 == d3
print

class E(object):
    def __init__(self, eq):
        self.__eq__ = eq

e1 = E(lambda rhs: True)
e2 = E(lambda rhs: False)
print e1 == e2
print e2 == e1

