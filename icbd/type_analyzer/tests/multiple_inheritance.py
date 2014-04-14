def f1():
    class A(object):
        pass

    class B(A):
        pass

    " Invalid mro:"
    class C(A,B): # e 4
        pass

def f2():
    class A(object):
        w = ''
        x = ''
        y = ''
        z = ''

    class B(A):
        y = 1
        z = 1

    class C(A):
        x = True
        y = True
        z = True

    class D(B, C):
        z = None

    o = D()
    o.w # 6 str

    " This is the hard one: if the MRO was D B A C A, it would get str instead of bool "
    o.x # 6 bool
    o.y # 6 int
    o.z # 6 None
