"""
simple import test
"""

import time
print time.time()
for i in xrange(10):
    time.sleep(.1)
    print time.time()

def fourth_root(x):
    import math
    def s1(x):
        def s2():
            return math.sqrt(x)
        return s2()
    return s1(s1(x))

print fourth_root(16)
print fourth_root(20)

def f(n):
    import math
    r = []
    for i in range(n):
        r.append(math.sqrt(i))
    return r
f(100)

