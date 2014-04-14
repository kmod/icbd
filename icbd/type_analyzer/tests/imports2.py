from import_test import dup
dup # 0 <int|module 'dup'>

from import_test import g
# packages hide modules with the same name:
g.xg # 0 module 'g' # 2 str

from import_test.f import dup1, dup2, e1, e2, xg
dup1 # 0 <int|module 'dup'>
dup2 # 0 module 'dup'
e1 # 0 module 'e'
e2 # 0 module 'e'
xg # 0 str

from import_test import a
a # 0 module 'a'
import import_test
import_test.a # 12 module 'a'

from . import sys # e 0
from .os import path # e 0
