"""
IM inlining test
"""


l = []
l2 = []
if 5 % 2:
    a = l.append
else:
    a = l2.append

a(1)
print len(l), len(l2)



