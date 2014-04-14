"""
string formatting
"""

print "hello %s" % "world"
print "%d" % 1, "%s" % (1,), "%s" % ((1,),)
print "2 + 2 = %d" % (2 + 2)

s = "%s"
for i in xrange(100000):
    s = "%s" % s
print s

print "%s" % [["a"]][0]
