"""
Function arg unpacking
"""

def f((a, b), (c,)):
    return a + b + c

t1 = (1, 2)
t2 = (3,)
print f(t1, t2)
