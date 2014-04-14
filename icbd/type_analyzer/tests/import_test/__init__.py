from . import b
import c

from .b import x
from b import y
from .c import x
from c import y

dup = 1

not_m = "not_m"

__all__ = ['b', 'dup', 'not_m']
