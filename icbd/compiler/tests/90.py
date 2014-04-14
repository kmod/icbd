"""
imports test
"""

import import_target
print import_target.x

import import_target
import_target.foo()

c = import_target.C()

print import_target.import_nested_target.y
import_target.import_nested_target.bar()
d = import_target.import_nested_target.D()

from import_target import x as z
from import_nested_target import y

import import_nested_target
print import_nested_target.y
import_target.import_nested_target.y = import_nested_target.y + 1
print import_nested_target.y

print z
print y
print __name__
