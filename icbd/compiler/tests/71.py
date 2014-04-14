"""
type lookahead: some operations need to be done knowing the resulting type
"""

# Somewhat easy: the type checker knows that l1 has type [str] from the start
l1 = [None]
l1[0] = "hello"
print l1

# Hard: the list literal correctly has type [None], but [None] * 1 needs to return
# an object of type [str], a case of things needing to be upconverted from _get
l2 = [None] * 1
l2[0] = ""
print l2
