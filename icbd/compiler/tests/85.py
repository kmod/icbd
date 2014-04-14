"""
Similar to 76.py, but subclassing a builtin type
"""

class I(int):
    def __add__(self, rhs):
        return 54321

    def __radd__(self, lhs):
        return 12345

print 1 + I()
print I() + 1

