"""
defining functions inside loops
"""

# in the global scope:

l = []
for i in xrange(5):
    def f():
        print i
    def g():
        f()
    g()
    l.append(f)
for _f in l:
    _f()

# in a function scope:

def wrapper():
    l = []
    for i in xrange(5):
        def f():
            print i
        f()
        l.append(f)
    for _f in l:
        _f()
wrapper()
