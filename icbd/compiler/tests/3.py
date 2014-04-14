"""
more complicated control flow test: the 3n+1 problem [the first real thing it was able to compile]
"""

x = 27
# x = 25
while x > 1:
    print x
    if x & 1 == 0:
        x = x >> 1
    else:
        x = x * 3 + 1
print x
