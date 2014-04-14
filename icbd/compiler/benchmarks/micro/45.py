a, b = 1, 2
for i in xrange(123456789):
    a, b = b, a

print a, b

def f():
    return 1, 2

a, b = f()

x, [y, (z, w)] = 1, (2, [3, 4])
print x, y, z, w

