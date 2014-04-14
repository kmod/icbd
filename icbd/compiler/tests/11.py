"""
more detailed refcounting test
"""

def sum(l):
    print "start of sum"
    l
    print "end of sum"
    return 1

print "about to run sum"
sum([])
print "done with sum"

l = []
for i in xrange(2):
    print i
    l.append(i)
