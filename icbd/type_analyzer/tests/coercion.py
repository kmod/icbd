import collections

f = dict.get

# TODO not sure if this should be an error or not
x = f(None, 1) # e 4
x = f({1:2}, 1) # 0 int

f2 = collections.deque.popleft
# TODO not sure if this should be an error or not
x = f2(None) # e 4
x = f2(collections.deque({2:3})) # 0 int

d1 = dict([(1,2)]) # 0 {int:int}
d2 = dict({1:2}) # 0 {int:int}
l2 = sorted(d2) # 0 [int]
