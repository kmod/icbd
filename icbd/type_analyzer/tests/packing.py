a,b = (1, 'b') # 0 int # 2 str
a,b = [1, 'b'] # 0 <int|str> # 2 <int|str>
a,b = [1, 1] # 0 int # 2 int

d = {'b':1} # 0 {<int|str>:<int|str>}
d[1] = 'b' # 0 {<int|str>:<int|str>}

d = {1:''} # 0 {int:str}
(x, y), (a,b) = d.iteritems() # 1 int # 4 str # 9 int # 11 str # 16 {int:str}

x = y = 1 # 0 int # 4 int
x,y = x = (1, '') # 0 int # 2 str # 6 (int,str)
x, y # 0 (int,str) # 3 str

x = 1 # 0 int
x = x = [x] # 0 [int] # 4 [int] # 9 int
x # 0 [int]

if []:
    t = [1,'']
else:
    t = (1, '', True)

a,a,a = t # 0 <int|str> # 2 <int|str> # 4 <bool|int|str>
print a # 6 <bool|int|str>
