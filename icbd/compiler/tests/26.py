"""
file test
"""

f = open("Makefile")
while True:
    s = f.read(10000)
    print len(s)
    if not s:
        break
print "done"

f = open("Makefile")
while True:
    s = f.readline()
    if not s:
        break
    print s,
