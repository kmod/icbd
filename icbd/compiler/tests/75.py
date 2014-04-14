"""
enumerate
"""

l = [5 - i for i in xrange(6)]
print l
print enumerate(l)
for i, x in enumerate(l):
    print i, x, i * x
print enumerate(["hello", "world"])
