def f(x):                   # 4 (int) -> (int) -> (int) -> int # 6 int
    def g(y):               # 8 (int) -> (int) -> int # 10 int
        def h(z):           # 12 (int) -> int # 14 int
            return x + y + z # 19 int # 23 int # 27 int
        return h
    return g

x = f(1) # 0 (int) -> (int) -> int
y = x(2) # 0 (int) -> int
z = y(3) # 0 int

class C(object):
    pass

c = C()
k = 0
def f2():
    def f3():
        c.k = k

    if k:
        k
    if k:
        k
    if k:
        k
    if k:
        k
    if k:
        k
    if k:
        k
    if k:
        k

    k = ''

x4 = 1
def f4():
    x4 = ''
    def f5():
        global x4
        x4 # 8 int

    def f6():
        x4 # 8 str
