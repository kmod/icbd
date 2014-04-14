import _ast
import collections
import sys

import cfa

def lineno(node):
    if hasattr(node, "lineno"):
        return "%s:%s" % (node.lineno, node.col_offset)
    return "?:?"

def display_ast(node):
    name = repr(node)
    if isinstance(node, _ast.FunctionDef):
        name = "<FunctionDef %s>" % (node.name,)
    return "%s at %s" % (name, lineno(node))

def node_name(node):
    if isinstance(node, _ast.FunctionDef):
        return "<Func:'%s'>" % (node.name,)
    return type(node).__name__

def crawl_ast(ast, listener, err_missing=False, fn=None, backwards=False):
    # print "crawling %s with listener %s" % (node_name(ast), listener)

    q = collections.deque()
    if isinstance(ast, list):
        if backwards:
            q.extendleft(ast)
        else:
            q.extend(ast)
    else:
        q.append(ast)

    while q:
        assert not None in q, node
        # print
        # print q
        node = q.popleft()
        # print node,
        # if hasattr(node, "lineno"):
            # print node.lineno
        # else:
            # print

        if callable(node):
            add = node()
            if add is not None:
                q.extendleft(add)
            continue

        name = type(node).__name__.lower()
        if err_missing and not hasattr(listener, "pre_%s" % name):
            raise Exception("%s doesn't support '%s' at %s of %s" % (listener, name, lineno(node), fn or "<unknown>"))

        if hasattr(listener, "pre_%s" % name):
            try:
                rtn = getattr(listener, "pre_%s" % name)(node)
            except:
                print "Errored on %s at %s::%s: %s" % (node, fn, lineno(node), format_node(node))
                raise
            if rtn is not None:
                q.extendleft(rtn)
                continue


        added = []
        if isinstance(node, (
                    _ast.Break,
                    _ast.Continue,
                    _ast.Global,
                    _ast.Import,
                    _ast.ImportFrom,
                    _ast.Name,
                    _ast.Num,
                    _ast.Pass,
                    _ast.Str,
                    cfa.Jump,
                    )):
            pass
        elif isinstance(node, cfa.Branch):
            added.append(node.test)
        elif isinstance(node, cfa.HasNext):
            added.append(node.iter)
        elif isinstance(node, (_ast.Expr, _ast.Index)):
            added.append(node.value)
        elif isinstance(node, _ast.Slice):
            if node.upper:
                added.append(node.upper)
            if node.lower:
                added.append(node.lower)
            if node.step:
                added.append(node.step)
        elif isinstance(node, _ast.Return):
            if node.value:
                added.append(node.value)
        elif isinstance(node, _ast.Assert):
            added.append(node.test)
        elif isinstance(node, _ast.ClassDef):
            added.extend(node.body)
            added.extend(node.decorator_list)
            added.extend(node.bases)
        elif isinstance(node, _ast.FunctionDef):
            added.extend(node.body)
            added.extend(node.args.args)
            added.extend(node.decorator_list)
            added.extend(node.args.defaults)
        elif isinstance(node, _ast.Lambda):
            assert isinstance(node.body, _ast.AST)
            added.append(node.body)
        elif isinstance(node, _ast.Module):
            added.extend(node.body)
        elif isinstance(node, _ast.Call):
            if node.starargs:
                added.append(node.starargs)
            if node.kwargs:
                added.append(node.kwargs)
            added.extend(node.keywords)
            added.extend(node.args)
            added.append(node.func)
        elif isinstance(node, _ast.keyword):
            added.append(node.value)
        elif isinstance(node, _ast.Attribute):
            added.append(node.value)
        elif isinstance(node, (_ast.Tuple, _ast.List)) or (sys.version_info >= (2,7) and isinstance(node, _ast.Set)):
            added.extend(node.elts)
        elif isinstance(node, _ast.Dict):
            added.extend(node.keys)
            added.extend(node.values)
        elif isinstance(node, _ast.For):
            added.extend(node.orelse)
            added.extend(node.body)
            added.append(node.target)
            added.append(node.iter)
        elif isinstance(node, _ast.While):
            added.extend(node.orelse)
            added.extend(node.body)
            added.append(node.test)
        elif isinstance(node, _ast.If):
            added.extend(node.orelse)
            added.extend(node.body)
            added.append(node.test)
        elif isinstance(node, _ast.IfExp):
            added.append(node.orelse)
            added.append(node.body)
            added.append(node.test)
        elif isinstance(node, _ast.Compare):
            added.extend(node.comparators)
            added.append(node.left)
        elif isinstance(node, _ast.UnaryOp):
            added.append(node.operand)
        elif isinstance(node, _ast.BinOp):
            added.append(node.right)
            added.append(node.left)
        elif isinstance(node, _ast.BoolOp):
            added.extend(node.values)
        elif isinstance(node, _ast.Raise):
            if node.tback:
                added.append(node.tback)
            if node.type:
                added.append(node.type)
            if node.inst:
                added.append(node.inst)
        elif isinstance(node, _ast.Assign):
            added.extend(node.targets)
            added.append(node.value)
        elif isinstance(node, _ast.AugAssign):
            added.append(node.target)
            added.append(node.value)
        elif isinstance(node, (_ast.GeneratorExp, _ast.ListComp)) or (sys.version_info >= (2,7) and isinstance(node, _ast.SetComp)):
            added.append(node.elt)
            # Make sure generators get hit in the right order
            added.extend(reversed(node.generators))
        elif sys.version_info >= (2,7) and isinstance(node, _ast.DictComp):
            added.append(node.key)
            added.append(node.value)
            # Make sure generators get hit in the right order
            added.extend(reversed(node.generators))
        elif isinstance(node, _ast.comprehension):
            added.append(node.target)
            added.extend(node.ifs)
            added.append(node.iter)
        elif isinstance(node, _ast.Print):
            if node.dest:
                added.append(node.dest)
            added.extend(node.values)
        elif isinstance(node, _ast.Subscript):
            added.append(node.value)
            added.append(node.slice)
        elif isinstance(node, _ast.TryExcept):
            added.extend(node.orelse)
            added.extend(node.handlers)
            added.extend(node.body)
        elif isinstance(node, _ast.TryFinally):
            added.extend(node.finalbody)
            added.extend(node.body)
        elif isinstance(node, _ast.ExceptHandler):
            added.extend(node.body)
            if node.name:
                added.append(node.name)
            if node.type:
                added.append(node.type)
        elif isinstance(node, _ast.Delete):
            added.extend(node.targets)
        elif isinstance(node, _ast.With):
            added.extend(node.body)
            if node.optional_vars:
                added.append(node.optional_vars)
            added.append(node.context_expr)
        elif isinstance(node, _ast.Yield):
            if node.value:
                added.append(node.value)
        elif isinstance(node, _ast.Exec):
            added.append(node.body)
            if node.locals:
                added.append(node.locals)
            if node.globals:
                added.append(node.globals)
        elif isinstance(node, _ast.Repr):
            added.append(node.value)
        elif isinstance(node, _ast.ExtSlice):
            added.extend(reversed(node.dims))
        else:
            raise NotImplementedError("Can't crawl %s at %s" % (node, lineno(node)))
        if backwards:
            q.extendleft(reversed(added))
        else:
            q.extendleft(added)

