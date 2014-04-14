"""
misc functionality test
"""

def f(x=12345, y=54321):
    print x, y
    return x * y

print f(1, 5)

l = []
for i in xrange(5):
    print l
    l.append(i)
print l

l2 = [l, l, l]
print [l2, l2]

l = []
l2 = []
l3 = []
for i in xrange(128):
    l.append(i)
    l2.append(l)
    l3.append(l2)
print len(str(l3))

l = ["hello", "world"]
print " ".join(l)

print str([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

print range(5)

if __name__ == "__main__":
    print "run as a script"
else:
    print "imported?"

def f():
    print 'f'
    return

f()
print f

# testing that list_str uses repr rather than str:
if str(["[]"]) == str([[]]):
    print "error: list_str uses elt_str instead of elt_repr"
    print [][0]

class C(object):
    pass
print (1, 123456789.123456789, str(123456789.123456789), 'hello', [], (), C())

print "aoeu" != "asdf"

print len(open("/dev/null").read(156))

def f2(x, y):
    return x * y
l = range(10)
l2 = map(lambda y:f2(7, y), l)
print l, l2
print map(lambda x:1.0/x, [i + 1 for i in xrange(10)])
