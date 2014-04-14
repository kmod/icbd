"""
conditional expressions
"""

def f():
    print "f"
    return True

def g():
    print "g"
    return False

def h():
    print "h"
    return False

print 1
# f
b1 = f() or g()
print 2
# f g
b2 = f() and g()
print 3
# g f
b3 = g() or f()
print 4
# g
b4 = g() and f()
print 5
# True False True Fals
print b1, b2, b3, b4

print g() or g() or g()
print f() and f() and f()

print g() or f() and h()
print (g() or f()) and h()
print g() and f() or h()
print g() and (f() or h())
print f() and (g() or not (h() and g()))

if "":
    x = True and False
else:
    x = True or False

print x

b = False
for i in xrange(5):
    b = b or (i == 3)
    print i, b

l = []
print l if 2 else []
print (True or True) if (True or True) else (True and True)

print g() or f() or g()
print g() or f() or f()
print f() and g() and f()
print f() and g() and g()
