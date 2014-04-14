"""
list iterators
"""

for i in [[1, 2]]:
    print ''
    print i

def main():
    it = [[]].__iter__

    print 1
    it = it()
    print 2
    print it.next()
    it = 3
    print 3
main()
