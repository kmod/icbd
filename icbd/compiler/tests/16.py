"""
function-passing test
"""

def map(f, l):
    r = []
    for i in xrange(len(l)):
        r.append(f(l[i]))
    return r

def g(x):
    print x
    return x ** x

l = map(g, [0, 1, 2, 3, 4, 5])
l2 = map(l.__getitem__, [0, 2, 4, 1, 3, 5])
for i in xrange(len(l2)):
    print l2[i]
