"""
__nonzero__ test
"""

print not 1
print not True
print not ""
def ident(s):
    return s
print not ident(" ")

if " ":
    pass
if True:
    pass
if not True:
    pass
if 5:
    pass
