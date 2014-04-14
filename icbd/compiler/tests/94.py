"""
collections.deque
"""

def main():
    from collections import deque
    d = deque()
    for i in xrange(25):
        d.append(i)
    print list(d)
    print d.popleft()
    print list(d)

    d.appendleft(55)
    for i in xrange(5):
        print d.pop()
    print list(d)
main()
