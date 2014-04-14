"""
function test
"""

def f(x):
    return x ** x

def g():
    def h():
        return 2
    return h

print 2
for i in xrange(15):
    # print i, f(i)
    if i > 0:
        if f(i-1) != 0:
            print i, f(i) * 100 / f(i-1) / i

print g()()

# cPython 2.6: 15.05s
# pypy 1.8: 2.59s
# icbd: 0.24s
# icbd -O3: 0.12s
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

print fib(24)

total = 0
def f2(x):
    return 12345 % x
for i in xrange(1, 100000):
    total = total + f2(i)
print total
