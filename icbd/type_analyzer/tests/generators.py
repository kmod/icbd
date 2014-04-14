def f():
    for i in xrange(2):
        yield 2

def g():
    for i in xrange(2):
        yield

l = f() # 0 generator of int
l2 = list(l) # 0 [int]

l = g() # 0 generator of None
l2 = list(l) # 0 [None]

l3 = (1 for i in xrange(2)) # 0 generator of int

def h():
    res = 5
    while True:
        res -= 1
        if not res:
            return
        yield res

l = list(h()) # 0 [int]

class C(object):
    def bar(self, x):
        for i in xrange(x):
            yield i

c = C()
c.bar
