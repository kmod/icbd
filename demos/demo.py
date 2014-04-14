if 0:
                                                        ""
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        # Basic type analysis:
                                                        a = 2
                                                        b = '3'
                                                        d = {a:b}
                                                        ch = ord(b[2].lower()[0])
                                                        print ch
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        




                                                        
                                                        
                                                        
                                                        
                                                        # Name errors:
                                                        ch *= e
                                                        




                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        # Nested-type manipulation:
                                                        d = {1:[1], 3:[4]}
                                                        d[1].append(2)
                                                        
                                                        l = [range(i) for i in xrange(5)]
                                                        l.append([-1])
                                                        l2 = [k[0] for k in l]
                                                        l2.append(1)
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        




                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        # Function type inference:
                                                        def func(x, y):
                                                            return b * (x + y)
                                                        r = func(3, 4)
                                                        
                                                        
                                                        
                                                        
                                                        




                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        # Higher-level types:
                                                        def f(x):
                                                            def g():
                                                                return x
                                                            return g
                                                        
                                                        inner = f(2)
                                                        print f(1)() + inner()
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        




                                                        
                                                        
                                                        # Control-flow analysis:
                                                        if inner():
                                                            x = 3
                                                        else:
                                                            x = [0]
                                                        print l2[x]
                                                        
                                                        def fib(x):
                                                            if x <= 1:
                                                                return x
                                                            return fib(x-1) + fib(x-2)
                                                        fib(2)
                                                        
                                                        
                                                        




                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        def foo():
                                                            return foo()
                                                        if 0:
                                                            x = 0
                                                        else:
                                                            x = foo()
                                                        print x
                                                        
                                                        
                                                        
                                                        




                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        # Classes:
                                                        class C(object):
                                                            def __init__(self, x):
                                                                self.x = x
                                                            def bar(self, z):
                                                                return self.x * z
                                                            def baz(self, k):
                                                                return k**2
                                                        
                                                        c = C(2)
                                                        c.baz(3)
                                                        
                                                        
                                                        
                                                        




                                                        
                                                        
                                                        # attributes
                                                        print c.x
                                                        z = c.bar(3)
                                                        c.y = 3
                                                        z = c.x * c.y
                                                        z *= c.z
                                                        
                                                        
                                                        




                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        # Complex type analysis:
                                                        def f1(x):
                                                            def g(y):
                                                                return x * y
                                                            return g
                                                        
                                                        a = f1('')
                                                        b = a(2)
                                                        
                                                        def f2(x):
                                                            def g(y):
                                                                return x * y
                                                            return g
                                                        
                                                        a = f2(1)
                                                        b = a(2)






                                                        ""
