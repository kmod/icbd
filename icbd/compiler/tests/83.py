""" Regression test: make sure that grabbing the instancemethod off of a boxed object keeps the underlying alive """

class A(object):
    def f(self):
        print "this is an A"

class B(object):
    def f(self):
        print "this is a B"


if "true":
    o = A()
else:
    o = B()

f = o.f
o = None
print [1]
f()


""" While we're add it, test putting them in closures as well """

def c(o):
    def g():
        return o.f()
    return g

if "true":
    g = c(A())
else:
    g = c(B())

print g()
