"""
is and is not
"""

class C(object):
    pass

c1, c2 = C(), C()
print c1 is c2
print c1 is not c2
print c1 is c1
print c1 is not c1

# Run it through mk_string to make sure it gets raised to a full string type
# It will correctly throw a compiler error if you check whether two str constants
# 'is' each other
def mk_string(s):
    return s
s1, s2, s3 = mk_string(""), mk_string(""), mk_string(""+"")
print s1 is s1
print s1 is s2
print s1 is s3
print s2 is s3
print s1 is not s2
print s1 is not s1
print s3 is not s1
