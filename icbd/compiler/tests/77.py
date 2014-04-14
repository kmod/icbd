"""
Callable merging of different arities
"""

# These two should correctly get merged into a callable that can take defaults
if 1:
    def f4(x, y=0, z=1):
        print x, y, z
else:
    def f4(x, y, z=2, w=3):
        print x, y, z, w

f4(5, 6)
f4(5, 6, 7)

