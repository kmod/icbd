"""
default arguments in class methods
"""

class O(object):
    def __init__(self, x):
        print "creating O", x

class C(object):
    def __init__(self, x=0):
        print x

    def test(self, o=O(2)):
        pass
if 0:
    C()
    C(1)
    c = C(2)
    c.test()
    c.test()

def f30(l=[]):
    print l
f30()