class _GlobalFinder(object):
    def __init__(self, recursive):
        self.global_names = set()
        self.recursive = recursive

    def pre_global(self, node):
        for n in node.names:
            assert isinstance(n, str)
            self.global_names.add(n)

    def pre_functiondef(self, node):
        if self.recursive:
            return None
        return ()

    def pre_classdef(self, node):
        if self.recursive:
            return None
        return ()

def find_global_vars(node, recursive=False):
    assert recursive or isinstance(node, (_ast.FunctionDef, _ast.ClassDef))

    finder = _GlobalFinder(recursive)
    crawl_ast(node.body, finder)
    return finder.global_names

class _YieldFinder(object):
    def __init__(self):
        self.found = False

    def pre_yield(self, node):
        self.found = True
        return ()

    def pre_functiondef(self, node):
        return ()

    def pre_classdef(self, node):
        return ()

def has_yields(func):
    assert isinstance(func, _ast.FunctionDef)

    finder = _YieldFinder()
    crawl_ast(func.body, finder)
    return finder.found

class _FunctionFinder(object):
    def __init__(self, skip_control_flow=False):
        self.functions = []
        self.skip_control_flow = skip_control_flow

    def pre_functiondef(self, node):
        self.functions.append(node)
        return ()

    def pre_if(self, node):
        if self.skip_control_flow:
            return ()

    def pre_for(self, node):
        if self.skip_control_flow:
            return ()

    def pre_while(self, node):
        if self.skip_control_flow:
            return ()

