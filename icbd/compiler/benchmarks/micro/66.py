import time
print time.time()
l = [[i for i in xrange(j)] for j in xrange(2000)]
print time.time()
print len(str(l))
print time.time()

