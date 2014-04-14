"""
Interesting case: dict.get, where the value passed into the get isn't necessarily exactly the same as the valuetype of the dict
"""

def main():
    d = {1:[123]}

    for i in xrange(5):
        print i
        l = d.get(i, d)
        for j in l:
            print j
        print
main()