def find_functions(node, skip_control_flow=False):
    assert isinstance(node, (_ast.FunctionDef, _ast.Module, _ast.ClassDef)), node

    finder = _FunctionFinder(skip_control_flow)
    crawl_ast(node.body, finder)
    return finder.functions

class _NameFinder(object):
    def __init__(self, recursive):
        self.names = []
        self.recursive = recursive

    def pre_name(self, node):
        self.names.append(node)

    def pre_functiondef(self, node):
        if self.recursive:
            return None
        return ()

    def pre_classdef(self, node):
        if self.recursive:
            return None
        return ()

def find_names(node, recursive=False):
    finder = _NameFinder(recursive)
    crawl_ast(node, finder)
    return finder.names

def est_expr_length(e):
    if isinstance(e, _ast.Num):
        return len(str(e.n))
    if isinstance(e, _ast.Name):
        return len(e.id)
    if isinstance(e, _ast.Call):
        t = est_expr_length(e.func)
        for a in e.args:
            t += 1 + est_expr_length(a)
        return t + 1
    if isinstance(e, _ast.Subscript):
        return 2 + est_expr_length(e.value) + est_expr_length(e.slice)
    if isinstance(e, _ast.Attribute):
        return 1 + est_expr_length(e.value) + len(e.attr)
    if isinstance(e, _ast.Index):
        return est_expr_length(e.value)
    if isinstance(e, _ast.List) or (sys.version_info >= (2,7) and isinstance(e, _ast.Set)):
        t = 1
        for a in e.elts:
            t += 1 + est_expr_length(a)
        return t
    if isinstance(e, _ast.Dict):
        t = 1
        for k in e.keys:
            t += est_expr_length(k) + 1
        for v in e.values:
            t += est_expr_length(v) + 1
        return t
    if isinstance(e, _ast.Str):
        return 2 + len(e.s)
    if isinstance(e, _ast.Slice):
        t = 1
        if e.lower:
            t += est_expr_length(e.lower)
        if e.upper:
            t += est_expr_length(e.upper)
        return t
    if isinstance(e, _ast.BinOp):
        # return est_expr_length(e.left) + 1 + est_expr_length(e.right)
        # hax: e.col_offset for a binop is actually the location of the operator
        return est_expr_length(e.right)
    if isinstance(e, _ast.Tuple):
        t = 1
        for e in e.elts:
            t += 1 + est_expr_length(e)
        return t
    if isinstance(e, _ast.Compare):
        r = est_expr_length(e.left)
        for sub in e.comparators:
            r += 1 + est_expr_length(sub)
        return r
    if isinstance(e, _ast.IfExp):
        return len(" if  else ") + est_expr_length(e.test) + est_expr_length(e.body) + est_expr_length(e.orelse)
    if isinstance(e, _ast.Lambda):
        return len("lambda:") + est_expr_length(e.body)
    if isinstance(e, _ast.BoolOp):
        return len(e.values) - 1 + sum(est_expr_length(e2) for e2 in e.values)
    if isinstance(e, (_ast.GeneratorExp, _ast.ListComp)) or (sys.version_info >= (2,7) and isinstance(e, _ast.SetComp)):
        # don't necessarily need parens, if it's implicit in a function call
        # TODO add e.generators
        return len(" for  in ") + est_expr_length(e.elt)
    if sys.version_info >= (2,7) and isinstance(e, _ast.DictComp):
        return len(": for  in ") + est_expr_length(e.key) + est_expr_length(e.value)
    if isinstance(e, _ast.UnaryOp):
        return 1 + est_expr_length(e.operand)
    if isinstance(e, _ast.ExtSlice):
        return 1 + len(e.dims) + sum(map(est_expr_length, e.dims))
    raise NotImplementedError(e)

_parse_cache = {}
def parse(s, fn):
    import os
    k = (s, os.path.abspath(fn))
    if k not in _parse_cache:
        r = compile(s, fn, "exec", _ast.PyCF_ONLY_AST)
        assert isinstance(r, _ast.Module)
        _parse_cache[k] = r
    return _parse_cache[k]

