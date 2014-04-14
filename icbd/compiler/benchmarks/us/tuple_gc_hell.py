#!/usr/bin/env python
#
# Test when Python's GC decides to do a full collection.
# Originally by Antoine Pitrou for http://bugs.python.org/issue4074.

import time

def Main():
 l = []
 prev_time = time.time()
 for i in xrange(10000000):
   if i % 1000000 == 0:
     cur_time = time.time()
     print i, cur_time - prev_time
     prev_time = cur_time
   l.append((i % 2, i % 12))

Main()
