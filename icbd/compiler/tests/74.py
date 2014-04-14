"""
str->repr with inheritance
"""

class A(object):
    def __str__(self):
        return "A"

class B(A):
    def __repr__(self):
        return "B"

# Should print "A B"
print B(), repr(B())
