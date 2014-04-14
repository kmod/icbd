def f1():
    class C(object):
        __a = 1
        def __init__(self):
            self.__b = ''

        def bar(self):
            print self.__a # 23 int
            print self.__c # e 18

    c = C()

    C.__c = True
    c.__d = []

    def foo(self):
        print self.__c # 19 bool
        print self.__a # e 14

    C.foo = foo
    c.foo()

    c.__a # e 4
    c.__b # e 4
    c.__c # 6 bool
    c.__d # 6 [<unknown>]

    c._C__a # 6 int
    c._C__b # 6 str
    c._C__c # e 4
    c._C__d # e 4

class C(object):
    global __a
    __a = 1

__a # e 0
_C__a # 0 int

def f3():
    class C(object):
        __a = 1
        def foo(self, __b):
            __b

        def bar(self):
            self.foo(__b=1) # e 12

def f4():
    class C(object):
        def __foo(self):
            pass

        def bar(self):
            self.__foo()

    c = C()
    c.__foo() # e 4
    c._C__foo()
