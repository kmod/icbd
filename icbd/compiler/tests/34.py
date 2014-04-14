"""
closure tests
"""

def f1(x):
    def g1():
        return 2
    def g2():
        y = 2
        def f1_2():
            return y + x + g1()
        return f1_2()
    return g2
print f1(1)()

def f3(x):
    if 1:
        return x
    return g3(x)

def g3(x):
    return f3(x)

print f3(2)

y = 1
def f4(x):
    return g4(x-h4(x))

def g4(x):
    if 1:
        return x
    return f4(x-1)

if 1:
    def h4(x):
        return x
else:
    def h4(x):
        return -x
h4(1)
f4(2)

def f5(x):
    return x + 1

def g5(x):
    def h5():
        return f5(x)
    return h5
g5(2)

def f6(x):
    def g6(y):
        if 0:
            g6(y-1)
        return x+y
    return g6

print f6(1)(2)

def f7():
    x = 1
    def g7():
        return x
    def h7():
        return g7()
    return h7
f7()()

def f8():
    def g8():
        pass
    def h8():
        g8()

    if 1:
        g8()

# It's ok for something to be both in the closure and the local scope
def f9():
    a = 1
    b = 2
    def g9():
        a

    def h9():
        a = 1
        a
        b

x12 = 2
def f12():
    x12 = 3
    def g12():
        # Tricky: this should bypass the above 'x12=3' definition and go to the global scope
        global x12
        def h12():
            # Even trickier: this one should also go up to globals
            print "h2", x12
        h12()
        return x12
    print g12()
f12()

# Same as above but without accessing the global var in the middle scope
# This should force x14 to be part of the global closure
x14 = 1
def f14():
    x14 = 2
    def g14():
        global x14
        def h14():
            print x14
        h14()
    g14()
f14()

# Super super tricky: jumps over the closure definition, up to the globals
x15 = 11
def f15():
    x15 = 12
    def g15():
        def h15():
            global x15
            def foo15():
                print x15
            foo15()
        h15()
        print x15
    g15()
f15()
print x15

# And just to make sure, this one should hit the local closure
x16 = 21
def f16():
    x16 = 22
    def g16():
        print x16
    g16()
f16()

# closures for default args
x17 = 0
y17 = 10
def f17(x17, y17):
    def h():
        global x17
        def g(_x=x17, _y=y17):
            print _x, _y
        return g
    return h()

g17 = f17(1, 11)
g17()
g17(2, 12)
g17(3)
x17, y17 = 100, 110
g17()
