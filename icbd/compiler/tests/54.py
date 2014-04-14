"""
Closure refcounting
"""

def f():
    l

l = []
f()
l = []

def f2():
    def inner():
        return len(s) + len(t)

    s = ''
    t = ()
    x = inner()
    s = ''
    t = ()
f2()

def f3():
    return x
if not "true":
    x = 1
    c = f3
else:
    c = lambda: 2
print c()
x = 2
print f3()

def f4():
    return x
if "true":
    x = 1
    c = f3
else:
    c = lambda: 2
print c()
x = 2
print f4()

def f5(x):
    def g():
        return x
    return g
print f5(5)()
