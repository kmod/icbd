"""
Testing for loops
"""

def main():
    for i in xrange(3):
        print i
        i = ''
        if i:
            continue
    else:
        print "done"
main()
