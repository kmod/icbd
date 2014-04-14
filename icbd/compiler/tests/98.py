"""
__call__
"""

class C(object):
    def __init__(self, x):
        self.x = x

    def __call__(self, y):
        return self.x + y

c = C(5)
print c(2)
