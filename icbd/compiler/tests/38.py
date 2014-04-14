"""
list comprehensions
"""

def main():
    x = -1
    j = 2

    [True or False for x in xrange(0)]
    print x
    [True or False for x in xrange(2)]
    print x
    # l = [i for i in range(5 + i)]
    l = [(i == 0) or (i == 1) for i in range(5)]
    l = [range(i) for i in range(5)]

    print [x for x in ([1] if '' else [2])]
    print x
    print l

    x = -1
    print [[[x] for x in xrange(i)] for i in xrange(5)]
    print x
    x = -1
    print [[[x] for x in xrange(0)] for i in xrange(5)]
    print x
    x = -1
    print [[[x] for x in xrange(i)] for i in xrange(1)]
    print x

    def f0():
        global x
        [[x for x in xrange(i)] for i in xrange(5)]
        print x
    f0()

    def f1():
        [[x for x in xrange(i)] for i in xrange(5)]
        # x is not defined here:
        # print x
    f1()

    print [i for i in [2, 3, 5]]
    d = {1:2, 3:4}
    print d
    print [(v,k) for k, v in d.items()]
    print [(d[k], k) for k in d]

    x = 1
    def f():
        global x
        [x for x in xrange(4)]
    f()
    print x

    l = [(1, 2)]
    [t[0] for t in l]
    # t should not be defined here, so the iter variable should get freed

    l = [(1, 2)]
    t = (3, 4)
    print [t[0] for t in l]
    # This should use the t from the iter variable:
    print t

    l2 = [1]
    x2 = 0
    print [x2 for x2 in l2]
    print x2

    def mk_str(s):
        return s
    l3 = [mk_str('asdf')]
    s = mk_str("aoeu")
    print [s for s in l3]
    print s

    l3 = ['asdf']
    s = "aoeu"
    print [s for s in l3]
    print s

    [s for s in {'aoeu':'b'}]

    l4 = ['asdf', 'aoe', 'aoeu', 'abcd']
    s4 = "aoeu"
    [0 for s4 in l4]
    print s4

    def f5():
        l2 = ['asdf', 'aoe', 'aoeu', 'abcd']
        s = "aoeu"
        if 0:
            pass
        [0 for s in l2]
        print s
    f5()
main()
