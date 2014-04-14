l = []
for i in xrange(65, 90):
    l.append(chr(i))
for i in xrange(97, 123):
    l.append(chr(i))

idx1 = 0
idx2 = 1
for it in xrange(10000000):
    # l[idx1] += l[idx2]
    if it % 16 == 0:
        l[idx1] = " "
    else:
        l[idx1] = l[idx1] + l[idx2]
    idx1 = (idx1 + 3 * idx2 + it) % len(l)
    idx2 = (idx2 * 2 + idx1 + 3) % len(l)

for i in xrange(len(l)):
    print i, l[i]

