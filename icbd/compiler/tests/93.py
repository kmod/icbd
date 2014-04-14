"""
builtin types constructors
"""

def main():
    d = {1:(1,3), 2:(1,2)}
    print list(range(5))
    print list(d)

    print dict(d)
    print dict(d.items())
    print dict(d.itervalues())

    s = set(range(5))
    print len(s)
    print 4 in s
    print 5 in s
    print list(s)

    s = set()
    s.add(1)
    print list(s)

    s2 = set(["", "", "world"])
    print list(s2)
    s3 = set([[], [], [1,2]])
    print list(s2)

    d = dict([(i, []) for i in xrange(10)])
    d = dict([(i, []) for i in xrange(10)])
main()
