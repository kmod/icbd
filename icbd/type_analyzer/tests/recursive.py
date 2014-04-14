l = [] # 0 @1[1]
l.append(l)

def f(l):
    return f([l])

f(1)

while f:
    l = [l]
