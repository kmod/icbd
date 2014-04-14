"""
Testing that div+mod behavior matches python's
"""

t1 = 0
t2 = 0
t3 = 0
t4 = 0
for i in xrange(-10, 10):
    t1 = t1 + i * (i / 4)
    t2 = t2 + i * (i / -4)
    t3 = t3 + i * (i % 4)
    t4 = t4 + i * (i % -4)
    print t1, t2, t3, t4

    print divmod(i, 5), divmod(i, -5)
# expected:
# 175 -165 -30 10
print t1, t2, t3, t4
