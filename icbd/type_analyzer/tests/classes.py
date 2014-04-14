def f1():
    class A(object):
        k = 2
        def __init__(self, x): # 12 (<A|B>,int) -> None
            self.x = x
            self.m = 1
            pass

        def bar(self): # 12 (<A|B>) -> int
            self.y = 2
            return self.x

        def baz(self): # 16 A
            self.z = 1

        def foo(self):
            return 2

    a = A(1) # 4 A # 8 class 'A'
    a2 = A(1)
    f1 = A.foo # 4 (A) -> int
    f2 = a.foo # 4 () -> int
    x1 = f1() # 4 <unknown> # e 9
    x2 = f2() # 4 int
    a2.m # 7 <int|str>
    a.m # 6 <int|str>
    a.m = "" # 6 <int|str>
    a.m # 6 <int|str>
    a2.m # 7 <int|str>
    a2.y # 7 int

    y = a.x # 4 int

    z = a.z # 4 int
    w = a.w # 4 <unknown> # e 8
    y = a.y # 4 int
    z = a.bar() # 4 int
    y = a.y # 4 int


    class B(A):
        pass

    def f(x): # 8 (<A|B>) -> <A|B>
        return x

    b = B(1,2,3) # e 8 # 4 B
    b = B(2) # 4 B

    A.k # 4 class 'A' # 6 int
    a.k # 4 A # 6 int
    B.k # 4 class 'B' # 6 int
    b.k # 4 B # 6 int

    b.y # 6 int

    x = b.bar() # 4 int # 8 B # 10 () -> int

    f(b) # 4 (<A|B>) -> <A|B> # 6 B
    f(a) # 4 (<A|B>) -> <A|B> # 6 A

def f2():
    class LinkedList(object):
        def __init__(self, l):
            if l:
                self.link = LinkedList(l[1:])
                self.val = l[0]
            else:
                self.link = None
                self.val = None
            self.x = 1

    k = LinkedList(range(5))
    k.link
    k.val
    k.x
    x = k.link.link.link.link.link.link.link.link.link.link.link.link.link.link.link.link.link.val # 4 int # 8 LinkedList # 10 LinkedList # 15 LinkedList # 20 LinkedList # 90 LinkedList # 95 int
    y = x # 4 int

def f3():
    class C(object):
        pass

    def ident(self):
        return self

    c = C()
    c2 = C()
    c2.x # 7 int
    c.x = 1 # 6 int

    C.f = ident

    x = c.f() # 4 C

    def ident(self):
        return self

    c.g = ident
    y = c.g() # e 8 # 4 int
    z = c.g(2) # 4 int

def f4():
    " Test class resolution order "
    class X(object):
        a = 1
        b = 1
        c = 1
        d = 1
        def __init__(self): # 21 <X|Y>
            self.a = ""
            self.b = ""

    class Y(X):
        a = object()
        b = object()
        c = object()
        def __init__(self):
            super(Y, self).__init__()
            self.a = [1]

    x = X()
    x.e = 1
    y = Y() # 4 Y
    y.a # 6 <[int]|str>
    y.b # 6 str
    y.c # 6 object
    y.d # 6 int
    y.e # e 4

def f5():
    """
    " test super behavior (also class redefinition) "
    class X(object):
        def __init__(self):
            self.name = "X"

        def get_name(self):
            return self.name

    class Y(X):
        def __init__(self):
            super(Y, self).__init__()
            self.name = 2

    y = Y()
    y.name ! 2 int
    y.a = 1
    x = super(Y, y)
    x.a ! e 0
    x.name ! 2 str
    super(Y, y).name ! 12 str
    " this is probably not going to be supported any time soon "
    '''
    n = super(Y, y).get_name() ! 0 int ! 16 () -> int
    '''
    """

def f6():
    # test __init__ inheritance

    class A(object):
        def __init__(self, x): # 27 int
            self.x = x # 17 int # 21 int

    class B(A):
        pass

    b = B(2) # 4 B
    b.x # 6 int

def f7():
    def A(object):
        pass

    # test that super.__init__ can be called even if it wasnt explicitly defined
    def B(object):
        def __init__(self):
            super(B, self).__init__()

def f8():
    # testing default behavior
    class C(object):
        pass

    c = C() # 4 C
    b = not c # 4 bool
    b = (c == c) # 4 bool
    x = hash(c) # 4 int

def f9():
    i = 0
    class C(object):
        global i

        for i in xrange(3):
            j = i

    c = C()
    print i # 10 int
    print c.j # 10 C # 12 int

def f10():
    class C(object): # 10 class 'C'
        class D(object): # 14 class 'D'
            pass

        def __init__(self):
            self.d = C.D() # 17 D

    c = C() # 4 C
    print c.d # 10 C # 12 D

def f11():
    class C(object):
        cls_arg = 1
        def __init__(self):
            x = cls_arg # e 16
            y = C.cls_arg # 12 int # 18 int

def f12():
    def f(x): # 8 (int) -> str
        return str(x)*2
    class C(object):
        i2 = 1 # 8 int
        j = f(i2) # 8 str
        k = i2 # 8 int

        def __init__(self):
            print i2 # e 18

    print C.i2 # 12 int
    print C.j # 12 str
    print C.k # 12 int

def f13():
    def f():
        pass

    class C(object):
        x = 1 # 8 int
        f()
        x # 8 int

def f14():
    class A(object):
        def bar(self):
            return 1

    class B(object):
        def bar(self):
            return ''

    class C(A, B):
        def bar(self):
            return super(C, self).bar()

    c = C() # 4 C
    x = c.bar() # 4 int

def f15():
    class C(object):
        def bar(*args): # 12 (*[C]) -> [C]
            return args # 19 [C]

    c = C() # 4 C
    l = c.bar() # 4 [C]

def f16():
    # Testing staticmethod behavior
    class C(object):
        @staticmethod
        def foo1(x):
            return x

        @staticmethod
        def foo2(x):
            return x

        def foo3(x):
            return x

    class B(object):
        pass

    B.foo1 = C.foo1
    s = staticmethod(C.foo2)
    B.foo2 = s
    x = B.foo1(B()) # 4 B # 10 (B) -> B
    x = B.foo1(2) # e 8
    y = B.foo2(2) # 4 int # 10 (int) -> int
    b = B()
    f1 = b.foo1 # 4 () -> B
    f2 = b.foo2 # 4 (int) -> int
    b.foo1()
    b.foo2() # e 4

def f17():
    class A(object):
        def __init__(self):
            pass

    class B(A):
        pass

    b = B() # 4 B
    b.__init__() # 4 B # 6 () -> None

    class C(list):
        pass

    c = C()
    x = c.pop() # 4 <mixed>
    c.__init__([1,2])
    c.__init__({1:2})

def f18():
    class A(object):
        def __init__(self): # 21 <A|B>
            self.x = 1

    class B(A):
        def bar(self):
            return self.x # 24 int

    class C(object):
        pass

def f19():
    class C(object):
        a = 1
        def __init__(self):
            print a # e 18

    C()

x20 = 1 # 0 int
def f20():
    x20 = '' # 4 str
    class C(object):
        global x20
        def __init__(self):
            print x20 # 18 str

    return C()

x21 = 1 # 0 int
def f21():
    x21 = 's' # 4 str
    class C(object):
        global x21
        class D(object):
            global x21
            def __init__(self):
                print x21 # 22 str

    return C.D()
