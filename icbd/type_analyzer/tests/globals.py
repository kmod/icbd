x = 0 # 0 int
y = 0 # 0 int

def f(): # 4 () -> int
    global x, y # 11 int # 14 <int|str>
    r = x # 4 int # 8 int
    x += 1 # 4 int
    y += 1 # 4 <int|str> # e 4
    return r # 11 int

def g(): # 4 () -> str
    global y # 11 <int|str>
    y = "" # 4 str
    return y # 11 str

k = 1
def f1():
    k = "inner"
    def f2():
        global k
        def f3():
            return k
        return f3
    return f2

r = f1()()() # 0 int

x1 = 0 # 0 int
x2 = 0 # 0 int
def f2():
    x1 # 4 int
    x2 # 4 <int|str>
    x2 = "" # 4 str
    global x1, x2 # 11 int # 15 <int|str>
    x1 # 4 int
    x2 # 4 str

f2()
def f3():
    global x1, x2
    x1 # 4 int
    x2 # 4 <int|str>

x1 # 0 int
x2 # 0 <int|str>
x2 = "" # 0 str
f2()
x2 # 0 <int|str>
x2 = 1 # 0 int
f2()
x2 # 0 <int|str>
