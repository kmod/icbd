class A(object):
    def __init__(self):
        self.x = 0
        self.l = []

    def f(self):
        print "this is an A"
        self.x += 1
        self.l.append(1 - self.x)

class B(object):
    def __init__(self):
        self.x = 0
        self.l = []

    def f(self):
        print "this is a B"
        self.x -= 1
        self.l.append(self.x)

def call_f(o):
    print o.l
    print o.x
    o.f()
    print o.l
    print o.x
    # print repr(B)

call_f(A())
call_f(B())
if "true":
    print "start of A block"
    o = A()
    print "end of A block"
else:
    o = B()
print "about to call"
call_f(o)
