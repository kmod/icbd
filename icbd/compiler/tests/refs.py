"""
refcount example
"""

[].append(1)
len([])
print [1][0]

l = []
l = l
print len(l)

# Test to run: have a single variable get copied, and have one copy need to be raised and the other not
def f1(x):
    return x * 2
def f2(x):
    return x ** 2

f = f1
if 5 % 2:
    f = f2
print f(5)
print f1(5)
print f2(5)
