"""
More fun with boxing
"""

def f1():
    """ Putting boxed objects in containers """
    d = {}
    d[0] = 1
    d[1] = "foo"
    print d

def f2():
    """ re-boxing a boxed object """
    def box1(o):
        return o

    def box2(o):
        return o

    print box1("hello")
    print box2(0)

    o = [1]
    o = box1(o)
    o = box2(o)
    print o
f2()
