y1 = 2

def f5(x=1):         # 4 (int?) -> int
    return x**2     # 11 int

def g1(s):               # 4 (str) -> str
    return s.lower()    # 13 () -> str

x = g1() # 4 (str) -> str # 0 str # e 4

def test():             # 4 () -> None
    def f2(x):          # 8 (int) -> str
        return f1(x).lower()

    def f1(x):          # 8 (int) -> str
        return "." * x

    f2(2)               # 4 (int) -> str

def h():                # 4 () -> str
    global y1, z, x
    y1 = 2
    return ""

def main():
    f5()
    f5(y1)
    g1(g1(h()))
    test()

main()  # 0 () -> None


x9 = "" # 0 str
def g2(): # 4 () -> str
    def f6(): # 8 () -> str
        if 0:
            return f6()
        return x9
    return f6()
y = g2() # 0 str # 4 () -> str



def r1(x):
    if x:
        return len(r2('.'*x))
    return -1

def r2(x):
    if x > 0: # e 7 # 7 str
        return '*' * r1(len(x))
    return 'bad'

def f3(x): # 4 (int) -> int
    if x > 0:
        return f3(x-1)
    return 0
print f3(0)

def f4(x): # 4 (<unknown>) -> int
    if x > 0:
        return f4(x)
    return 0

def f7():
    pass

def f6(x): # 4 (int) -> int # 7 int
    f7()
    return x # 11 int

k = f6(2) # 0 int



def f9(x): # 4 (<int|str>) -> <int|str>
    return x # 11 <int|str>

f9 # 0 (<int|str>) -> <int|str>

while '':
    f9 # 4 (<int|str>) -> <int|str>

    x = f9(1) # 4 <int|str>

y = f9 # 0 (<int|str>) -> <int|str>
z = y('') # 0 <int|str>

# testing un-called functions:
def f(): # 4 () -> int
    return 2

def f():
    def g(l=[]): # 8 ([int]?) -> [int] # 10 [int]
        return l
    l1 = g() # 4 [int]
    l1.append(2)
    l2 = g() # 4 [int]
