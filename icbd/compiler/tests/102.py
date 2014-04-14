"""
overriding buitlin names
"""

slice = 1
aoeu = 2

def f():
    print aoeu
    return slice

def g():
    int = 1
    def h():
        return int
    print h()

print f()
g()
