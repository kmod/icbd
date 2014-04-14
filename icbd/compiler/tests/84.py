# Testing and/or behavior

print "true" or "BAD"
print "true" and "BAD"
# Have to make sure these get freed, too:
print [] or [1]
print [] and [1]


class C(object):
    def __init__(self, x, b):
        self.x = x
        self.b = b
        print "making", x, b
    def __nonzero__(self):
        print self.x, "nonzero"
        return self.b

print (C(0, True) and C(1, True) and C(2, False)).x
print (C(0, False) or C(1, False) or C(2, False)).x
print (C(0, True) and C(1, True) or C(2, False)).x
print (C(0, False) or C(1, True) and C(2, True)).x

# I guess cPython optimizes this:
x = (C(0, True) or C(1, True))
print (x and C(2, True)).x
print ((C(0, True) or C(1, True)) and C(2, True)).x

print ("" or None) # have to upconvert None
