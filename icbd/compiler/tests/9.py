"""
inlining/optimization test (the print statements should all print constant values and there shouldnt be any loads, though the stores might not be eliminated.  also all refcounting should be elided.)
"""

l = []
l.append(123)
l.append(321)
print l[0], len(l)
l[1] = 666
print l[1]
