"""
isinstance and downcasting
"""

class A(object):
    def a(self):
        print "this is an A"

class B(object):
    def b(self):
        print "this is a B"

def thefunc(o):
    print isinstance(o, A)
    print isinstance(o, B)
    # This doesn't work right now since cpython treats bool as a subclass of int:
    # print isinstance(o, int)
    print isinstance(o, float)
    print isinstance(o, str)
    if isinstance(o, A):
        o.a()
    elif isinstance(o, B):
        o.b()
    elif isinstance(o, float):
        print "this is a float!", o
    elif isinstance(o, str):
        print "this is a string!", o
    elif isinstance(o, bool):
        print "This is a bool!", o
    elif isinstance(o, int):
        print "this is an int!", o
    else:
        print "this is something else??"

print isinstance(A(), A)
print isinstance(B(), A)
print isinstance(A(), B)
print isinstance(B(), B)
thefunc(A())
thefunc(B())
thefunc(1)
thefunc(1.0)
thefunc("aoeu")
thefunc(True)
thefunc(())
thefunc([2])
thefunc({1:"hello"})
thefunc(set([1]))
if "true":
    o = A()
else:
    o = B()
thefunc(o)
