"""
Closure refcounting 2 -- hard version
"""

def cycle_test(x):
    def inner(n):
        if n <= 0:
            return 0
        return inner(n - x) + 1
    return inner(100)
print cycle_test(3)
