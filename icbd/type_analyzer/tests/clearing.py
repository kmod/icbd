import MySQLdb
import collections

c = MySQLdb.connect()

f = collections.deque.popleft


# TODO not sure if this should be an error or not
f(None) # e 0
c # 0 MySQLConnection
if 1:
    c # 4 MySQLConnection



x = 1 # 0 int

def g():
    global x
    x = ''

x # 0 int
g()
x # 0 <int|str>

x = '' # 0 str
g()
x # 0 <int|str>


def f():
    global x
    x = 1 # 4 int
    g()
    x # 4 <int|str>

# TODO another test: get a reference to the local scope (ex to the module), and change a local through that
