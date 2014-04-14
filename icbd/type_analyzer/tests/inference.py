def f1():
    l = []          # 4 [int]
    d = {1:l}       # 4 {int:[int]}
    d[0][1] = 2     # 4 {int:[int]}
    x = l[1]        # 4 int

def f2():
    l = []          # 4 [int]
    d = {1:l}       # 4 {int:[int]}
    d[0].append(2)  # 4 {int:[int]}
    x = l[1]        # 4 int
    y = d[0][1]     # 4 int

def f3():
    l = []          # 4 [<unknown>]
    l1 = [1]        # 4 [int]
    d = {1:l, 2:l1}       # 4 {int:[int]}

def f4():
    l = []          # 4 [int]
    l1 = []         # 4 [int]
    d = {1:l, 2:l1}       # 4 {int:[int]}
    d[0].append(1)
    x = l[1]        # 4 int

def f5():
    d = {} # 4 {int:str}
    def add(x): # 8 (int) -> None # 12 int
        d[x] = '' # 8 {int:str} # 10 int
    add(1) # 4 (int) -> None
    d # 4 {int:str}

def f6():
    l = [] # 4 [int]
    def add(x): # 8 (int) -> None # 12 int
        l.append(x) # 8 [int] # 10 (int) -> None # 17 int
    add(1) # 4 (int) -> None
    l # 4 [int]

def f7():
    l = [] # 4 [[int]]
    l2 = [] # 4 [int]
    l.append(l2) # 4 [[int]] # 6 ([int]) -> None # 13 [int]
    l.pop().append(1) # 4 [[int]] # 6 (int?) -> [int] # 12 (int) -> None
    l2 # 4 [int]

def f8():
    l = [] # 4 [int]
    list.append(l, 1) # 4 class 'list' # 16 [int]

def f9():
    l1 = [] # 4 [int]
    l2 = [] # 4 [int]
    for x, l in ((1, l1), (2, l2)):
        l.append(1)
