from ast_utils import parse

test_1 = "def f():\n return 1"
test_2 = "def f(x):\n if x:\n  r=1\n else:\n  r=0\n return r"
test_2 = "def f(x):\n global r\n if x:\n  r=1\n else:\n  r=0\n return r"
test_2 = "def f(x):\n ''.lower()"

def show(ast):
    if isinstance(ast, list):
        print ast
        return
    print str(type(ast)), dict([(k,type(getattr(ast,k))) for k in dir(ast) if not k.startswith("_")])

"""
<class '_ast.alias'> {'name': <type 'str'>, 'asname': <type 'str'>}
- asname can also be None
<class '_ast.arguments'> {'args': <type 'list'>, 'kwarg': <type 'NoneType'>, 'defaults': <type 'list'>, 'vararg': <type 'NoneType'>}
<class '_ast.Assert'> {'msg': <type 'NoneType'>, 'test': <class '_ast.Name'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.Assign'> {'value': <class '_ast.Num'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'targets': <type 'list'>}
<class '_ast.Attribute'> {'value': <class '_ast.Str'>, 'ctx': <class '_ast.Load'>, 'attr': <type 'str'>, 'col_offset': <type 'int'>, 'lineno': <type 'int'>}
<class '_ast.AugAssign'> {'value': <class '_ast.Num'>, 'target': <class '_ast.Name'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'op': <class '_ast.Add'>}
<class '_ast.BinOp'> {'op': <class '_ast.Pow'>, 'right': <class '_ast.Num'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'left': <class '_ast.Num'>}
<class '_ast.BoolOp'> {'values': <type 'list'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'op': <class '_ast.And'>}
<class '_ast.Call'> {'col_offset': <type 'int'>, 'starargs': <type 'NoneType'>, 'args': <type 'list'>, 'lineno': <type 'int'>, 'func': <class '_ast.Name'>, 'kwargs': <type 'NoneType'>, 'keywords': <type 'list'>}
- args is a list of values (ex Num)
- keywords is a list of _ast.keyword; no overlap with args
<class '_ast.ClassDef'> {'body': <type 'list'>, 'decorator_list': <type 'list'>, 'name': <type 'str'>, 'col_offset': <type 'int'>, 'bases': <type 'list'>, 'lineno': <type 'int'>}
- body is a list of FunctionDef, etc
<class '_ast.Compare'> {'ops': <type 'list'>, 'comparators': <type 'list'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'left': <class '_ast.Num'>}
- ops is a list of Lt/Gt/etc
- comparators is a list of values (ex: Num)
<class '_ast.comprehension'> {'target': <class '_ast.Name'>, 'iter': <class '_ast.List'>, 'ifs': <type 'list'>}
<class '_ast.Delete'> {'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'targets': <type 'list'>}
<class '_ast.Dict'> {'keys': <type 'list'>, 'values': <type 'list'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.DictComp'> {'value': <class '_ast.Name'>, 'generators': <type 'list'>, 'key': <class '_ast.Name'>, 'col_offset': <type 'int'>, 'lineno': <type 'int'>}
<class '_ast.Exec'> {'body': <class '_ast.Str'>, 'globals': <type 'NoneType'>, 'locals': <type 'NoneType'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.ExceptHandler'> {'body': <type 'list'>, 'type': <class '_ast.Name'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'name': <type 'NoneType'>}
- type can be 'None' which is a bare 'except:'
<class '_ast.ExtSlice'> {'dims': <type 'list'>}
- dims is a list of Slice or Index objects
<class '_ast.Expr'> {'value': <class '_ast.Call'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.For'> {'body': <type 'list'>, 'target': <class '_ast.Name'>, 'col_offset': <type 'int'>, 'iter': <class '_ast.Call'>, 'lineno': <type 'int'>, 'orelse': <type 'list'>}
<class '_ast.FunctionDef'> {'body': <type 'list'>, 'decorator_list': <type 'list'>, 'name': <type 'str'>, 'col_offset': <type 'int'>, 'args': <class '_ast.arguments'>, 'lineno': <type 'int'>}
<class '_ast.GeneratorExp'> {'generators': <type 'list'>, 'elt': <class '_ast.Num'>, 'col_offset': <type 'int'>, 'lineno': <type 'int'>}
- elt is the first thing in the expression, ie the thing that will be evaluated multiple times
- generators is a list of comprehension objects
<class '_ast.Global'> {'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'names': <type 'list'>}
<class '_ast.If'> {'body': <type 'list'>, 'test': <class '_ast.Name'>, 'orelse': <type 'list'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.IfExp'> {'body': <class '_ast.Num'>, 'test': <class '_ast.Num'>, 'orelse': <class '_ast.Num'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.Import'> {'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'names': <type 'list'>}
- names is a list of alias objects
<class '_ast.ImportFrom'> {'module': <type 'str'>, 'names': <type 'list'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'level': <type 'int'>}
- names is a list of alias objects
<class '_ast.Index'> {'value': <class '_ast.Num'>}
<class '_ast.keyword'> {'value': <class '_ast.Num'>, 'arg': <type 'str'>}
<class '_ast.Lambda'> {'body': <class '_ast.Name'>, 'args': <class '_ast.arguments'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.List'> {'elts': <type 'list'>, 'ctx': <class '_ast.Load'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.ListComp'> {'generators': <type 'list'>, 'elt': <class '_ast.Name'>, 'col_offset': <type 'int'>, 'lineno': <type 'int'>}
- see notes for GeneratorExp
<class '_ast.Module'> {'body': <type 'list'>}
<class '_ast.Num'> {'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'n': <type 'int'>}
<class '_ast.Name'> {'ctx': <class '_ast.Load'>, 'id': <type 'str'>, 'col_offset': <type 'int'>, 'lineno': <type 'int'>}
<class '_ast.Name'> {'ctx': <class '_ast.Store'>, 'id': <type 'str'>, 'col_offset': <type 'int'>, 'lineno': <type 'int'>}
<class '_ast.Pass'> {'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.Pow'> {}
<class '_ast.Print'> {'dest': <type 'NoneType'>, 'values': <type 'list'>, 'nl': <type 'bool'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.Raise'> {'tback': <type 'NoneType'>, 'type': <class '_ast.Name'>, 'inst': <type 'NoneType'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.Repr'> {'value': <class '_ast.Num'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.Return'> {'value': <class '_ast.Name'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.Set'> {'elts': <type 'list'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.Slice'> {'upper': <class '_ast.Num'>, 'lower': <class '_ast.Num'>, 'step': <type 'NoneType'>}
- they can all be None
<class '_ast.Str'> {'s': <type 'str'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.Subscript'> {'value': <class '_ast.List'>, 'slice': <class '_ast.Index'>, 'ctx': <class '_ast.Load'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.TryExcept'> {'body': <type 'list'>, 'orelse': <type 'list'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'handlers': <type 'list'>}
- handlers is a list of ExceptHandler
<class '_ast.TryFinally'> {'body': <type 'list'>, 'finalbody': <type 'list'>, 'col_offset': <type 'int'>, 'lineno': <type 'int'>}
<class '_ast.Tuple'> {'elts': <type 'list'>, 'ctx': <class '_ast.Load'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.UnaryOp'> {'operand': <class '_ast.Name'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>, 'op': <class '_ast.USub'>}
<class '_ast.While'> {'body': <type 'list'>, 'test': <class '_ast.Num'>, 'orelse': <type 'list'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
<class '_ast.With'> {'body': <type 'list'>, 'optional_vars': <type 'NoneType'>, 'context_expr': <class '_ast.Name'>, 'col_offset': <type 'int'>, 'lineno': <type 'int'>}
- optional_vars can be a name that it gets with'd as
- context_expr is the with object
<class '_ast.Yield'> {'value': <class '_ast.Num'>, 'lineno': <type 'int'>, 'col_offset': <type 'int'>}
- Yield is an expression??
"""

ast1 = parse(test_1, "text").body[0]
ast2 = parse(test_2, "text").body[0]
show(parse("""
global a
""".strip(), "text").body[0].names)
