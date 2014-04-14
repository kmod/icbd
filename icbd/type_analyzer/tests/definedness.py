def b1():
    (1 for a in [a]) # e 17
def g2():
    (1 for a in [1])
    (1 for a in [1] if a)
    (a for a in [1])
    (1 for a in [1] for b in [[a]]) # 11 int # 31 int # 24 [int]
def b3():
    (1 for a in [b] for b in [1]) # e 17
def b4():
    a = a # e 8
def b5():
    a, a.b = 1 # e 7
# punting on this for now... too hard
def b6():
    (1 for a in [])
    print a # e 10
def g7():
    with open("/dev/null") as f:
        print f
    print f
def b8():
    with open(f8) as f8: # e 14
        pass
# getting these two right is also very hard
def b9():
    def inner():
        return x9 # e 16
    inner()
    x9 = 1
def g10():
    def inner():
        return x10
    x10 = 1
    inner()

global11 = 0
def g11():
    def i1():
        def i2():
            def i3():
                return x + y + z + global11
            z = y + x
            return i3()
        y = x + global11
        return i2()
    x = 3
    return i1()

def g12():
    l = [0,0,0,0]
    a = l[a] = 1

def b13():
    l = [0,0,0,0]
    l[a] = a = 1 # e 6

def g14():
    def f():
        pass
    if 1:
        b = 2
        def f():
            return b
        f()

def g15():
    f = lambda x:x
    return f

def b16():
    x = 1
    if 1:
        del x
    else:
        del x
    return x # e 11

def g17():
    if 0:
        return 0
    x = 0
    def f():
        return x
    return f()

def g18():
    class C(object):
        def foo(self):
            return C()

