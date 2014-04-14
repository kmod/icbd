# Harder version of 80.py, since it mixes class-level methods and instance attributes

class A(object):
    def f(self):
        print "this is an A"

class B(object):
    def __init__(self):
        def f():
            print "this is a B"
        self.f = f

def call_f(o):
    o.f()

call_f(A())
call_f(B())
if "true":
    o = A()
else:
    o = B()
call_f(o)
