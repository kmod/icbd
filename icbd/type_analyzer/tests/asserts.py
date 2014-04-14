l = []
x = l[0]

y = l[1]
assert isinstance(x, int)
print x # 6 int
print y # 6 <unknown>
if isinstance(y, (str, int)):
    print x # 10 int
    print y # 10 <int|str>
