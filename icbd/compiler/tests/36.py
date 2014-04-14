"""
classes
"""

class C1(object):
    def foo(self, x):
        return x

c1 = C1()
print c1.foo(1)
print C1.foo(c1, 2)

class C2(object):
    pass

c2 = C2()
c2.x = 1
print c2.x

class Counter(object):
    def __init__(self, start):
        self.x = start

    def inc(self):
        self.x = self.x + 1

    def __str__(self):
        return "<Counter: " + str(self.x) + ">"

c3 = Counter(5)

for i in xrange(100):
    c3.inc()
    print c3
