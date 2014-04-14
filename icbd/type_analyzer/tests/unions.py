class A(object):
    def __init__(self):
        self.x = ""

    def y(self, x=1):
        return x**2

class B(object):
    def __init__(self):
        self.x = 1

    def y(self):
        return self.x

if 0:
    o = A() # 4 A # 8 class 'A'
else:
    o = B() # 4 B # 8 class 'B'

o # 0 <A|B>
x = o.x # 0 <int|str> # 4 <A|B> # 6 <int|str>

y = o.y # 0 <() -> int|(int?) -> int> # 4 <A|B> # 6 <() -> int|(int?) -> int>
z = y() # 0 int # 4 <() -> int|(int?) -> int>

if x:
    def f(x): # 8 (<int|str>) -> int
        return 1
    f(1) # 4 (<int|str>) -> int
else:
    def f(x): # 8 (str) -> int
        return 2
f # 0 (<int|str>) -> int
x = f('') # 0 int # 4 (<int|str>) -> int

if x:
    def g(x): # 8 (int) -> int
        return 1
else:
    def g(x): # 8 (int) -> int
        return 2
g # 0 (int) -> int
x = g(1) # 0 int # 4 (int) -> int
