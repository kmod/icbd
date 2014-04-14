"""
Dispatching based on type, using a dict mapping from the class -> function

The compiler itself does this
"""

class C(object):
    def __init__(self, x):
        self.x = x

class D(object):
    def __init__(self, y):
        self.y = y

def fc(c):
    assert isinstance(c, C)
    print "c:", c.x

def fd(d):
    assert isinstance(d, D)
    print "d:", d.y

def main():
    mapper = {
            C: fc,
            D: fd,
            }

    mapper[C](C(2))
    mapper[D](D(3))

    t = type(C(2))
    print t

    def map(o):
        print type(o), o.__class__
        mapper[type(o)](o)

    map(C(2))
    map(D(3))

    # print type(1).__class__

main()

t = set()
t.add(1)
print t
d = {1:2}
print type(t)
print type(d)
print C(2)
