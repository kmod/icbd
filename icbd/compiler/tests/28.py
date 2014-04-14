"""
string functionality test
"""

def main():
    s = " hello  world  "
    l = s.split()
    print len(l)
    for i in xrange(len(l)):
        print i, len(l[i]), l[i]
    print "done"

    print int("123") + 5

    def map(f, l):
        r = []
        for i in xrange(len(l)):
            r.append(f(l[i]))
        return r
    l = map(int, "1 2 3 5 7 9".split())
    for i in xrange(len(l)):
        print l[i] + 5

    s = "hello  \t world"
    print s.split()
    print s.split(' ')
    print s.split('l')
    print s.split('ll')
    print s.split("he")
    print s.split("ld")
    print s.split(s)
    print s.split("X")
    print s.strip()
    print repr("\thello world\n ".strip())

    print repr("\n\t\r\0\xff\\\"\'")
    for i in xrange(256):
        if i == ord('\''):
            # I don't currently handle switching repr to use double-quotes
            continue
        print i, repr(chr(i))
main()
