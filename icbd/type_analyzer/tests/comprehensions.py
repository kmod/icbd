def f1():
    l = [i**2 for i in xrange(5)] # 4 [int] # 9 int # 18 int
def f2():
    l = [(a,b) for a in xrange(2) for b in xrange(3)] # 4 [(int,int)] # 10 int # 12 int # 19 int # 38 int
def f3():
    l = [i**2 for i in xrange(10) if i%2 == 1] # 4 [int] # 37 int
def f4():
    l = [(a,b) for a in xrange(5) for b in xrange(a)] # 4 [(int,int)] # 50 int
def f5():
    l = [(a,b) for a in xrange(b) for b in xrange(5)] # e 31
def f6():
    t = sum([i**2 for i in xrange(20)]) # 4 int
def f14():
    l = [1 for a in xrange(5) if a == 2 for b in xrange(5) if a == 3] # 4 [int] # 33 int # 44 int # 62 int
def f15():
    l = [1 for a in xrange(5) if b == 2 for b in xrange(5) if a == 3] # e 33
def f16():
    l = [1 for a in xrange(5) if a == 2 for b in xrange(5) if b == 3] # 4 [int] # 33 int # 44 int # 62 int
def f17():
    l = [i**2 for i in xrange(i)] # e 30
def f18():
    l = [(a,b) for a in xrange(b) for b in xrange(a)] # e 31
def f19():
    l = [(a,b) for a in xrange(1) for b in xrange(b)] # e 50
def f20():
    l1 = ([(1,2)],) # 4 ([(int,int)],)
    l = [[a+b for a,b in t] for t in l1] # 4 [[int]] # 10 int # 12 int # 18 int # 20 int # 25 [(int,int)] # 32 [(int,int)] # 37 ([(int,int)],)
def f21():
    l = [x for x in l] # e 20 # 4 [<unknown>]
def f22():
    def f(x): # 8 (int) -> int
        return x
    l = [x for x in range(5) if f(x)] # 4 [int]

def f7():
    l = (i**2 for i in xrange(5)) # 4 generator of int
def f8():
    l = ((a,b) for a in xrange(2) for b in xrange(3)) # 4 generator of (int,int)
def f9():
    l = (i**2 for i in xrange(10) if i%2 == 1) # 4 generator of int
def f10():
    l = ((a,b) for a in xrange(5) for b in xrange(a)) # 4 generator of (int,int)
def f11():
    l = ((a,b) for a in xrange(b) for b in xrange(5)) # e 31
def f12():
    t = sum((i**2 for i in xrange(20)))
def f13():
    t = sum(i**2 for i in xrange(20))

