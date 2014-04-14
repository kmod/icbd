"""
Augassign tests
"""

class C(object):
    pass

c = C()
c.total = 0

l = range(10)
for i in xrange(len(l)-1):
    l[i+1] += l[i]
    c.total += i

print l
print c.total
