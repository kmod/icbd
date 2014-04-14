"""
setting fields on boxed objects
"""

class A(object):
    pass
class B(object):
    pass

def f(o):
    o.x += 1
    o.l = [o.x]

a = A()
a.x = 1
a.l = [1]
f(a)
print a.x

b = B()
b.x = 100
b.l = [2]
f(b)
print b.x
