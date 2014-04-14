"""
list of functions
"""

def f1(x):
    return x ** 1
def f2(x):
    return x ** 2
def f3(x):
    return x ** 3
def f4(x):
    return x ** 4
l = [f1, f2, f3, f4]
print l

l.append([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47].__getitem__)

for i in xrange(10):
    for j in xrange(len(l)):
        print l[j](i),
    print
