"""
try/except
"""

try:
    1/0
except Exception:
    print "bad!"
except Exception:
    print "second bad!"
else:
    print "else"
finally:
    print "finally"
print "done"
