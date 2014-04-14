1 < '' # e 0

# These could later to be found to not be an error, but they shouldnt mark the list as updating certainly
l1 = []
'' in l1 # e 0 # 6 [<unknown>]
l2 = [1]
'' in l2 # e 0 # 6 [int]


1 in "" # e 0

def f(x):
    return x

y = f() # e 4 # 0 <unknown>

l = []
l2 = l() # e 5

e = NotImplementedError() # 0 NotImplementedError
raise e
