def f(x, *l): # 4 (int,*[<unknown>]) -> int # 10 [<unknown>]
    return x * len(l) # 11 int # 19 [<unknown>]

y = f(0) # 0 int

def sum(*l): # 4 (*[int]) -> int
    t = 0 # 4 int
    for x in l: # 8 int # 13 [int]
        t += x # 8 int # 13 int
    return t

z = sum(1, 2, 3) # 0 int # 4 (*[int]) -> int

def k(x, y, z=1): # 4 (int,str,int?) -> str # 6 int # 9 str # 12 int
    return y * (x + z) # 11 str # 16 int # 20 int
k(1, y='')

def k2(a, b): # 4 (int,int) -> int
    return a * b
z = k2(b=1, a=3) # 0 int

def kw(**kw): # 4 (**{str:<unknown>}) -> None # 9 {str:<unknown>}
    for s in kw: # 8 str # 13 {str:<unknown>}
        print s # 14 str

def kw2(**kw): # 4 (**{str:int}) -> int
    t = 0 # 4 int
    for s, v in kw.items(): # 8 str # 11 int # 16 {str:int}
        t += v # 8 int # 13 int
    return t # 11 int
kw2(a=1, b=2)

def kw3(**kw): # 4 (**{str:<int|str>}) -> {str:<int|str>}
    return kw # 11 {str:<int|str>}

d1 = kw3() # 0 {str:<int|str>}
d2 = kw3(a=1) # 0 {str:<int|str>}
d3 = kw3(b='') # 0 {str:<int|str>}

def test_all(a, b, c=1, *args, **kw): # 4 (int,int,int?,*[str],**{str:object}) -> object
    idx = (a * b) + c # 4 int
    s = args[idx] # 4 str
    return kw[s] # 11 {str:object}

test_all(1, 2, 3, "", k=object())

def f((x, y), z): # 4 ((int,int),int) -> int
    return x + y + z # 11 int # 15 int # 19 int
k = f((1,2), 3) # 0 int

def f(x): # 4 (int) -> int # 6 int
    return x # 11 int

y = f(x=1) # 0 int

d = {1:''} # 0 {int:str}
x = d.get(2) # 0 str # this is true if None hiding is turned on
y = d.get(2, '') # 0 str
z = d.get(2, 2) # 0 <int|str>
d = {1:''} # 0 {int:str}
x = d.get('') # e 4 # 0 str # this is true if None hiding is turned on

def f5(a, b, *c): # 4 (int,int,*[int]) -> int
    return b
f5(*range(0))

def f6(a, b, *c): # 4 (int,int,*[int]) -> int
    return b
f6(2, 3, *range(0))

def f7():
    def f(a, b): # 10 int # 13 str
        print a, b

    f(*(1, ''))
    f(*(1, '', True)) # e 4

def f8():
    def f(a, b): # 10 <bool|int|str> # 13 <bool|int|str>
        print a, b
    f(*[1, '', True])

def f9():
    def f(a, b, *c): # 10 int # 13 int # 17 [<bool|str>]
        print a, b, c

    f(1, *(2, '', True))

def f10():
    def f(a, b, *c): # 10 int # 13 <bool|int|str> # 17 [<bool|int|str>]
        print a, b, c

    f(1, *[2, '', True])

def f11():
    def f(a, b, *c): # 10 <int|str> # 13 <int|str> # 17 [<int|str>]
        print a, b, c

    f(*[2, ''])
