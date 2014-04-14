"""
subclassing
"""

class A(object):
    def __init__(self):
        self.x = 1

    def foo(self):
        print "A.foo()"
        print self.x

class B(A):
    def foo(self):
        print "B.foo()"
        print self.x

class C(B):
    def __init__(self):
        self.x = 5

def f(o):
    o.foo()
    print o.x
    print isinstance(o, A)
    print isinstance(o, B)
    print isinstance(o, C)

a = A()
print a.x
a.foo()
f(a)

b = B()
b.foo()
b.x += 1
b.foo()

c = C()
c.foo()

class E(object):
    def __init__(self):
        self.x = 1

    def bar(self):
        print "E.bar()"
        self.x += 1
        print self.x

    def foo(self):
        print "E.foo()"
        print self.x

class F(E):
    def foo(self):
        print "F.foo()"
        print self.x

E().foo()
F().foo()
E().bar()
F().bar()
