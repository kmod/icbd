from . import dup as dup1

dup1 # 0 <module 'dup'|num>

import dup as dup2

dup2 # 0 module 'dup'

from .d import e as e1
e1

from d import e as e2
e2

from . import g
xg = g.xg

from .d.e import x as x2
print x2
