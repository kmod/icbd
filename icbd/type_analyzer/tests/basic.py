a = a # e 4
a = 1       # 0 int
l = [a]     # 0 [int]
d = {a:l}   # 0 {int:[int]}

s = "abc"
c = ord(s[2].lower()[0]) # 0 int # 4 (str) -> int
l2 = [range(i) for i in d] # 0 [[int]]

y = [(a,b) for a,b in {1:'2'}.iteritems()] # 0 [(int,str)]

b = 1 # 0 int
if 0:
    b = '' # 4 str
else:
    b = str(b) # 4 str # 12 int

r = 0 # 0 int
if r: # 3 int
    r = str(r) # 4 str # 12 int
r # 0 <int|str>

l = range(5) # 0 [int]
l2 = l[2:3] # 0 [int]
x = l2[1] # 0 int

k = 1() # 0 <unknown> # e 4

del k
k # e 0

l = [] # 0 [int]
x = 1 # 0 int
while x: # 6 int
    l = [] # 4 [int]
l.append(1) # 0 [int] # 2 (int) -> None

l = [1, 2] # 0 [int]
l2 = [x for x in l] # 0 [<int|str>]
l2.append('') # 0 [<int|str>]

s = str() # 0 str
s2 = str(s) # 0 str
s3 = repr() # e 5 # 0 str
s4 = repr(s) # 0 str

x = 1 if [] else '' # 0 <int|str>

l = [1] # 0 [<int|str>]
l2 = [''] # 0 [str]
l[:] = l2 # 0 [<int|str>]

b = 1 < 2 < 3 # 0 bool

l = sorted(range(5), key=lambda x:-x) # 0 [int]

d = {} # 0 {<bool|int>:<int|str>}
d1 = {1:''} # 0 {int:str}
d.update(d1)
d[True] = 1
d # 0 {<bool|int>:<int|str>}

l = [] # 0 [int]
l1 = [] # 0 [<unknown>]
l.extend(l1)
l.append(2)

l = [] # 0 [<[str]|int>]
l1 = [[]] # 0 [[str]]
l.extend(l1)
l[0].append('') # e 0
l.append(1)

l = [] # 0 [[<int|str>]]
l2 = [1] # 0 [int]
l3 = [''] # 0 [str]
l.append(l2)
l.append(l3)

for i, s in enumerate("aoeu"): # 4 int # 7 str
    pass

x = 1 # 0 int
y = x + 1.0 # 0 float
y << 1 # e 0
l = [1, 1.0] # 0 [float]
1.0 in [1] # e 0

x = `1` # 0 str
def f():
    x = `1` # 4 str

d = dict(a=1) # 0 {str:int}
l = list() # 0 [<unknown>]

i = int(1) # 0 int
i = int(1.2) # 0 int
i = abs(1) # 0 int
i = abs(1.0) # 0 float

d = dict() # 0 {int:int}
d[1] = 2
d2 = dict(d) # 0 {<int|str>:<int|str>}
d2[''] = ''
d3 = dict([(1,2)]) # 0 {int:int}
d4 = dict(a=1) # 0 {str:int}
