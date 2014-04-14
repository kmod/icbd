"""
string test
"""

s = ""
for i in xrange(10):
    s += " 5"
print s

def ident(s):
    return s
def double(s):
    return s + s
print double("hello"), ident("world")

def callit(f):
    return f("hello")
print callit("world ".__add__)

l = ["hi"]
while len(l) < 10:
    l.append(l[-1] + "i")

for i in xrange(len(l)):
    print i, l[i]

def get_space():
    return " "
print "hello" + get_space() + "world"

