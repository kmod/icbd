if 0:
    print 1
else:
    print 2

for i in xrange(0): # 4 int # 9 (int,int?,int?) -> [int]
    print i # 10 int
else:
    print "else"
print "done"
print i # 6 int

if 0:
    a = 0   # 4 int
elif 1:
    a = object() # 4 object # 8 class 'object'
elif 2:
    a = ()
else:
    a = ""  # 4 str
a # 0 <()|int|object|str>
a # !0 <mixed>

l = range(5) # 0 [int]
t = 0 # 0 int
for x in l: # 4 int # 9 [int]
    t += x # 4 int # 9 int
for i in xrange(len(l)): # 4 int
    t -= l[i] # 4 int # 9 [int] # 11 int
assert t == 0 # 7 int

l2 = [range(i) for i in xrange(10)] # 0 [[int]]
for l in l2: # 4 [int]
    for x in l: # 8 int
        y = x

for i in 0: # e 0
    print i

for k in {"":2}: # 4 str
    y = k # 4 str # 8 str

li = range(5).__iter__() # 0 iterator of int
for i in li: # 4 int
    k = i # 4 int

l = range(5)
x = l[""] # e 4

x = 1 # 0 int
while l:
    x = "" # 4 str
    break
x # 0 <int|str>

x = 1 # 0 int
while True:
    x = '' # 4 str
    break
x # 0 str

def loop(): # 4 () -> <unknown>
    x = 1 # 4 int
    0() # e 4
    while True:
        x = '' # 8 str
    0()
    return x
x = loop() # 0 <unknown> # 4 () -> <unknown>

x = object() # 0 object
while True:
    if 1:
        x = 1 # 8 int
        continue
    else:
        x = "" # 8 str
        break
x # 0 str

def f(): # 4 () -> <unknown>
    raise Exception()
    return 1
y = f() # 0 <unknown>
