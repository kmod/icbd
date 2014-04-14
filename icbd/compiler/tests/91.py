"""
dict iterator methods
"""

def main():
    d = {1:[1], 3:[2, 3]}
    k = d.iterkeys()
    y = k.next()
    for x in k:
        print x

    v = d.itervalues()
    y = v.next()
    for x in v:
        print x

    i = d.iteritems()
    y = i.next()
    for x in i:
        print x
main()
