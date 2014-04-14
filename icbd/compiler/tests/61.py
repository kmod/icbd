"""
None handling
"""

if 1:
    t = (None, None, None, None)
else:
    t = ((), '', [''], {'':1})
def f(x):
    print len(x)
f(t)
