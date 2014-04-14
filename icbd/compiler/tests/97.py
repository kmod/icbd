"""
recursive boxing
"""

def gimme_int_iterable(container):
    for i in container:
        print i, i+1, i**2

gimme_int_iterable([1, 2, 3])
gimme_int_iterable({5:[], 9:[1,2]})
