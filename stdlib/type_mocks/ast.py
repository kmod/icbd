class AST(object):
    pass

class Module(object):
    def __init__(self):
        self.body = [AST()]

class Add(AST):
    pass
class Sub(AST):
    pass
class Div(AST):
    pass
class Mult(AST):
    pass
class Mod(AST):
    pass
class Pow(AST):
    pass

def parse(s, fn=''):
    return Module()
