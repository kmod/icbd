"""
type upconverting
"""

if "":
    s = None
    x = 1.0
else:
    s = ""
    x = 1

t = (s, x)
print t

def f(s, x):
    pass

f("", 1)
f(None, 1.0)

def f2():
    s = ''
    s = None
    s = ''
    x = 1.0
    x = 1
    def g():
        s
        x
f2()

class C(object):
    def __init__(self):
        self.s = None
        self.x = 1.0
C().s = ''
C().x = 1

l = [1, 1.0]
print l
print 1 if True else 1.0

def f3():
    if 1:
        return 1
    else:
        return 1.0
print f3()

def f4():
    if 1:
        return None
    elif 2:
        return
    else:
        return ''
print len([f4()])

def f5(x=1):
    return x
print f5(1.0)
