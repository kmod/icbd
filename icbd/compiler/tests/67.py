"""
Testing polymorphic functions
"""

print abs(1)
print abs(1.1)

def f(a):
    return a(2)
print f(abs)
# This is tough (well, to support both of them, at least):
# def f2(a):
    # return a(2.2)
# print f2(abs)

l = range(10)
print l[4]
print l[::-1]
print l[:-1:-1]
print l[1:9:2]
print l[1000000000:0:-7]
print l[1000000001:0:-7]
print l[1000000001:10000:-7]
print l[3:500:2]
print l[10:0:-1]
print l[500:]

# Test with malloc'd things in the list as well to make sure they get freed:
l2 = [range(i) for i in range(10)]
print l2[5]
print l2[1:3]
print l2[5::-1]

s = "abcdefghijk"
print s[5]
print s[::-1]
print s[1:9:2]
print s[1000000000:0:-7]
print s[1000000001:0:-7]
print s[1000000001:10000:-7]
print s[3:500:2]
print s[500:]
