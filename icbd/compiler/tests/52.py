"""
stdin / out / err
"""

import sys

sys.stderr.write("Please enter a number:\n")
n = int(sys.stdin.readline())
print "%d ** 2 = %d" % (n, n * n)
