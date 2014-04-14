"""
finding the sum of all primes less than 1M
"""

total = 0
for i in xrange(2, 1000000):
    j = 2
    while j * j <= i:
        if i % j == 0:
            break
        j = j + 1
    else:
        total = total + i
print total
