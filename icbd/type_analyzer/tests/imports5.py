import import_test.a as y
import import_test

x = import_test.a # 0 module 'a'
y # 0 module 'a'

import import_test.dup as dup
dup # 0 module 'dup'
import_test.dup # 12 <int|module 'dup'>
