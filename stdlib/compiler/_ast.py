class AST(object):
    def __init__(self):
        self.lineno = -1
        self.col_offset = -1

class alias(AST):
    pass

class arguments(AST):
    pass

class boolop(AST):
    pass

class cmpop(AST):
    pass

class excepthandler(AST):
    pass

class expr(AST):
    pass

class expr_context(AST):
    pass

class keyword(AST):
    def __init__(self):
        self.value = expr()
        self.arg = ""

class mod(AST):
    pass

class operator(AST):
    pass

class slice(AST):
    pass

class stmt(AST):
    pass

class unaryop(AST):
    pass

class comprehension(AST):
    def __init__(self):
        self.target = self.iter = expr()
        self.ifs = [expr()]



class Add(operator):
    pass

class And(boolop):
    pass

class Assert(stmt):
    def __init__(self):
        self.test = self.msg = expr()

class Assign(stmt):
    def __init__(self):
        self.value = expr()
        self.targets = [expr()]

class Attribute(expr):
    def __init__(self):
        self.value = expr()
        self.ctx = expr_context()
        self.attr = ""

class AugAssign(stmt):
    def __init__(self):
        self.target = self.value = expr()
        self.op = operator()

class AugLoad(expr_context):
    pass

class AugStore(expr_context):
    pass

class BinOp(expr):
    def __init__(self):
        self.op = operator()
        self.left = self.right = expr()

class BitAnd(operator):
    pass

class BitOr(operator):
    pass

class BitXor(operator):
    pass

class BoolOp(expr):
    def __init__(self):
        self.values = [expr()]
        self.op = boolop()

class Break(stmt):
    pass

class Call(expr):
    def __init__(self):
        self.func = expr()
        self.starargs = expr()
        self.args = [expr()]
        self.kwargs = expr()
        self.keywords = [keyword()]

class ClassDef(stmt):
    def __init__(self):
        self.decorator_list = [expr()]
        self.name = ''
        self.bases = [expr()]
        self.body = [stmt()]

class Compare(expr):
    def __init__(self):
        self.ops = [cmpop()]
        self.comparators = [expr()]
        self.left = expr()

class Continue(stmt):
    pass

class Del(expr_context):
    pass

class Delete(stmt):
    def __init__(self):
        self.targets = [expr()]

class Dict(expr):
    def __init__(self):
        self.keys = self.values = [expr()]

class Div(operator):
    pass

class Ellipsis(slice):
    pass

class Eq(cmpop):
    pass

class ExceptHandler(excepthandler):
    def __init__(self):
        self.body = [stmt()]
        self.type = expr()
        self.name = expr() # Name()?

class Exec(stmt):
    def __init__(self):
        self.body = self.globals = self.locals = expr()

class Expr(stmt):
    def __init__(self):
        self.value = expr()

class Expression(mod):
    pass

class ExtSlice(slice):
    def __init__(self):
        self.dims = [slice()]

class FloorDiv(operator):
    pass

class For(stmt):
    def __init__(self):
        self.iter = expr()
        self.orelse = self.body = [stmt()]
        self.target = expr()

class FunctionDef(stmt):
    def __init__(self):
        self.name = ""
        self.body = [stmt()]
        self.decorator_list = [expr()]
        self.args = arguments()

class GeneratorExp(expr):
    def __init__(self):
        self.generators = [comprehension()]
        self.elt = expr()

class Global(stmt):
    def __init__(self):
        self.names = ['']

class Gt(cmpop):
    pass

class GtE(cmpop):
    pass

class If(stmt):
    def __init__(self):
        self.test = expr()
        self.body = [stmt()]
        self.orelse = [stmt()]

class IfExp(expr):
    def __init__(self):
        self.test = self.body = self.orelse = expr()

class Import(stmt):
    def __init__(self):
        self.names = [alias()]

class ImportFrom(stmt):
    def __init__(self):
        self.module = ''
        self.level = 0
        self.names = [alias()]

class In(cmpop):
    pass

class Index(slice):
    def __init__(self):
        self.value = expr()

class Interactive(mod):
    pass

class Invert(unaryop):
    pass

class Is(cmpop):
    pass

class IsNot(cmpop):
    pass

class LShift(operator):
    pass

class Lambda(expr):
    def __init__(self):
        self.body = expr()

class List(expr):
    def __init__(self):
        self.elts = [expr()]
        self.ctx = expr_context()

class ListComp(expr):
    def __init__(self):
        self.generators = [comprehension()]
        self.elt = expr()

class Load(expr_context):
    pass

class Lt(cmpop):
    pass

class LtE(cmpop):
    pass

class Mod(operator):
    pass

class Module(mod):
    def __init__(self):
        self.body = [stmt()]

class Mult(operator):
    pass

class Name(expr):
    def __init__(self):
        self.id = ""
        self.ctx = expr_context()

class Not(unaryop):
    pass

class NotEq(cmpop):
    pass

class NotIn(cmpop):
    pass

class Num(expr):
    def __init__(self):
        self.n = 0

class Or(boolop):
    pass

class Param(expr_context):
    pass

class Pass(stmt):
    pass

class Pow(operator):
    pass

class Print(stmt):
    def __init__(self):
        self.dest = expr()
        self.values = [expr()]
        self.nl = True

PyCF_ONLY_AST = 1024

class RShift(operator):
    pass

class Raise(stmt):
    def __init__(self):
        self.tback = self.type = self.inst = expr()

class Repr(expr):
    def __init__(self):
        self.value = expr()

class Return(stmt):
    def __init__(self):
        self.value = expr()

class Slice(slice):
    def __init__(self):
        self.upper = self.lower = self.step = expr()

class Store(expr_context):
    pass

class Str(expr):
    def __init__(self):
        self.s = ''

class Sub(operator):
    pass

class Subscript(expr):
    def __init__(self):
        self.value = self.slice = expr()
        self.ctx = expr_context()

class Suite(mod):
    pass

class TryExcept(stmt):
    def __init__(self):
        self.body = self.orelse = [stmt()]
        self.handlers = [ExceptHandler()]

class TryFinally(stmt):
    def __init__(self):
        self.body = self.finalbody = [stmt()]

class Tuple(expr):
    def __init__(self):
        self.elts = [expr()]
        self.ctx = expr_context()

class UAdd(unaryop):
    pass

class USub(unaryop):
    pass

class UnaryOp(expr):
    def __init__(self):
        self.operand = expr()
        self.op = unaryop()

class While(stmt):
    def __init__(self):
        self.test = expr()
        self.body = [stmt()]
        self.orelse = [stmt()]

class With(stmt):
    def __init__(self):
        self.body = [stmt()]
        self.optional_vars = expr()
        self.context_expr = expr()

class Yield(expr):
    def __init__(self):
        self.value = expr()

