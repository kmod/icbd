"""
dicts
"""

d = {}
for i in xrange(10):
    d[i] = i ** 2

print d

print {1:[]}

print d.values()

d2 = {}
d2["hello"] = ""
d2["hello"] = "world"
print d2
print d2["hello"]

d3 = {}
d3[1] = 2
d3[1] = 3
print d3[1]
print len(d3)

d4 = {}
d4[(2,)] = ""
d4[(2,)] = "new"
for i in xrange(10):
    d4[(i,)] = str(i)
print len(d4)

for i in xrange(20):
    print (i,) in d4, d4.get((i,), "nope not in there")
