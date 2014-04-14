"""
generator expressions
"""

def main():
    def f(x):
        print "f(%d)" % x
        return x
    g = (f(i) for i in xrange(5))

    for x in g:
        print x
main()
