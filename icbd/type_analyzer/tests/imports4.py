import import_test.d.e

import_test # 0 module 'import_test'
import_test.d # 12 module 'd'
import_test.d.e # 14 module 'e'
import_test.d.e.x # 16 module 'b'

from import_test.f import x2 as x3
x3 # 0 module 'b'

from .imports2 import e1 # e 0
