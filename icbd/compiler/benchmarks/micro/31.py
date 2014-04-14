x = 65

def f(n):
    t = 0
    for i in xrange(n):
        t = t / 2 + x + i
    return t

for i in xrange(9):
    x += 1
    print f(10**i)

