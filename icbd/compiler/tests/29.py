"""
closure test
"""

x = 65
l = ["aoeu"]
s = "aoeu"

def f():
    # return 1
    return chr(x) + l[0]

print f()

f2 = lambda y: x + y
print f2(5)
