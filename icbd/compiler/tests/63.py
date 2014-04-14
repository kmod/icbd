"""
Regression test: interaction between closure-constant-folding, and symbol table propagation to following basic blocks
"""

x = 1
def f():
    x

def g():
    f()

while '':
    pass

f()
x

