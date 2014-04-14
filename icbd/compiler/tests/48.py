"""
tuple test
"""

def main():
    t = 1, 2, "hi", []
    print t[2]
    a, b, c, l = t
    print "%d" % (a+b) + c
    t = 1

    def f(t):
        return t[0] + t[1]
    print f((2, 3))

    def g(x, y):
        return (x, y)
    print g(1, 2)

    print ([], "aoeu")

    print "%d, %d" % (1, 2)
    a, b = g(1, 2)
    print a, b

    # def f2((a, b)):
        # return a * b
    # print f2((2, 3))

    t = ([], 1, 2)
    t[0].append(2)
    print len(t[0])

    def h(t):
        print t
        return

    h(t)

    class C(object):
        def __init__(self, x):
            self.l = [0]
            self.x = x

        def foo(self):
            return self.x

        def bar(self, y):
            return self.x * y

    class D(object):
        def foo(self):
            return 5

        def bar(self, y):
            print "D.bar"
            return y


    def p(o):
        print o[1](o[0]())

    c = C(37)
    d = D()
    p((c.foo, c.bar))
    p((d.foo, d.bar))

    # Testing some pathological cases:
    print ()
    # These two could naively be called the same type, tuple_tuple_i64
    print ((), 1)
    print ((1,),)

    for i in xrange(10):
        print (4, (), "hello") == (i, (), "hello")

    if 1:
        t3 = None
    else:
        t3 = ()
    print t3 == ()
    print () == t3

    if 1:
        t4 = None
    else:
        t4 = (1,)
    print t4 == (2,)

    for i in xrange(5):
        for j in xrange(5):
            print i, j, (i,j) < (2,3)

main()
