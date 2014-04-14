"""
additional list functionality
"""

l = range(10)
print l.pop(5)
print l.pop(5)
print l.pop(5)
print l

l = range(5)
l.insert(2, -1)
l.insert(100, -2)
l.insert(-1, -3)
l.insert(-100, -4)
print l

l2 = []
while len(l2) < 1000:
    l2.insert(0, 5)
print len(l2)

l3 = []
l3.insert(0, "")
l3.pop(0)
s = "hello"
l3.insert(0, s)
l3.insert(0, s)
l3.insert(0, s)

l4 = range(5)
l4[::2] = range(3)
print l4
l4[:] = range(6)
print l4
l4[-3:] = [8,9]
print l4

l5 = ["i" for i in xrange(5)]
print l5
l5[:] = [""]
print l5
l5[:] = ["hello"]
print l5
l5[::-1] = ["world"]
print l5
l5[8:] = ["foo"]
print l5

class C(object):
    pass
l6 = [C()]
