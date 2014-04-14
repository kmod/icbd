# This is probably never going to work:
if l:
    x = {1:2}
else:
    x = [(1,3)]
d5 = dict(x) # 0 {int:int}

# This is too hard; can't prove it will never be set back to int
from import_test import dup
dup # 0 module 'dup'

# import_test defines __all__, which is hard to support
from import_test import *
c # e 0

class A(object):
    def __init__(self):
        self.x = 1

class B(object):
    def __init__(self):
        super(B, self).__init__()
        self.x = ''

b = B()
b.x # 2 str

g = (i for i in xrange(5))
# Generator expression shouldnt keep the loop variable set, but that's hard to do
i # e 0
