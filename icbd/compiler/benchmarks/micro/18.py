t = 0
for i in xrange(100000000):
    if i % 2 == 0:
        def f_even(x):
            # print x, "is even"
            return x
        f = f_even
    else:
        def f_odd(x):
            # print x, "is odd"
            return 0
        f = f_odd

    t += f(i)
print t

