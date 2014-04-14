"""
instancemethod raising test
"""

l = []
l2 = []
if 5 % 2:
    a = l.append
else:
    a = l2.append

a(1)
print len(l), len(l2)


l = []
l2 = []
for i in xrange(20000000):
    if i % 2:
        a = l.append
    else:
        a = l2.append
    a(i)

print len(l), len(l2)

if 5 % 2:
    f = l.__getitem__
else:
    f = l2.__getitem__
print f(0)

l = []
append = l.append
for i in xrange(5):
    append(2)

