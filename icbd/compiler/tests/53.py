"""
complex default args
"""

x = 1
def f(x=x):
    return x
x = 2

assert f() == 1

l = []
def g(x=l):
    return x
assert len(g()) == 0
l.append(1)
assert len(g()) == 1
g().append(2)
assert len(l) == 2

# these have to get raised
def h(s="hello world", f=f):
    f(2)
    return s
print len(h())

def b(y=1):
    pass

def a():
    b()

def k(s=None):
    return s
print k('')

def f2(x, l=[]):
    l.append(x)
    print l
f2(1, [])
f2(2, [])
f2(3, [])
f2(1)
f2(2)
f2(3)

x3 = 1
def f3():
    x3 = 2
    def g3(y=x3):
        global x3
        print x3, y
    g3()
f3()

# copies from 34.py:
# closures for default args
x17 = 0
y17 = 10
def f17(x17, y17):
    def h():
        global x17
        def g(_x=x17, _y=y17):
            print _x, _y
        return g
    return h()

g17 = f17(1, 11)
g17()
g17(2, 12)
g17(3)
x17, y17 = 100, 110
g17()

def f18(g):
    print g(2)
    print g(3, 4)
    print g(5, 6, 7)

def g18(x, y=3, z=4):
    print x, y, z
    return x + y + z

f18(g18)

def f19(x):
    def g(y, z=0):
        return x + y + z
    return g

g19 = f19(5)
print g19(2), g19(5)
print g19(0, 100)

c20 = 5
def f20(x=c20):
    return x

print f20()
print f20(6)
c20 = 0
print f20()

def g20():
    return f20()
print g20()

def f21(l=[]):
    l.append(1)
    print l

def m21(f):
    return f
_f21 = m21(f21)
_f21()
_f21()
_f21()

def f22(x=0, s=None):
    print x, s

def g22():
    f22()
g22()

l23 = []
l23_2 = []
def f23(x, l=l23):
    l.append(x)
for i in xrange(10):
    if i % 2 == 0:
        f23(i)
    else:
        f23(i, l23_2)
print l23, l23_2

# Roughly the same as f21 but inside another function, so it has to come from a closure
def f24():
    l = []
    def g(l=l):
        l.append(1)
        print l

    def h(n):
        for i in xrange(n):
            g()
    h(3)
f24()

def f25(name, s="Hello"):
    print s, name
def g25():
    f25("world")
    f25("everyone", "hi")
f25("world")
f25("everyone", "hi")
g25()

def g26(x):
    return x
def f26(f=g26):
    print f(12345)
def h26():
    f26()
    f26(lambda x: x**2)
f26()
f26(lambda x: x**2)
h26()

def f27(l=[None]):
    print l
def g27():
    f27()
    f27(["hello"])
g27()

# Same as 25 except now with an additional default arg which will force it to be instantiated
def f28(name, s="Hello", l=[]):
    print s, name
def g28():
    f28("world")
    f28("everyone", "hi")
f28("world")
f28("everyone", "hi")
g28()

# testing having both defaults and a closure:
def f29():
    l = [1, 2, 3]
    x = 5
    def f(y=5):
        l.append(y)
        print x, y, l

    def mk(f):
        return f
    mk(f)()
    mk(f)(2)
f29()

def f30(l=[]):
    print l
f30()
