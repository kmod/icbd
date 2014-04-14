d = {1:''} # 0 {int:str}
d2 = dict(d) # 0 {int:str}
print d2

l = [('', 2)] # 0 [(str,int)]
d3 = dict(l) # 0 {str:int}
print d3

l = [('', 2, 3)] # 0 [(str,int,int)]
d4 = dict(l) # e 5 # 0 <unknown>
print d4
