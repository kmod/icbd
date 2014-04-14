"""
lists of lists
"""

def r(n1, n2):
    l = []
    for i in xrange(n1, n2):
        l.append(i)
    return l

l2 = []
for i in xrange(5):
    l2.append(r(i, i + 5))
print len(l2)

l2[1] = l2[0]
l2[3] = l2[2]
l2[4] = l2[1]
l2[0] = l2[3]
[l2, l2].append([[1]])

print "done"
