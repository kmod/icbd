"""
doubles
"""

d = 1.0
print d
print d + 2.5

print 234512345.6789012345
print 1e12
print 123456789012.0
print 1e11
print 0.00012345678901234567
print 0.0001

print 1.1 + 5
print 3 + 1.1

d = 1.2
for i in xrange(5):
    d += 2.31
    print d, d>10

print 1 / .5
print 2 / 2.3

if 2.5:
    print "yes"
else:
    print 1.0/0.0

t = 1.0
for i in xrange(20):
    print float(i), 1.0 / i
    print repr(1.0 + t), repr(t)
    t /= 10
