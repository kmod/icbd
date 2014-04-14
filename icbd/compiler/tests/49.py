"""
classes and modules in closures
"""

import sys
print sys.argv

class C(object):
    def __str__(self):
        return "<C>"

def make():
    print sys.argv
    return C()

print make()
