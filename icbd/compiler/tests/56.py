"""
writing to global variables
"""

x = 1

def f():
    global x
    x
    x = 2

    def g():
        return x
    print g()

print x
f()
print x

def f3():
    global x
    x = 4
    print x
    f()
    # This needs to reload from the globals:
    print x
f3()
print x
