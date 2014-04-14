"""
Triggers some weird bug
"""

l = [12345]
l2 = [54321]
if 5 % 2:
    f = l.__getitem__
else:
    f = l2.__getitem__
print f(0)
