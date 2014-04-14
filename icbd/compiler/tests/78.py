"""
test to make sure that types can be deeply nested
"""

t1 = (1, "hello", [])
t2 = (t1, t1)
t3 = (t2, t2)
t4 = (t3, t3)
t5 = (t4, t4)
t6 = (t5, t5)
t7 = (t6, t6)
t8 = (t7, t7)
t9 = (t8, t8)
t10 = (t9, t9)
t11 = (t10, t10)
t12 = (t11, t11)
