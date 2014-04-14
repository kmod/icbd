"""
Testing class-only method resolution for special functions,
to match cPython's optimization
"""

class C(object):
    def __getitem__(self, sl):
        return 1

def gi(sl):
    return 2

c = C()
c.__getitem__ = gi
print c.__getitem__(1)
print c[1]

if 0:
    C.__getitem__(c, 1)
