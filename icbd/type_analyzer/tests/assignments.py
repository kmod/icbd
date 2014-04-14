a,a = 1,'x' # 0 int # 2 str
print a # 6 str
(a,b,b),a = ((1, None, 'x'), True) # 1 int # 3 None # 5 str # 8 bool
print a, b # 6 bool # 9 str
(a, b) = a = (1, 'x') # 1 int # 4 str # 9 (int,str)
print a, b # 6 (int,str) # 9 str

class C(object):
    pass

c = C()

c.a = 1 # 2 <int|str> # 0 C
c.a = '' # 2 <int|str> # 0 C

[a,b] = [1] # 1 int # 3 int
