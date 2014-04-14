"""
List test
"""

l = []
for i in xrange(100000):
    # print i
    l.append(i)
print "successfully added", len(l), "elements"

l = []
for i in xrange(8):
    l.append(i * i)

for i in xrange(len(l)):
    print i, l[i]

print "testing more complicated list behavior"
def sort(l):
    n = len(l)
    rtn = []
    for i in xrange(n):
        rtn.append(l[i])

    for i in xrange(n):
        for j in xrange(i+1, n):
            if rtn[i] > rtn[j]:
                t = rtn[i]
                rtn[i] = rtn[j]
                rtn[j] = t
    return rtn
def sum(l):
    t = 0
    for i in xrange(len(l)):
        t = t + l[i]
    return t
l2 = [1, 5, 3, 9, 7, 8]
for i in xrange(10):
    l2.append((l2[-1] * 37 + l2[-2]) % 41)
l3 = sort(l2)
import sys
sys.stdout.write("initial: ")
for i in xrange(len(l2)):
    sys.stdout.write('%s ' % l2[i])
print
sys.stdout.write("sorted:  ")
for i in xrange(len(l3)):
    sys.stdout.write('%s ' % l3[i])
print
print "eq:", sum(l2) == sum(l3)

print "testing mul and extend"
l4 = [0]
l5 = l4 * 10
print l4, l5, len(l5)

l4 = [0]
l5 = [1]
l4.extend(l5)
print l4, l5

l4 = l5 = l6 = [1]
l6 = l6 + [3]
l5 += [2]
# This should print [1, 2] [1, 2] [1, 3]
print l4, l5, l6

print range(6) == range(5)
print range(5) == range(5)
print range(5) == range(5)[::-1]
if 1:
    l7 = None
else:
    l7 = [5]
print [1] == l7
print l7 == [2]

print "testing negative indices"
for i in xrange(-8, 8):
    print i, l[i]


for i in xrange(8):
    print i in range(6)
