"""
None handling
"""

def main():
    print None, repr(None)
    if 1:
        l = None
        s = None
        d = None
        t = None
    else:
        l = [1]
        s = ""
        d = {1:2}
        t = ()
    print l, s, d, t, repr(s)
    print () == None
    print None == ()

    x = [].append(1)
    print x

    def f6(l):
        pass
    f6([""])
    f6([None])
    f6(None)

    def f7(l):
        print l
    f7([[""]])
    f7([None, [None]])
    f7(None)

    def f8(l):
        print l
    if 1:
        l = None
    else:
        l = [1]
    f8(l)

    d = {1:None}
    print d
    print d[1]

    d = {1:[1], 2:None}
    l = d[2]
main()
