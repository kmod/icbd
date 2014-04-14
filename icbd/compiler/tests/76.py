"""
exception to binop rules: if one type is a subclass of the other, then __rop__ is tried first
http://docs.python.org/2/reference/datamodel.html#coercion-rules
"""

class A(object):
    def __add__(self, rhs):
        return 1

    def __radd__(self, rhs):
        return 2

    def __iadd__(self, rhs):
        return 3

class B(object):
    def __add__(self, rhs):
        return 4

    def __radd__(self, rhs):
        return 5

    def __iadd__(self, rhs):
        return 6

class C(A):
    def __add__(self, rhs):
        return 7

    def __radd__(self, rhs):
        return 8

    def __iadd__(self, rhs):
        return 9

a = A()
b = B()
c = C()

print a + a
print a + b
print a + c
print b + a
print b + b
print b + c
print c + a
print c + b
print c + c

a += c
print a
c += c
b += b

