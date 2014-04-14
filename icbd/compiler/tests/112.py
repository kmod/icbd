"""
controllable formatting (mainly around floats)

note: this program outputs different results under python2.6 and python2.7;
TODO ideally icbd would be configurable in which it emulated, but for now
it outputs the 2.7 version.
"""

import math
def p(x):
    print "%f" % x, "%.3f" % x, "% 20f" % x, "% 12.2f" % x, str(x), repr(x)
p(math.pi)
p(math.pi * 10)
p(math.pi * 100)

print "% 2%" % ()
print "% 5s" % "hi"
print "% 1s" % "hi"