def format_node(node):
    if isinstance(node, _ast.Name):
        return node.id
    elif isinstance(node, _ast.Call):
        return format_node(node.func) + "(%s)" % (", ".join(format_node(a) for a in node.args))
    elif isinstance(node, _ast.Attribute):
        return "%s.%s" % (format_node(node.value), node.attr)
    elif isinstance(node, cfa.HasNext):
        return "__has_next__(%s)" % format_node(node.iter)
    elif isinstance(node, _ast.Assign):
        r = ""
        for t in node.targets:
            r += "%s = " % format_node(t)
        return r + format_node(node.value)
    elif isinstance(node, cfa.Jump):
        return "goto %d" % node.block_id
    elif isinstance(node, cfa.Branch):
        return "goto %d if %s else goto %d" % (node.true_block, format_node(node.test), node.false_block)
    elif isinstance(node, _ast.Print):
        return "print %s" % ', '.join(format_node(v) for v in node.values)
    elif isinstance(node, _ast.Str):
        return repr(node.s)
    elif isinstance(node, _ast.Num):
        return str(node.n)
    elif isinstance(node, _ast.Expr):
        return format_node(node.value)
    elif isinstance(node, _ast.Compare):
        s = format_node(node.left)
        ops = {
                _ast.Lt : '<',
                _ast.LtE : '<=',
                _ast.Gt : '>',
                _ast.GtE : '>=',
                _ast.Eq : '==',
                _ast.NotEq : '!=',
                _ast.Is : 'is',
                _ast.IsNot : 'is not',
                _ast.In : 'in',
                _ast.NotIn : 'not in',
              }
        for i in xrange(len(node.ops)):
            s += " %s %s" % (ops[type(node.ops[i])], format_node(node.comparators[i]))
        return s
    elif isinstance(node, _ast.AugAssign):
        ops = {
                _ast.Add : '+=',
                _ast.Sub : '-=',
                _ast.Mult : '*=',
                _ast.Mod : '%=',
                _ast.Pow : '**=',
                _ast.Div : '/=',
              }
        return "%s %s %s" % (format_node(node.target), ops[type(node.op)], format_node(node.value))
    elif isinstance(node, _ast.BinOp):
        ops = {
                _ast.Add : '+',
                _ast.Sub : '-',
                _ast.Mult : '*',
                _ast.Mod : '%',
                _ast.Pow : '**',
                _ast.Div : '/',
                _ast.LShift : '<<',
                _ast.RShift : '>>',
                _ast.BitAnd : '&',
                _ast.BitOr : '|',
                _ast.BitXor : '^',
              }
        return "%s %s %s" % (format_node(node.left), ops[type(node.op)], format_node(node.right))
    elif isinstance(node, _ast.FunctionDef):
        return "def %s" % (node.name,)
    elif isinstance(node, _ast.Return):
        return "return %s" % format_node(node.value)
    elif isinstance(node, _ast.BoolOp):
        ops = {
                _ast.And: "and",
                _ast.Or: "or",
              }
        op_s = " %s " % (ops[type(node.op)],)
        return op_s.join(format_node(a) for a in node.values)
    elif isinstance(node, _ast.Tuple):
        return "(...)"
    elif isinstance(node, _ast.List):
        return "[%s]" % ", ".join(format_node(e) for e in node.elts)
    elif isinstance(node, _ast.Dict):
        return "{%s}" % ", ".join("%s:%s" % (format_node(k), format_node(v)) for k,v in zip(node.keys, node.values))
    elif isinstance(node, _ast.Subscript):
        return "%s[%s]" % (format_node(node.value), format_node(node.slice))
    elif isinstance(node, _ast.Index):
        return format_node(node.value)
    elif isinstance(node, _ast.Pass):
        return "pass"
    elif isinstance(node, _ast.Import):
        return "import ..."
    elif isinstance(node, _ast.ClassDef):
        return "classdef " + node.name
    elif isinstance(node, _ast.UnaryOp):
        if isinstance(node.op, _ast.USub):
            return '-' + format_node(node.operand)
        if isinstance(node.op, _ast.Not):
            return 'not ' + format_node(node.operand)
        raise Exception(node.op)
    else:
        return str(node)

