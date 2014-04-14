"""
list sorting
"""

l = [1, 5, 8, 3, 2, 3, 5]
l.sort()
print l

class C(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, rhs):
        return self.x < rhs.x

    def __repr__(self):
        return "<C(%d, %d)>" % (self.x, self.y)

l2 = []
for i in xrange(1000):
    l2.append(C((i * 7) % 13, (i * 53) % 41))
print l2
l2.sort()
print l2
