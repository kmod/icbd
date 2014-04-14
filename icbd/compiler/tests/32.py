"""
actual closure test
"""

def f(x):
    def g(y):
        return x + y
    return g

f2 = f(5)
print f2(1), f2(5)

def twice(f):
    def inner(x):
        return f(f(x))
    return inner

# f3 = twice(lambda x: x**2)
f3 = twice(f2)
print f3(5), f3(10)

def t1(x):
    def t2():
        def t3():
            return x
        return t3()
    return t2()

print t1(1)

def r1(x):
    def r2(y):
        def r3(z):
            return x + y + z
        return r3
    return r2

def r4(x, y):
    return r1(x)(y)

print r1(1)(2)(3)
print r1(5)(6)(7)
print r4(1,5)(6)

def k1():
    x = 1
    def k2():
        def k3():
            return 0
        def k4():
            return k3()
        return x + k4()
    return k2()

def i1():
    """This tests that a single closure object can be passed by object and by type"""
    def i2():
        pass
    x = 1

    def i3():
        i2()
    def i4():
        x
    i3()
    i4()

def j1():
    """This tests to make sure that static resolution doesn't happen before non-static, and that it climbs correctly."""
    def j2():
        pass

    def j3():
        j2()

    def j4():
        j2 = 1
        def j5():
            return 1 + j2
