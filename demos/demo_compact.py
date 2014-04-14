# Basic type analysis:
a = 2
b = '3'
d = {a:b}
c = ord(b[2].lower()[0])
print c


# Name errors:
c *= e

# Nested-type manipulation:
d = {1:[1], 3:[4]}
d[1].append(2)

l = [range(i) for i in xrange(5)]
l.append([-1])
l2 = [k[0] for k in l]
l2.append(1)


# Argument-type checking, based on inferred types
l2.append('')



# Function type inference:
def f(x, y):
    return b * (x + y)
r = f(3, 4)



# Higher-level types:
def f(x):
    def g():
        return x
    return g

f1 = f(2)
print f(1)() + f1()




# Control-flow analysis:
if f1():
    x = 3
else:
    x = [0]
print l2[x]

def fib(x):
    if x <= 1:
        return x
    return fib(x-1) + fib(x-2)
fib(2)


def foo():
    return foo()
if 0:
    x = 0
else:
    x = foo()
print x


# Classes:
class Foo(object):
    def __init__(self, x):
        self.x = x
    def bar(self, z):
        return self.x * z
    def baz(self, k):
        return k**2

f = Foo(2)
f.baz(3)

# attributes
print f.x
z = f.bar(3)
f.y = 3
z = f.x * f.y
z *= f.z


# Complex type analysis:
def f1(x):
    def g(y):
        return x * y
    return g

a = f1('')
b = a(2)

def f2(x):
    def g(y):
        return x * y
    return g

a = f2(1)
b = a(2)

