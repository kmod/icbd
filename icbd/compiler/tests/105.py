"""
boxing on attribute-access of a boxed object
"""

class A(object):
    def __init__(self):
        self.x = 1

class B(object):
    def __init__(self):
        self.x = "hello world"

def f(o):
    print o.x
f(A())
f(B())
