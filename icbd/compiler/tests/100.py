"""
Difficult recursive boxing case
"""

class IntNode(object):
    def __init__(self, i, next):
        self.i = i
        self.next = next

    def val(self):
        return self.i

    def get_next(self):
        return self.next

class StrNode(object):
    def __init__(self, s, next):
        self.s = s
        self.next = next

    def val(self):
        return self.s

    def get_next(self):
        return self.next

def print_nodes(cur):
    i = 0
    while cur is not None:
        print cur.val()
        cur = cur.get_next()
        i += 1
        if i >= 100:
            print "loop!"
            break

n = None
for i in xrange(10):
    n = IntNode(i, n)
print_nodes(n)

print_nodes(StrNode("hello", StrNode("world", None)))

# An example where recursively-boxing fields  would cause major issues:
n1 = IntNode(100, None)
n2 = IntNode(101, None)
n1.next = n2
n2.next = n1
print_nodes(n1)
