"""
chained comparisons
"""

class C(object):
    def __init__(self, x):
        self.x = x

    def __lt__(self, rhs):
        print self.x, rhs.x
        return self.x < rhs.x

    def __gt__(self, rhs):
        print "gt", self.x, rhs.x
        return self.x > rhs.x

print C(1) < C(2) < C(3)
print C(4) < C(2) < C(3)
print C(1) < C(2) > C(3)
print C(1) < C(4) < C(3)
print C(1) > C(4) < C(3)
print C(5) > C(4) < C(3)

