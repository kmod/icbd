"""
lists of boxed objects
"""

l = []
l.append(1)
l.append("")
print l

l2 = [l]
print l2

t = (l, l2)
t2 = (t, t)
print t2
