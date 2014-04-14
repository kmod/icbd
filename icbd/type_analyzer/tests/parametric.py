import collections

def unknown():
    raise Exception()

l = [1] # 0 [<int|str>]
l.append(2) # 0 [<int|str>] # 2 (<int|str>) -> None
l.append('')
l[0] = 1
l[0] = ""

l2 = list(l) # 0 [<int|str>]
l2 = sorted(l) # 0 [<int|str>]
x = collections.deque(l2).pop() # 0 <int|str>
l2 = reversed(l) # 0 iterator of <int|str>
l2 = {1:l}[1] # 0 [<int|str>]
l2 = {'':l}[1] # 0 [<int|str>] # e 5
l2 = (l, l)[0] # 0 [<int|str>]

l = range(5)
l2 = list(l) # 0 [int]
l2 = sorted(l) # 0 [int]
x = collections.deque(l2).pop() # 0 int
l2 = reversed(l) # 0 iterator of int
l2 = {1:l}[1] # 0 [int]
l2 = {'':l}[1] # 0 [int] # e 5
l2 = (l, l)[0] # 0 [int]

d = dict([(1,2), (3,4)]) # 0 {int:int}
d = dict([]) # 0 {<unknown>:<unknown>}
d = dict([1]) # 0 <unknown> # e 4
d = dict(1) # 0 <unknown> # e 4
d = dict(unknown()) # 0 {<unknown>:<unknown>}
d = dict({1:''}) # 0 {int:str}
d = dict(a=1) # 0 {str:int}

l = range(3) # 0 [<int|object>]
l.extend([object()])

s = set() # 0 set(int)
s.add(2) # 0 set(int) # 2 (int) -> None

s = set() # 0 set(<unknown>)
s = set(2) # e 4 # 0 set(<unknown>)
s = set('') # 0 set(str)

l = []
l[''] = 1 # e 0

def f(x): # 4 (int) -> str
    return ''*x
l1 = range(2) # 0 [int]
l2 = map(f, l1) # 0 [str]
s1 = "abc123" # 0 str
# filter special cases strings...
s2 = filter(str.isalpha, s1) # 0 str
s3 = ''.join(s2) # 0 str
s4 = filter(str.isalpha, [s1]) # 0 [str]

d = {1:2} # 0 {int:int}
d2 = d.copy() # 0 {<int|str>:<bool|int>}
d2[''] = True # 0 {<int|str>:<bool|int>}

d = {1:''} # 0 {int:str}
t = d.popitem() # 0 (int,str)
d.clear()

d = {1:2} # 0 {int:<int|str>}
x = d.setdefault(2, '') # 0 <int|str>

d = {1:2} # 0 {int:int}
x = d.get(2, '') # 0 <int|str>

s = set([1,2]) # 0 set(int)
s2 = s.difference(['']) # 0 set(int)

s = set([1,2]) # 0 set(int)
s2 = s.difference_update(['']) # 0 None

s = set([1, 2])
x = s.pop() # 0 int
s.remove('') # e 0
s.remove(0)

s = set([1, 2]) # 0 set(int)
l = ["a"] # 0 [str]
s2 = s.symmetric_difference(l) # 0 set(<int|str>)

s = set([1, 2]) # 0 set(<int|str>)
l = ["a"] # 0 [str]
s2 = s.symmetric_difference_update(l) # 0 None

s = set([1, 2]) # 0 set(int)
l = ["a"] # 0 [str]
s2 = s.union(l) # 0 set(<int|str>)

s = set([1, 2]) # 0 set(<int|str>)
l = ["a"] # 0 [str]
s2 = s.update(l) # 0 None

t1 = (1,) # 0 (int,)
t2 = ('',) # 0 (str,)
t3 = t1 + t2 # 0 (int,str)

s = set([''])
s.issubset([1]) # e 0
s.issuperset([1]) # e 0

s = set(['', 1])
s.issubset([1]) # e 0
s.issuperset([1])

s = set([1])
s.issubset([1, ''])
s.issuperset([1, '']) # e 0

def f9():
    r = range(5) # 4 [int]
    f = map(float, r) # 4 [float]
    m = max(f) # 4 float

    def f(x, y): # 8 (str,int) -> [str]
        return [x] * y

    l = map(f, "aoeu", range(4)) # 4 [[str]]

def f10():
    def is_divisible(x, k): # 8 (int,int) -> bool
        return (x%k) == 0

    l = filter(lambda x:is_divisible(x, 3), range(100)) # 4 [int]

    l2 = filter(None, range(10)) # 4 [int]
    print l2

    l3 = filter(None, "") # 4 str
    l4 = filter(None, [""]) # 4 [str]

    if 1:
        l = ''
    else:
        l = [1]
    l5 = filter(None, l) # 4 <[int]|str> # 22 <[int]|str>
