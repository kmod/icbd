"""
function raising test
"""

def f_even(x):
    # print x, "is even"
    return x

def f_odd(x):
    # print x, "is odd"
    return 0

t = 0
for i in xrange(100000):
    if i % 2 == 0:
        f = f_even
    else:
        f = f_odd
    t += f(i)
print t
