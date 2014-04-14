x = 1 # 0 int
y = 1 # 0 int
z = x + y # 0 int
z = x - y # 0 int
z = x * y # 0 int
z = x / y # 0 int
z = x // y # 0 int
z = x % y # 0 int
z = x ** y # 0 int
z = x & y # 0 int
z = x ^ y # 0 int
z = x | y # 0 int
z = x << y # 0 int
z = x >> y # 0 int

z += y # 0 int
z -= y # 0 int
z *= y # 0 int
z /= y # 0 int
z //= y # 0 int
z %= y # 0 int
z **= y # 0 int
z &= y # 0 int
z ^= y # 0 int
z |= y # 0 int
z <<= y # 0 int
z >>= y # 0 int

z = -x # 0 int
z = +x # 0 int
z = ~x # 0 int
b = not x # 0 bool
b = x in [] # 0 bool # e 4
b = 1 in [1] # 0 bool

z = abs(x) # 0 int
z = complex(x) # 0 float
z = long(x) # 0 int
z = int(x) # 0 int
z = float(x) # 0 float
z = oct(x) # 0 str
z = hex(x) # 0 str
z = repr(x) # 0 str
z = str(x) # 0 str

b = x < y # 0 bool
b = x <= y # 0 bool
b = x > y # 0 bool
b = x >= y # 0 bool
b = x == y # 0 bool
b = x != y # 0 bool
b = x is y # 0 bool
b = x is not y # 0 bool

s = '' # 0 str
r = '' # 0 str
t = s + r # 0 str
t = s % r # 0 str
t = s * x # 0 str
t = s % x # 0 str
t = s % (x,) # 0 str
t = s % (r,) # 0 str
t = s % (x,r) # 0 str
b = r in s # 0 bool
b = not s # 0 bool

1 < "" # e 0
1 == ""
1 is ""

l1 = [1, 2] # 0 [int]
l2 = [1, ''] # 0 [<int|str>]
l3 = ['', ''] # 0 [str]
l = l1 + l1 # 0 [int]
l = l1 + l2 # 0 [<int|str>]
l = l1 + l3 # 0 [<int|str>]
l = l2 + l2 # 0 [<int|str>]
l = l3 + l3 # 0 [str]
l = l3 + l3 # 0 [<int|str>]
l.append(1) # 0 [<int|str>]
