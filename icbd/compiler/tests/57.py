"""
importfrom
"""

from time import time, clock
print time(), clock()
for i in xrange(100000):
    i *= 2
print time(), clock()
