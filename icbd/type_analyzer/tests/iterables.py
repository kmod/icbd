l = [1] # 0 [int]
d = {True:l} # 0 {bool:[int]}

l2 = sorted(l) # 0 [int]
l3 = sorted(d) # 0 [bool]
l4 = sorted('') # 0 [str]
l5 = sorted(1) # 0 [<unknown>] # e 5

l2 = reversed(l) # 0 iterator of int
l3 = reversed(d) # 0 iterator of bool
l4 = reversed('') # 0 iterator of str
l5 = reversed(1) # 0 iterator of <unknown> # e 5

l2 = list(l) # 0 [int]
l3 = list(d) # 0 [bool]
l4 = list('') # 0 [str]
l5 = list(1) # 0 [<unknown>] # e 5

