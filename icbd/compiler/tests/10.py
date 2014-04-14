"""
refcounting test; should hit 0 allocations at the end
"""

def main():
    l = [1, 2]
    print len(l)
    l = []

    def sum(l):
        return 1

    def sort(l):
        return l

    def sort2(l):
        return []

    def sort3(l):
        l2 = l
        return l

    l = []
    print 1
    sum(l)
    print 2
    sum([])
    print 3
    sort(l)
    print 4
    sort([])
    print 5
    sort2(l)
    print 6
    sort2([])
    print 7
    sort3(l)
    print 8
    sort3([])
    print 9

    if 0:
        l.append(1)
    for i in xrange(len(l)):
        print i, l[i]

    l2 = []
    if 5 % 2:
        print len(l2)

    l3 = []
    if 4 % 2:
        print len(l3)

    [].append(1)
    len([])
    print [1][0]

    l = []
    l = l
    print len(l)

    f5 = []
    def f5():
        pass

    l4 = [1]
    if "a":
        l4 = [2]
    def f6():
        return len(l4)
main()
