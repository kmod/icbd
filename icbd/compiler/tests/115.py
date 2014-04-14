def iadd(x, y):
    print x, y
    return x + y
print reduce(iadd, range(5), 0)

def fadd(x, y):
    return x + y
fadd(1.0, 1.0)
x = reduce(fadd, range(5), 0)
