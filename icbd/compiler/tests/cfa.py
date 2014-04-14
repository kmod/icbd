def isprime(x):
    #0
    for i in xrange(2, x): #1
        if i * i > x: #2
            break
        if x % i == 0: #3
            return True #4
    return False #5

def f1(x):
    r = 0 #0
    while x: #1
        r = r * 2 + 1 #2
        x -= 1
    return r

def f2():
    # a = 1
    if 1:
        for i in xrange(2):
            print i
        # print i
        while True:
            print 'x'

def f3():
    i = ""
    for i in xrange(0):
        print i
    return i

y=1
def test():
    z = 1
    def f4(x):
        return x + y + z
    f4(1)

(i*2 for i in xrange(2))
print i

# def inv(x):
    # try:
        # return 1.0 / x
    # except ZeroDivisionError:
        # return float('nan')


