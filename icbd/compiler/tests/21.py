"""
returning functions
"""

def f():
    def g(x):
        return x ** 2
    return g

def f2():
    return [2, 3, 5, 7, 11, 13].__getitem__

for i in xrange(5):
    if i % 2 == 0:
        h = f2()
    else:
        h = f()
    print i, h(i)

