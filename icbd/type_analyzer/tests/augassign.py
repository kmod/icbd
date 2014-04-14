class C(object):
    def __iadd__(self, rhs):
        return rhs

class D(object):
    def __add__(self, rhs):
        return rhs

c = C() # 0 C
d = D() # 0 D
c += 1
c # 0 int
d += 1
d # 0 int
