"""
Some misc class testing
"""

class C(object):
    pass
c = C()

class D(object):
    def __init__(self, x):
        self.x = x
d = D(1)
print d.x

class E(object):
    pass

def set_e():
    def e(self):
        print "in e()"
    E.e = e
set_e()
E().e()
