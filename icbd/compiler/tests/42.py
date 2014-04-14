"""
with statement
"""

class C(object):
    def __enter__(self):
        print "enter!"
        return self

    def __exit__(self, a, b, c):
        print "exit!"

    def __repr__(self):
        return "a c instance"

c = C()
# Hack:
if 0:
    c.__exit__(None, None, None)

with c as b:
    print "inner"
    print b

with open('/dev/null') as f:
    print len(f.read(128))
