"""
List perf test
"""

def sort2(l):
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
def sum2(l):
    t = 0
    for i in xrange(len(l)):
        t = t + l[i]
    return t

# on my machine:
# cPython 2.6: 36.3s
# pypy 1.8: 1.06s
# icbd: 2.56s
# icbd -O3: 0.80s
# cpp: 0.28s
# icbd -O3, with no support for negative indices: 0.66s
# icbd -O3, with no array bounds checking: 0.54s
# icbd -O3, with no bounds checking or negative indices: 0.27s
print "perf test"
l4 = [1, 2]
while len(l4) < 1000:
    l4.append((l4[-1] * 127 + l4[-2]) % 253)
l5 = sort2(l4)
print sum2(l4), sum2(l5)

