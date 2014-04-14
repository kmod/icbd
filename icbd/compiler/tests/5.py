"""
Putting it together: finding the sum of all primes less than 10k
"""

total = 0
for i in xrange(2, 10000):
    j = 2
    while j * j <= i:
        if i % j == 0:
            break
        j = j + 1
    else:
        total = total + i
print total
