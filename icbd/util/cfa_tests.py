import _ast
import sys

import ast_utils
from cfa import cfa

if __name__ == "__main__":
    t = """
try:
    1/0
except Exception:
    print "bad!"
except Exception2:
    print "second bad!"
else:
    print "else"
finally:
    print "finally"
print "done"
    """.strip()

    cfg = cfa(ast_utils.parse(t, "test"))
    cfg.show()
    sys.exit(-1)

    t = """
with f() as b:
    print b
    """.strip()

    t = """
x = 1 # 1
while x: # 2
    if 1: # 3
        continue
    elif 2: # 4
        break
    print 2 # 5
else:
    print # 6
3 # 7
    """.strip()
    cfg = cfa(ast_utils.parse(t, "test"))
    assert cfg.connects_to == {0: set([1]), 1: set([2]), 2: set([3, 6]), 3: set([2, 4]), 4: set([5, 7]), 5: set([2]), 6: set([7]), 7: set([8])}

    t = """
x = 1 # 1
while 0: # 2
    if 1: # X
        continue
    elif 2: # X
        break
    print 2 # X
else:
    print # 3
3 # 4
    """.strip()
    cfg = cfa(ast_utils.parse(t, "test"))
    assert cfg.connects_to == {0: set([1]), 1: set([2]), 2: set([3]), 3: set([4]), 4: set([5])}

    t = """
x = 1 # 1
while True: # 2
    if 1: # 3
        continue
    elif 2: # 4
        break
    print 2 # 5
else:
    print # X
3 # 6
    """.strip()
    cfg = cfa(ast_utils.parse(t, "test"))
    assert cfg.connects_to == {0: set([1]), 1: set([2]), 2: set([3]), 3: set([2, 4]), 4: set([5, 6]), 5: set([2]), 6: set([7])}

    t = """
x = 1 # 1
for i in [2]: # 2
    if 1: # 3
        continue
    elif 2: # 4
        break
    print 2 # 5
else:
    print # 6
3 # 7
    """.strip()
    cfg = cfa(ast_utils.parse(t, "test"))
    assert cfg.connects_to == {0: set([1]), 1: set([2, 6]), 2: set([3]), 3: set([2, 4, 6]), 4: set([5, 7]), 5: set([2, 6]), 6: set([7]), 7: set([8])}
