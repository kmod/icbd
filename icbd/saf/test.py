y1 = 2

def f5(x=1):         # 4 (int?) -> int
    return x**2     # 11 int

def g1(s):               # 4 (str) -> str
    return s.lower()    # 13 () -> str
g1('')

class C(object):
    def __init__(self):
        self.x = 1

c = C()
c
