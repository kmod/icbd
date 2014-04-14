def listify(f): # 4 ((int) -> int) -> (int) -> [int] # 12 (int) -> int
    return lambda x: [f(x)]

@listify # 1 ((int) -> int) -> (int) -> [int]
def g(x): # 4 (int) -> int
    return x ** 2

x = g(3) # 0 [int] # 4 (int) -> [int]



def d(f):
    def inner(x):
        return f(x, x)
    return inner

def g(x, y):
    return x + y

x = d(g)(2) # 0 int

@d
def h(x, y): # 4 (int,int) -> int
    return x + y
y = h(3) # 0 int # 4 (int) -> int

class C(object):
    @staticmethod
    def bar(x):
        return x

y = C.bar(2) # 0 int
c = C()
z = c.bar(3) # 0 int

def f3():
    def d1(x):
        def inner1(f):
            def inner2():
                return f(x)
            return inner2
        return inner1

    def d2(f):
        def inner3(x):
            return f(x, x)
        return inner3

    @d1(3)
    @d2
    def g(x, y):
        return x * y

    x = g() # 4 int

def f4():
    class C(object):
        @property
        def bar(self): # 12 (C) -> int
            return self.x

    c = C()
    y = c.bar # 4 int
    c.x = 2

def f5():
    class C(object):
        @classmethod
        def bar(cls, x): # 12 (class 'C',int) -> int
            return x

    c = C()
    x = C.bar(2) # 4 int
    y = c.bar(3) # 4 int
