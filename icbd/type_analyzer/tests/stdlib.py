f = open("/dev/null") # 0 file
for l in f: # 4 str
    pass

import collections
d = collections.deque() # 0 deque(int)
d.append(0)
d.appendleft(0)
d.extend([])
d.extendleft([])

s = raw_input() # 0 str
s = raw_input("") # 0 str

b = isinstance(1, int) # 0 bool
