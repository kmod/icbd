from __future__ import absolute_import

# Debug level.  0 is no debug, 1 is basic debugging, 2 is complex invariant checking
DEBUG = 1
ITERATIONS = 1
PRETTY_DISPLAY = 1
GENERATE_IMPORT_ERRS = 0
VERBOSE = 1

import _ast
import collections
import glob
import hashlib
import heapq
import os.path
import time
import traceback
import sys
import random
import re

from icbd.util.graph_utils import get_scc
from icbd.util.graph_tests import test_scc
from icbd.type_analyzer.visualizer.annotate import annotate

from icbd.util import ast_utils
from icbd.type_analyzer.builtins import (
        BUILTINS,
        KNOWN_MODULES,
        get_instance_type,
        SetClass,
        )
from icbd.util import cfa

from icbd.type_analyzer.type_system import (
        Union,

        Type,
        TopType, TOP,
        FloatType, FLOAT,
        IntType, INT,
        StrType, STR,
        NoneType, NONE,
        SliceType, SLICE,
        BoolType, BOOL,

        get_iter_type,
        has_params,

        Param,
        InstanceType,
        ClassType,
        InstanceMethod,

        ObjectClass,
        Iterable,
        GeneratorClass,
        UserClassType,
        UserFunction,
        ListClass,
        DictClass,
        TupleClass,
        Module,
        FixedFunction,
        PolymorphicFunction,
        SpecialFunction,

        InvalidClassHierarchyException,

        )

class Scope(object):
    def __init__(self):
        self.__listeners = {} # name -> set of listeners on that name

    def add_listener(self, name, l):
        assert isinstance(name, str)
        if not l:
            return
        assert callable(l)
        self.__listeners.setdefault(name, set()).add(l)

    def fire_listeners(self, name):
        for l in self.__listeners.get(name, []):
            l()

class ModuleScope(Scope):
    # these things should be singletons
    __modules_scoped = set()

    def __init__(self, fn, t):
        assert isinstance(t, Module)
        assert fn.startswith('/'), fn

        assert not fn in ModuleScope.__modules_scoped
        ModuleScope.__modules_scoped.add(fn)

        super(ModuleScope, self).__init__()

        self._filename = fn
        self._t = t
        # Important: if you change the module globals through a module reference, have to trigger the scope listeners as well
        # TODO maybe only have one set of listeners, rather than both?  could do this by calling self._t.add_listener instead of self.add_listener
        self._t.add_name_listener(None, self.fire_listeners)

    def get_name(self, name, listener, global_=False, skip=False):
        self.add_listener(name, listener)

        # if name == "__m__":
            # return Union(self._t)

        # TODO could probably also avoid adding the listener
        if skip:
            return BUILTINS.get(name, None)

        u = self._t.get_name(name)
        if u is not None:
            return u
        return BUILTINS.get(name, None)

    def set_name(self, name, u, global_=False):
        assert isinstance(name, str)
        assert isinstance(u, Union)

        # Note: setattr will fire _t's listeners if it changes, which will fire this scopes listeners
        self._t.setattr(name, u)

    def filename(self):
        return self._filename

    def enclosing_class(self):
        return None

class FunctionScope(Scope):
    def __init__(self, parent, t):
        assert isinstance(parent, Scope)
        assert isinstance(t, UserFunction), t

        super(FunctionScope, self).__init__()

        while isinstance(parent, ClassScope):
            parent = parent._parent

        self._parent = parent
        self._t = t
        self._names = {}
        self._global_names = set()

    def is_global(self, n):
        return n in self._global_names

    def get_name(self, name, listener, global_=False, skip=False):
        if not global_:
            self.add_listener(name, listener)

        if global_ or name in self._global_names:
            return self._parent.get_name(name, listener, True)

        if not skip and name in self._names:
            return self._names[name]

        return self._parent.get_name(name, listener, False, False)

    def set_name(self, name, u, global_=False):
        assert isinstance(name, str)
        assert isinstance(u, Union)

        if global_ or name in self._global_names:
            self._parent.set_name(name, u, True)
        else:
            old_u = self._names.get(name)
            self._names[name] = Union.make_union(u, old_u or Union.EMPTY)

            if old_u != self._names[name]:
                self.fire_listeners(name)

    def set_global(self, name):
        assert isinstance(name, str)

        # This would be bad because you'd have to re-set that variable now that it's global, and we don't track that dependency
        assert not name in self._names

        if name not in self._global_names:
            self._global_names.add(name)
            self.fire_listeners(name)

    def filename(self):
        return self._parent.filename()

    def type(self):
        return self._t

    def enclosing_class(self):
        return self._parent.enclosing_class()

class ClassScope(Scope):
    def __init__(self, parent, t):
        assert isinstance(parent, Scope)
        assert isinstance(t, UserClassType), t

        super(ClassScope, self).__init__()

        self._parent = parent
        self._t = t
        self._global_names = set()

        self._t.add_name_listener(None, self.fire_listeners)

    # TODO duplication with FunctionScope.get_name
    def get_name(self, name, listener, global_=False, skip=False):
        if not global_:
            self.add_listener(name, listener)

        if global_ or name in self._global_names:
            return self._parent.get_name(name, listener, True)

        # Don't actually have to get it from the class, because it will stay in the locals
        # if not skip:
            # u = self._t.get_name(name, listener)
            # if u:
                # return u

        return self._parent.get_name(name, listener, False, False)

    def set_name(self, name, u, global_=False):
        assert isinstance(name, str)
        assert isinstance(u, Union)

        if global_ or name in self._global_names:
            self._parent.set_name(name, u, True)
        else:
            self._t.setattr(name, u)

    def set_global(self, name):
        assert isinstance(name, str)

        # This would be bad because you'd have to re-set that variable now that it's global, and we don't track that dependency
        # TODO hax
        assert not name in self._t._attributes

        if name not in self._global_names:
            self._global_names.add(name)
            self.fire_listeners(name)

    def filename(self):
        return self._parent.filename()

    def type(self):
        return self._t

    def enclosing_class(self):
        return self._t

# TODO global var
# expr => Type
created = {}

class Context(object):
    cache = {}
    __slots__ = ("_analyzer", "_node", "_idx")

    def __init__(self, analyzer, node, idx):
        assert isinstance(analyzer, Analyzer)
        assert isinstance(node, _ast.AST)
        assert isinstance(idx, int)
        self._analyzer = analyzer
        self._node = node
        self._idx = idx

    def listener(self):
        return self._analyzer.get_listener()

    def get_cached(self, key):
        return Context.cache.get((self._node, self._idx, key))

    def set_cached(self, key, value):
        Context.cache[(self._node, self._idx, key)] = value

    def register_definition(self, t):
        assert not t in self._analyzer.engine.type_definitions
        self._analyzer.engine.type_definitions[t] = (self._analyzer.scope.filename(), self._node.lineno)

    def log_error(self, s):
        # print s
        self._analyzer.engine.do_error(self._analyzer.scope.filename(), self._node.lineno, self._node.col_offset, s, self._analyzer.state.queue_key)

    def log_warning(self, s):
        pass

    def clear_locals(self):
        # Sometimes need to clear the locals state, such as when in a global context and calling a function,
        # or when importing from another module (which could cause code to get run)

        # To deal with this, set the locals back to the conservative scope-based estimate.
        # Note: important not to just clear the locals, since that won't propagate
        # the clear to future nodes

        a = self._analyzer
        l = a.get_listener()
        locals_ = a.state.locals_
        if isinstance(a.scope, ModuleScope):
            get_name = a.scope.get_name
            for n in locals_:
                u = get_name(n, l)
                if DEBUG >= 2:
                    assert u == Union.make_union(u, locals_[n])
                locals_[n] = u
        elif isinstance(a.scope, FunctionScope):
            for n in locals_:
                if a.scope.is_global(n):
                    u = a.scope.get_name(n, l)
                    if DEBUG >= 2:
                        assert u == Union.make_union(u, locals_[n])
                    locals_[n] = u
        elif isinstance(a.scope, ClassScope):
            for n in locals_:
                u = a.scope.type().get_name(n, l)
                if DEBUG >= 2:
                    assert u == Union.make_union(u, locals_[n])
                locals_[n] = u
        else:
            raise Exception(a.scope)

BINOP_NAMES = {
    _ast.Mult:"__mul__",
    _ast.Add:"__add__",
    _ast.Sub:"__sub__",
    _ast.Mod:"__mod__",
    _ast.Pow:"__pow__",
    _ast.Div:"__div__",
    _ast.FloorDiv:"__floordiv__",
    _ast.BitAnd:"__and__",
    _ast.BitXor:"__xor__",
    _ast.BitOr:"__or__",
    _ast.LShift:"__lshift__",
    _ast.RShift:"__rshift__",
}
UNOP_NAMES = {
    _ast.USub:"__neg__",
    _ast.UAdd:"__pos__",
    _ast.Invert:"__invert__",
    _ast.Not: "__nonzero__",
}
CMP_NAMES = {
    _ast.LtE:"__le__",
    _ast.Lt :"__lt__",
    _ast.GtE:"__ge__",
    _ast.Gt :"__gt__",
    _ast.Eq :"__eq__",
    _ast.NotEq :"__ne__",
    # _ast.In :"__contains__",
    # _ast.NotIn :"__contains__", 
}
AUGASSIGN_NAMES = dict((k, "__i%s__" % v[2:-2]) for (k,v) in BINOP_NAMES.iteritems())

class Analyzer(object):
    def __init__(self, engine, scope, state):
        assert isinstance(engine, Engine)
        assert isinstance(scope, Scope)
        assert isinstance(state, BlockState)
        self.engine = engine
        self.scope = scope
        self.state = state
        self.__listener = self.engine.get_listener(self.state.queue_key)

    def __eq__(self, rhs):
        raise Exception()
    def __ne__(self, rhs):
        return not (self==rhs)
    def __hash__(self):
        raise Exception()

    def get_listener(self):
        return self.__listener

    def _mangle_name(self, n):
        assert isinstance(n, str)
        if n.startswith("__") and not n.endswith("__"):
            cls = self.scope.enclosing_class()
            if cls:
                n = "_%s%s" % (cls.name, n)

        return n

    def mangle_name(self, n):
        assert isinstance(n, _ast.Name)
        return self._mangle_name(n.id)

    def get_expr_type(self, e):
        assert isinstance(e, _ast.AST), e

        u = self._get_expr_type(e)
        assert isinstance(u, Union), (u, e)
        self.engine.node_types[e] = u

        if DEBUG >= 2 and has_params(u):
            print "WARNING: output %s??" % (u.display(),)

        for t in u.types():
            t.add_listener(self.get_listener())
        return u

    def _context(self, e, n=0):
        assert isinstance(e, _ast.AST)
        assert isinstance(n, int)
        return Context(self, e, n)

    def _get_expr_type(self, e):
        if isinstance(e, _ast.Num):
            if isinstance(e.n, (int, long)):
                return Union(INT)
            return Union(FLOAT)
        elif isinstance(e, _ast.Str):
            return Union(STR)
        elif isinstance(e, _ast.Name):
            n = self.mangle_name(e)
            if n in self.engine.overrides:
                u = self.engine.overrides[n]
            elif n in self.state.locals_:
                u = self.state.locals_[n]
            else:
                # # The 'skip' parameter is used to show that you 'del'd something, but for the global namespace we'd rather see other global updates
                # u = self.scope.get_name(n, self.get_listener(), skip=(not isinstance(self.scope, ModuleScope)))
                # no that doesn't work
                u = self.scope.get_name(n, self.get_listener(), skip=True)
                if u is None:
                    u = Union.EMPTY
                    if not hasattr(e, "not_real"):
                        self.engine.do_error(self.scope.filename(), e.lineno, e.col_offset, "NameError: no variable named '%s'" % (n), self.state.queue_key)
                else:
                    assert isinstance(u, Union), u
            if not hasattr(e, "not_real"):
                self.engine.do_annotate(self.scope.filename(), e.lineno, e.col_offset, u)
            return u
        elif isinstance(e, _ast.List) or (sys.version_info >= (2,7) and isinstance(e, _ast.Set)):
            # TODO have a _make_list function that takes the elt type and goes through the normal machinery
            u = Union.make_union(*[self.get_expr_type(elt) for elt in e.elts])
            if not e in created:
                cls = ListClass
                if sys.version_info >= (2,7) and isinstance(e, _ast.Set):
                    cls = SetClass
                created[e] = InstanceType(cls, [Union.EMPTY])
                self._context(e).register_definition(created[e])
            created[e].update(0, u)
            return Union(created[e])
        elif isinstance(e, _ast.Dict):
            # TODO have a _make_list function that takes the elt type and goes through the normal machinery
            k = Union.make_union(*[self.get_expr_type(elt) for elt in e.keys])
            v = Union.make_union(*[self.get_expr_type(elt) for elt in e.values])
            if not e in created:
                created[e] = InstanceType(DictClass, [Union.EMPTY, Union.EMPTY])
                self._context(e).register_definition(created[e])
            created[e].update(0, k)
            created[e].update(1, v)
            return Union(created[e])
        elif isinstance(e, _ast.Attribute):
            v = self.get_expr_type(e.value)
            u = v.getattr(self._mangle_name(e.attr), self._context(e))
            if not hasattr(e, "not_real"):
                offset = e.col_offset
                if offset == -1:
                    offset = 0
                else:
                    offset += ast_utils.est_expr_length(e.value)
                self.engine.find_annotate(self.scope.filename(), e.lineno, offset, "\\." + e.attr, 1, u)
            return u
        elif isinstance(e, _ast.Call):
            if e.kwargs:
                kw = self.get_expr_type(e.kwargs)
                for t in kw.types():
                    if not isinstance(t, InstanceType) or not t.cls is DictClass:
                        self.engine.do_error(self.scope.filename(), e.kwargs.lineno, e.kwargs.col_offset, "kwargs is not a dict", self.state.queue_key)
                        continue
                    if Union.make_union(t.unions[0], Union(STR)) != Union(STR):
                        self.engine.do_error(self.scope.filename(), e.kwargs.lineno, e.kwargs.col_offset, "kwargs is not a dict with string keys", self.state.queue_key)
                        continue
                self.engine.do_error(self.scope.filename(), e.lineno, e.col_offset, "kwargs not supported yet", self.state.queue_key)
                print "kwargs not supported yet"

            f = self.get_expr_type(e.func)
            args = [self.get_expr_type(a) for a in e.args]
            keywords = dict((kw.arg, self.get_expr_type(kw.value)) for kw in e.keywords)
            starargs = self.get_expr_type(e.starargs) if e.starargs else None

            u = f.call(args, keywords, starargs, self._context(e), False, e.args)
            return u
        elif isinstance(e, _ast.Subscript):
            v = self.get_expr_type(e.value)
            s = self.get_expr_type(e.slice)

            rtn = []
            for t in v.types():
                # TODO is this the right place to special-case tuple subscripts?
                # it would be more disruptive to pass the actual ast all the way through.
                if isinstance(t, InstanceType) and t.cls is TupleClass and isinstance(e.slice, _ast.Index) and isinstance(e.slice.value, _ast.Num):
                    n = e.slice.value.n
                    if not (0 <= n < len(t.unions)):
                        self.engine.do_error(self.scope.filename(), e.lineno, e.col_offset, "Can't get index %d on a %d-tuple" % (n, len(t.unions)), self.state.queue_key)
                    else:
                        rtn.append(t.unions[n])
                else:
                    rtn.append(t.getattr("__getitem__", self._context(e, 1)).call([s], {}, None, self._context(e, 2), False, None))
            return Union.make_union(*rtn)
        elif isinstance(e, _ast.Index):
            return self.get_expr_type(e.value)
        elif isinstance(e, _ast.Slice):
            if e.lower:
                l = self.get_expr_type(e.lower)
            else:
                l = Union(INT)
            if e.upper:
                u = self.get_expr_type(e.upper)
            else:
                u = Union(INT)
            if e.step:
                step = self.get_expr_type(e.step)
            else:
                step = Union(INT)

            if Union.make_union(l, Union(INT)) != Union(INT):
                self.engine.do_error(self.scope.filename(), e.lower.lineno, e.lower.col_offset, "Slice lower bound is %s instead of num" % (l.display(),), self.state.queue_key)
            if Union.make_union(u, Union(INT)) != Union(INT):
                self.engine.do_error(self.scope.filename(), e.upper.lineno, e.upper.col_offset, "Slice upper bound is %s instead of num" % (u.display(),), self.state.queue_key)

            if Union.make_union(step, Union(INT)) != Union(INT):
                self.engine.do_error(self.scope.filename(), e.upper.lineno, e.upper.col_offset, "Slice step is %s instead of num" % (step.display(),), self.state.queue_key)
            return Union(SLICE)
        elif isinstance(e, (_ast.ListComp, _ast.GeneratorExp)) or (sys.version_info >= (2,7) and isinstance(e, _ast.SetComp)):
            # TODO handle generatorexp and listcomp the same.  should probably just not set the iterator variable?  ie clear it afterwards
            for comp in e.generators:
                target = comp.target

                iter_type = self.get_expr_type(comp.iter)
                target_type = get_iter_type(iter_type, self._context(e, 5))

                self._do_set(target, target_type)

                for _e in comp.ifs:
                    self.get_expr_type(_e)

            elt_type = self.get_expr_type(e.elt)
            if not e in created:
                cls = ListClass
                if isinstance(e, _ast.GeneratorExp):
                    cls = GeneratorClass
                elif sys.version_info >= (2,7) and isinstance(e, _ast.SetComp):
                    cls = SetClass
                created[e] = InstanceType(cls, [Union.EMPTY])
                self._context(e).register_definition(created[e])
            created[e].update(0, elt_type)
            return Union(created[e])
        elif sys.version_info >= (2,7) and isinstance(e, _ast.DictComp):
            # TODO dict comprehensions don't leave the variables set afterwards
            for comp in e.generators:
                target = comp.target

                iter_type = self.get_expr_type(comp.iter)
                target_type = get_iter_type(iter_type, self._context(e, 5))

                self._do_set(target, target_type)

                for _e in comp.ifs:
                    self.get_expr_type(_e)

            key_type = self.get_expr_type(e.key)
            value_type = self.get_expr_type(e.value)
            if not e in created:
                cls = DictClass
                created[e] = InstanceType(cls, [Union.EMPTY, Union.EMPTY])
                self._context(e).register_definition(created[e])
            created[e].update(0, key_type)
            created[e].update(1, value_type)
            return Union(created[e])
        elif isinstance(e, _ast.BinOp):
            l = self.get_expr_type(e.left)
            r = self.get_expr_type(e.right)
            op = e.op

            # TODO __rmul__, ie right-sided ops
            n = BINOP_NAMES[type(op)]
            f = l.getattr(n, self._context(e, 1))

            return f.call([r], {}, None, self._context(e, 2), False, None)
        elif isinstance(e, _ast.BoolOp):
            r = []
            for v in e.values:
                u = self.get_expr_type(v)
                u.getattr("__nonzero__", self._context(e, 1)).call([], {}, None, self._context(e, 2), False, None)
                r.append(u)
            return Union.make_union(*r)
        elif isinstance(e, _ast.UnaryOp):
            v = self.get_expr_type(e.operand)
            op = e.op

            # TODO __rmul__, ie right-sided ops
            n = UNOP_NAMES[type(op)]
            f = v.getattr(n, self._context(e, 1))

            return f.call([], {}, None, self._context(e, 2), False, None)
        elif isinstance(e, _ast.Compare):
            assert len(e.comparators) == len(e.ops)

            l = self.get_expr_type(e.left)
            for i in xrange(len(e.ops)):
                op = e.ops[i]

                r = self.get_expr_type(e.comparators[i])

                if type(op) in (_ast.Is, _ast.IsNot):
                    return Union(BOOL)
                elif type(op) in (_ast.In, _ast.NotIn):
                    l, r = r, l
                    n = "__contains__"
                    # I think it converts "a not in b" to "not (a in b)"  ie theres no __notcontains__?
                else:
                    # TODO reflection?
                    n = CMP_NAMES[type(op)]

                f = l.getattr(n, self._context(e, 1))

                rtn = f.call([r], {}, None, self._context(e, 2), False, None)
                # if f.types() and rtn != Union(BOOL) and TOP not in f.types():
                    # print "comparator didn't return bool??", (l.display(), n, f.display(), rtn.display())

                l = r
            # TODO does it coerce like this?
            return Union(BOOL)
        elif isinstance(e, _ast.Tuple):
            us = [self.get_expr_type(elt) for elt in e.elts]
            if not e in created:
                created[e] = InstanceType(TupleClass, [Union.EMPTY for u in e.elts])
                self._context(e).register_definition(created[e])
            t = created[e]
            assert len(t.unions) == len(e.elts)
            for i in xrange(len(e.elts)):
                t.update(i, us[i])
            return Union(t)
        elif isinstance(e, _ast.Lambda):
            return self._make_function(e)
        elif isinstance(e, _ast.IfExp):
            v1 = self.get_expr_type(e.body)
            v2 = self.get_expr_type(e.orelse)
            t = self.get_expr_type(e.test)
            return Union.make_union(v1, v2)
        elif isinstance(e, _ast.Yield):
            assert isinstance(self.scope, FunctionScope)
            if e.value:
                v = self.get_expr_type(e.value)
            else:
                v = Union(NONE)
            f = self.scope.type()
            f.update_yield(v)
            return Union.EMPTY
        elif isinstance(e, _ast.Repr):
            self.get_expr_type(e.value)
            return Union(STR)
        elif isinstance(e, _ast.ExtSlice):
            # wtf
            return Union(TOP)
        elif isinstance(e, cfa.HasNext):
            self.get_expr_type(e.iter)
            return Union(BOOL)
        else:
            raise Exception(e)
        raise Exception()

    def pre_jump(self, node):
        pass

    def pre_branch(self, node):
        self.get_expr_type(node.test)
        return ()

    def get_type_constraints(self, e):
        """
        Gets the set of type constraints that must be true in order for 'e' to evaluate to a True value.

        Returns a dict of name -> Union updates
        """

        if isinstance(e, _ast.Call):
            if isinstance(e.func, _ast.Name) and e.func.id == "isinstance" and len(e.args) == 2 and isinstance(e.args[0], _ast.Name):
                cls = self.get_expr_type(e.args[1])
                r = get_instance_type(cls)
                if r is None:
                    return {}
                return {e.args[0].id: r}

            return {}

        if isinstance(e, _ast.BoolOp):
            t = e.op

            keys = set()
            subs = [self.get_type_constraints(v) for v in e.values]
            for d in subs:
                keys.update(d)

            r = {}

            if isinstance(t, _ast.And):
                for k in keys:
                    cur = None
                    for d in subs:
                        if k not in d:
                            continue

                        if cur is None:
                            cur = d[k]
                            continue

                        types = set(cur.types()).intersection(d[k].types())
                        cur = Union(*types)
                    r[k] = cur
                return r

            if isinstance(t, _ast.Or):
                for k in keys:
                    cur = None
                    for d in subs:
                        if k not in d:
                            break

                        if cur is None:
                            cur = d[k]
                            continue

                        types = set(cur.types() + d[k].types())
                        cur = Union(*types)
                    else:
                        r[k] = cur
                return r

            raise Exception(t)

        if isinstance(e, (_ast.Name, _ast.BinOp, _ast.Compare, _ast.UnaryOp, _ast.Attribute, _ast.Num, _ast.Str, _ast.Subscript, _ast.ListComp, _ast.GeneratorExp, _ast.IfExp, _ast.Tuple)):
            return {}
        raise Exception(e)

    def pre_assign(self, node):
        u = self.get_expr_type(node.value)

        # TODO verify that the order is correct when a variable is set multiple times in the same statement
        for t in node.targets:
            self._do_set(t, u)
        return ()

    def _do_set(self, target, u, scope=None, locals_=None):
        assert isinstance(target, _ast.AST)
        assert isinstance(u, Union)
        if scope is None:
            scope = self.scope
        assert isinstance(scope, Scope)
        if locals_ is None:
            locals_ = self.state.locals_
        assert isinstance(locals_, dict)

        # this is used as a stack
        to_set = collections.deque([(target, u)])
        # TODO verify that the order is correct when a variable is set multiple times in the same statement
        vars_to_set = {}
        while to_set:
            target, u = to_set.pop()

            if isinstance(target, _ast.Name):
                vars_to_set[self.mangle_name(target)] = u
                self.engine.node_types[target] = u
                if not hasattr(target, "not_real"):
                    self.engine.do_annotate(scope.filename(), target.lineno, target.col_offset, u)
            elif isinstance(target, _ast.Subscript):
                v = self.get_expr_type(target.value)
                s = self.get_expr_type(target.slice)
                v.getattr("__setitem__", self._context(target, 1)).call([s, u], {}, None, self._context(target, 2), False, None)
            elif isinstance(target, _ast.Attribute):
                v = self.get_expr_type(target.value)
                n = self._mangle_name(target.attr)
                v.setattr(n, u)
                self.engine.node_types[target] = u
                self.engine.find_annotate(scope.filename(), target.lineno, target.col_offset, "\\." + target.attr, 1, v.getattr(n, self._context(target)))

                # edge case: if you assign something to the global scope that you're currently in, do it there too
                # TODO is this the only place that Module.setattr could be called?
                if isinstance(self.scope, ModuleScope) and self.scope._t in v.types():
                    if len(v.types()) == 1:
                        vars_to_set[n] = u
                    else:
                        vars_to_set[n] = Union.make_union(self.state.locals_.get(n, Union.EMPTY), u)
            elif isinstance(target, (_ast.Tuple, _ast.List)):
                nv = len(target.elts)
                to_assign = [Union.EMPTY for i in xrange(nv)]
                for t in u.types():
                    if isinstance(t, InstanceType):
                        if t.cls is TupleClass:
                            if len(t.unions) != nv:
                                self.engine.do_error(scope.filename(), target.lineno, target.col_offset, "unable to unpack a %s-tuple into a %s-tuple" % (len(t.unions), nv), self.state.queue_key)
                                continue
                            for i in xrange(nv):
                                to_assign[i] = Union.make_union(to_assign[i], t.unions[i])
                            continue

                    elt_type = get_iter_type(Union(t), self._context(target, 5))

                    if len(elt_type.types()) == 0:
                        self.engine.do_error(scope.filename(), target.lineno, target.col_offset, "unable to unpack a %s into a %s-tuple" % (t.display(), nv), self.state.queue_key)
                    else:
                        for i in xrange(nv):
                            to_assign[i] = Union.make_union(to_assign[i], elt_type)

                # Have to put them on in reverse order because it's a stack
                for i in reversed(xrange(nv)):
                    to_set.append((target.elts[i], to_assign[i]))
            else:
                raise Exception(target)

        for n, u in vars_to_set.iteritems():
            assert isinstance(n, str)
            assert isinstance(u, Union)
            locals_[n] = u
            scope.set_name(n, u)
        return ()

    def pre_augassign(self, node):
        t = self.get_expr_type(node.target)
        v = self.get_expr_type(node.value)

        name = AUGASSIGN_NAMES[type(node.op)]
        fallback_name = BINOP_NAMES[type(node.op)]
        f = t.getattr((name, fallback_name), self._context(node, 1))
        r = f.call([v], {}, None, self._context(node, 2), False, None)
        self._do_set(node.target, r)
        return ()

    def pre_expr(self, node):
        self.get_expr_type(node.value)
        return ()

    def pre_assert(self, node):
        if isinstance(node.test, (_ast.Tuple, _ast.List)):
            self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "why are you using this as an assertion test?", self.state.queue_key)
        self.get_expr_type(node.test)
        if node.msg:
            self.get_expr_type(node.msg)

        for name, t in self.get_type_constraints(node.test).iteritems():
            self.state.locals_[name] = t
        return ()

    def pre_print(self, node):
        for v in node.values:
            self.get_expr_type(v)
        if node.dest:
            self.get_expr_type(node.dest)
        return ()

    def pre_pass(self, node):
        return ()

    def _make_function(self, node, initial_args=None):
        assert isinstance(node, _ast.AST)

        # TODO closure won't let things die
        # should probably take them as arguments
        def up():
            if isinstance(node, _ast.FunctionDef):
                self.engine.find_annotate(self.scope.filename(), node.lineno, node.col_offset+4, node.name, 0, Union(t))
            narg = len(node.args.args)
            locals_ = {}
            for i in xrange(narg):
                # TODO closure problem...
                self._do_set(node.args.args[i], t.unions[i], self.engine.scopes[node], locals_)
            if node.args.vararg:
                vkey = (node, 'vararg')
                if vkey not in created:
                    created[vkey] = _va = InstanceType(ListClass, [Union.EMPTY])
                    self.engine.type_definitions[created[vkey]] = (self.engine.scopes[node].filename(), node.lineno)
                    _va.add_listener(lambda:t.update(t.vararg_idx, _va.unions[0]))
                    _va.add_listener(up)
                created[vkey].update(0, t.unions[t.vararg_idx])
                u = Union(created[vkey])
                # TODO hax
                locals_[node.args.vararg] = u
                self.engine.scopes[node].set_name(node.args.vararg, u, self.engine.get_listener((node, 0)))
                self.engine.find_annotate(self.scope.filename(), node.lineno, node.col_offset, "\\*" + node.args.vararg, 1, Union(created[vkey]))
            if node.args.kwarg:
                kkey = (node, 'kwarg')
                if kkey not in created:
                    created[kkey] = _ka = InstanceType(DictClass, [Union(STR), Union.EMPTY])
                    self.engine.type_definitions[created[kkey]] = (self.engine.scopes[node].filename(), node.lineno)
                    _ka.add_listener(lambda:t.update(t.kwarg_idx, _ka.unions[1]))
                    _ka.add_listener(up)
                created[kkey].update(1, t.unions[t.kwarg_idx])
                u = Union(created[kkey])
                # TODO hax
                locals_[node.args.kwarg] = u
                self.engine.scopes[node].set_name(node.args.kwarg, u, self.engine.get_listener((node, 0)))
                self.engine.find_annotate(self.scope.filename(), node.lineno, node.col_offset, "\\*\\*" + node.args.kwarg, 2, Union(created[kkey]))

            self.engine.queue_scope(node, locals_)

        # Do this even if we're not going to create the node, to update the annotations / type info of these things
        defaults = [self.get_expr_type(e) for e in node.args.defaults]
        if not node in created:
            arg_types = [Union.EMPTY for a in node.args.args]
            if initial_args:
                for i, u in enumerate(initial_args):
                    arg_types[i] = u
            ndefault = len(defaults)
            for i in xrange(ndefault):
                arg_types[len(arg_types) - ndefault + i] = defaults[i]

            vararg = Union.EMPTY if node.args.vararg else None
            kwarg = Union.EMPTY if node.args.kwarg else None
            arg_names = []
            for a in node.args.args:
                if isinstance(a, _ast.Name):
                    arg_names.append(self.mangle_name(a))
                elif isinstance(a, _ast.Tuple):
                    # tuple arguments can only be positional arguments, so this name doesn't really matter
                    arg_names.append('! tuple-hidden')
                else:
                    raise Exception(a)
            t = UserFunction(arg_names, arg_types, ndefault, vararg, kwarg, Union.EMPTY)
            # TODO hax
            self.engine.scopes[node] = FunctionScope(self.scope, t)
            if isinstance(node, _ast.FunctionDef):
                global_names = ast_utils.find_global_vars(node)
                for n in global_names:
                    self.engine.scopes[node].set_global(n)

            created[node] = Union(t)
            t.add_listener(up)
            up()

            self.engine.type_definitions[t] = (self.scope.filename(), node.lineno)
        else:
            [f] = created[node].types()
            for i in xrange(len(defaults)):
                f.update(len(node.args.args) - len(defaults) + i, defaults[i])

        u = created[node]
        if isinstance(node, _ast.FunctionDef):
            for d in reversed(node.decorator_list):
                ud = self.get_expr_type(d)
                u = ud.call([u], {}, None, self._context(d), False, None)
        return u

    def pre_functiondef(self, node):
        # TODO not sure if this should happen here or in make_function
        initial_args = []
        if isinstance(self.scope, ClassScope) and not node.decorator_list and len(node.args.args) >= 1:
            assert len(node.args.args) >= 1
            if self.mangle_name(node.args.args[0]) == "self":
                initial_args.append(Union(self.scope.type().instance()))

        u = self._make_function(node, initial_args)
        name = self._mangle_name(node.name)
        self.state.locals_[name] = u
        self.scope.set_name(name, u)
        self.engine.node_types[node] = u
        return ()

    def pre_return(self, node):
        if node.value is None:
            r = Union(NONE)
        else:
            r = self.get_expr_type(node.value)
        assert isinstance(self.scope, FunctionScope)
        t = self.scope.type()
        t.update(t.rtn_idx, r)
        return ()

    def pre_raise(self, node):
        if node.tback:
            self.get_expr_type(node.tback)
        if node.type:
            self.get_expr_type(node.type)
        if node.inst:
            self.get_expr_type(node.inst)
        return ()

    def pre_exec(self, node):
        self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "gtfo", self.state.queue_key)
        self.get_expr_type(node.body)
        if node.locals:
            self.get_expr_type(node.locals)
        if node.globals:
            self.get_expr_type(node.globals)
        return ()

    def pre_classdef(self, node):
        for d in node.decorator_list:
            self.engine.do_error(self.scope.filename(), d.lineno, d.col_offset, "Class decorators are unsupported", self.state.queue_key)

        if len(node.bases) == 0:
            bases = [Union(ObjectClass)]
            self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Don't really handle old-style classes", self.state.queue_key)
        else:
            bases = [self.get_expr_type(b) for b in node.bases]

        # The base types might be imported, in which case they will be unknown for now
        error = None
        classes = []
        for b in bases:
            assert isinstance(b, Union)
            picked = None
            for t in b.types():
                if isinstance(t, ClassType):
                    if picked:
                        self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Multiple possible classes to derive from, picking %s" % (t.display(),), self.state.queue_key)
                    picked = t
                else:
                    self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Non-class as a potential base class: %s" % (t.display(),), self.state.queue_key)
            if picked is None:
                error = "No suitable type to subclass from"
            else:
                classes.append(picked)

        if error:
            self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, error, self.state.queue_key)

            u = Union.EMPTY

            self.state.locals_[node.name] = u
            self.scope.set_name(node.name, u)
        else:
            assert len(classes) == len(bases)
            for b in classes:
                assert isinstance(b, ClassType)

            if not node in created:
                try:
                    t = UserClassType(node.name, classes)
                    self.engine.scopes[node] = ClassScope(self.scope, t)
                    self.engine.type_definitions[t] = (self.scope.filename(), node.lineno)
                except InvalidClassHierarchyException:
                    t = "Invalid class hierarchy"
                created[node] = t

            t = created[node]
            if isinstance(t, str):
                self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, t, self.state.queue_key)
                u = Union.EMPTY
            else:
                u = Union(t)

                # note: important to recrawl even if we've created it already
                self.engine.queue_scope(node)

                init = t.get_name("__init__", self.get_listener())
                assert init
                for t2 in init.types():
                    if isinstance(t2, UserFunction):
                        t2.update(0, Union(t.instance()))

            # note: important to insert the class into the scope before executing it
            self.state.locals_[node.name] = u
            self.scope.set_name(node.name, u)

        self.engine.find_annotate(self.scope.filename(), node.lineno, node.col_offset+6, node.name, 0, u)
        self.engine.node_types[node] = u

        # raise NotImplementedError()
        return ()

    def pre_global(self, node):
        if isinstance(self.scope, ModuleScope):
            self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Can't have a global declaration in a global scope", self.state.queue_key)
            return

        for n in node.names:
            assert isinstance(n, str)
            n = self._mangle_name(n)
            self.scope.set_global(n)
            u = self.scope.get_name(n, self.get_listener())
            if u:
                self.engine.find_annotate(self.scope.filename(), node.lineno, node.col_offset, n, 0, u)

        return ()

    def pre_delete(self, node):
        for target in node.targets:
            if isinstance(target, _ast.Name):
                n = self.mangle_name(target)
                if n in self.state.locals_:
                    del self.state.locals_[n]
                else:
                    self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Can't delete non-existent name '%s'" % (n,), self.state.queue_key)
                # TODO shouldn't do anything in the scope, right?
            elif isinstance(target, _ast.Subscript):
                v = self.get_expr_type(target.value)
                s = self.get_expr_type(target.slice)
                v.getattr("__delitem__", self._context(target, 1)).call([s], {}, None, self._context(target, 2), False, None)
            elif isinstance(target, _ast.Attribute):
                v = self.get_expr_type(target.value)
                v.getattr(self._mangle_name(target.attr), self._context(target))
                self.engine.do_error(self.scope.filename(), target.lineno, target.col_offset, "Don't support deleting attributes in any useful way", self.state.queue_key)
            else:
                raise Exception(target)
        return ()

    def pre_import(self, node):
        # Have to clear locals because the act of importing another module could have arbitrary effects (if this is the global scope, which clear_locals takes care of checking)
        self._context(node).clear_locals()
        for a in node.names:
            # module_name is the name to give to the resulting loaded module
            # as_name is the name to set in the locals

            modules = self.engine.load_modules(a.name, [os.path.dirname(self.scope.filename())] + self.engine.python_path)
            for m in modules:
                assert isinstance(m, Module)
            for i in xrange(len(modules)-1):
                modules[i].add_name_listener(modules[i+1].name, self.get_listener())

            names = a.name.split('.')
            assert len(modules) <= len(names)
            loaded = True
            if len(modules) < len(names):
                self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Unable to load module %s" % names[len(modules)], self.state.queue_key)
                loaded = False

            if a.asname:
                if loaded:
                    m = modules[-1]
                asname = a.asname
            else:
                if loaded:
                    m = modules[0]
                    asname = m.name
                else:
                    asname = names[0]
                if '.' in a.name:
                    assert asname == a.name[:a.name.find('.')]
                else:
                    assert asname == a.name

            if loaded:
                t = Union(m)
            else:
                t = Union.EMPTY
            for i in xrange(len(modules)):
                self.engine.find_annotate(self.scope.filename(), node.lineno, node.col_offset, names[i], 0, Union(modules[i]))
            for i in xrange(len(modules), len(names)):
                self.engine.find_annotate(self.scope.filename(), node.lineno, node.col_offset, names[i], 0, Union.EMPTY)
            assert isinstance(t, Union)
            self.state.locals_[asname] = t
            self.scope.set_name(asname, t)
        return ()

    def pre_importfrom(self, node):
        # Have to clear locals because the act of importing another module could have arbitrary effects (if this is the global scope, which clear_locals takes care of checking)
        self._context(node).clear_locals()

        if node.module and node.module == "__future__":
            for name in node.names:
                if name.name not in ("with_statement",):
                    self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Not sure how to handle '%s'" % name.name, self.state.queue_key)
            return

        loaded = True
        if node.level > 0:
            f = self.scope.filename()
            for i in xrange(node.level):
                f = os.path.dirname(f)
                if not os.path.exists(os.path.join(f, "__init__.py")):
                    # Kind of hax control flow here
                    loaded = False
                    self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Attempted relative import from non-package", self.state.queue_key)
                assert f != '/'
            python_path = [f]
        else:
            python_path = [os.path.dirname(self.scope.filename())] + self.engine.python_path

        # TODO should only allow relative imports from packages
        modules = self.engine.load_modules(node.module, python_path)

        if node.module:
            names = node.module.split('.')
            assert len(modules) <= len(names)
            if len(modules) < len(names):
                self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Unable to load module %s" % names[len(modules)], self.state.queue_key)
                loaded = False

            for i in xrange(len(modules)):
                self.engine.find_annotate(self.scope.filename(), node.lineno, node.col_offset, "[^\w]%s([^\w]|$)" % names[i], 1, Union(modules[i]))
            for i in xrange(len(modules), len(names)):
                self.engine.find_annotate(self.scope.filename(), node.lineno, node.col_offset, "[^\w]%s([^\w]|$)" % names[i], 1, Union.EMPTY)
        else:
            assert len(modules) <= 1
            if not modules:
                self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Attempted relative import from non-package", self.state.queue_key)
                loaded = False

        for m in modules:
            assert isinstance(m, Module)
        for i in xrange(len(modules)-1):
            modules[i].add_name_listener(modules[i+1].name, self.get_listener())

        if any(a.name == '*' for a in node.names):
            self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "warning: using import * (doing indirect imports)", self.state.queue_key)
            if GENERATE_IMPORT_ERRS:
                print >>sys.stderr, "%s:%s      import *" % (self.scope.filename(), node.lineno)
            assert len(node.names) == 1
            if loaded:
                module = modules[-1]
                module.add_name_listener(None, lambda n:self.get_listener()())
                for n in module.all_names():
                    if n == "__all__":
                        print "warning: am not respecting the __all__ directive in module %s" % (module.name,)
                        continue
                    t = module.get_name(n)
                    assert t

                    t.add_listener(self.get_listener())
                    self.state.locals_[n] = t
                    self.scope.set_name(n, t)

            return ()

        types = []
        if loaded:
            module = modules[-1]
            for a in node.names:
                t = module.get_name(a.name)
                module.add_name_listener(a.name, self.get_listener())
                if t is None and module.fn.endswith("/__init__.py"):
                    sub = self.engine.load_modules(a.name, python_path=[os.path.dirname(module.fn)])
                    if sub:
                        [m] = sub
                        assert isinstance(m, Module)
                        module.setattr(a.name, Union(m))
                    t = Union(sub[0]) if sub else Union.EMPTY
                elif t and len(t.types()) == 1 and module.name != "cStringIO":
                    # only check for single unions; otherwise too hard to track down
                    for t2 in t.types():
                        if t2 in self.engine.type_definitions and self.engine.type_definitions[t2][0] != module.fn:
                            self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Warning, indirect import of name '%s', originally from %s" % (a.name, self.engine.type_definitions[t2][0]), self.state.queue_key)
                            if GENERATE_IMPORT_ERRS:
                                print >>sys.stderr, "%s:%s      indirect import of %s; defined in %s but imported from %s" % (self.scope.filename(), node.lineno, a.name, self.engine.type_definitions[t2][0], module.fn)

                if t is None:
                    self.engine.do_error(self.scope.filename(), node.lineno, node.col_offset, "Unable to import name %s" % a.name, self.state.queue_key)
                    t = Union.EMPTY

                types.append(t)
        else:
            for t in node.names:
                types.append(Union.EMPTY)

        for i, a in enumerate(node.names):
            asname = a.asname if a.asname else a.name
            assert not '.' in asname

            t = types[i]

            t.add_listener(self.get_listener())

            self.state.locals_[asname] = t
            self.scope.set_name(asname, t)
            self.engine.find_annotate(self.scope.filename(), node.lineno, node.col_offset, "[^\w]%s($|[^\w])" % asname, 1, t, lines_to_search=1000)
        return ()

class BlockState(object):
    def __init__(self, locals_, queue_key):
        self.locals_ = locals_
        assert isinstance(queue_key, tuple), queue_key
        self.queue_key = queue_key

    def copy(self):
        return BlockState(dict(self.locals_), self.queue_key)

    def __eq__(self, rhs):
        raise Exception()
    def __ne__(self, rhs):
        return not (self==rhs)
    def __hash__(self):
        raise Exception()

class Engine(object):
    def __init__(self, allow_import_errors=True):
        self.cfgs = {} # node -> cfg
        self.input_states = {} # (node, block_id) -> BlockState
        self.scopes = {} # node -> scope
        self.fn_to_blocks = {} # fn -> [(node, block_id)]

        self.annotations = {} # filename -> ((row, col) -> (Union, annotation))
        self.node_types = {} # _ast.AST -> Union
        self.errors = {} # (node, block_id) -> ((row, start, end) -> message)
        self.sources = {} # filename -> list of source lines
        self.listeners = {} # key -> listen for that key

        self.python_path = [] # list of directories to search
        self._loaded_modules = {} # filename -> Module

        self.type_definitions = {} # Type -> (fn, lineno)

        self._cur_key = None
        self._dependencies = {} # queue key -> set([queue keys it updated])
        self.queue = Engine.AnalysisQueue()

        self.overrides = {} # name -> Type

        self._allow_import_errors = allow_import_errors

    def get_listener(self, key):
        if key not in self.listeners:
            self.listeners[key] = lambda: self.mark_changed(key)
        return self.listeners[key]

    def load_source(self, fn, source):
        self.sources[fn] = source.split('\n')

    def do_annotate(self, fn, lineno, col_offset, u):
        assert isinstance(fn, str)
        assert isinstance(lineno, int)
        assert isinstance(col_offset, int)
        assert isinstance(u, Union), u
        # self.annotations.setdefault(fn, {})[(lineno, col_offset)] = (t, str(t) + " " + t.display())
        dis = u.display() if DEBUG else ""
        self.annotations.setdefault(fn, {})[(lineno, col_offset)] = (u, dis)

    def find_annotate(self, fn, lineno, start, regex, offset, u, lines_to_search=10):
        assert isinstance(fn, str)
        assert isinstance(lineno, int)
        assert isinstance(start, int)
        assert isinstance(regex, str)
        assert isinstance(offset, int), offset
        assert isinstance(u, Union), u
        assert isinstance(lines_to_search, int)

        start_lineno = lineno
        start_start = start

        for i in xrange(lines_to_search):
            try:
                source = self.sources[fn][lineno-1]
                col_offset = re.search(regex, source[start:]).start() + offset + start
            except Exception, e:
                # print e
                start = 0
                lineno += 1
            else:
                self.do_annotate(fn, lineno, col_offset, u)
                return
        else:
            print "Couldn't find annotation %s (started looking at %s::%d:%d)" % (repr(regex), fn, start_lineno, start_start)
            # traceback.print_stack()
            return

    def do_error(self, fn, lineno, col_offset, error, key):
        assert isinstance(fn, str)
        assert isinstance(lineno, int)
        assert isinstance(col_offset, int)
        assert isinstance(error, str)
        assert isinstance(key, tuple), key
        assert len(key) == 2
        assert isinstance(key[0], _ast.AST)
        assert isinstance(key[1], int)
        end = len(self.sources[fn][lineno-1])
        err_key = (lineno, col_offset, end)
        self.errors[key][err_key] = error

    def print_score(self, show_files=False, filter=None):
        score = 0.0
        max_score = 0.0
        file_scores = []
        for fn, annotations in self.annotations.iteritems():
            if filter and not filter(fn):
                continue
            file_score = 0.0
            file_max_score = 0.0
            for t, d in annotations.itervalues():
                file_score += t.prettify().score()
                file_max_score += 1.0
            score += file_score
            max_score += file_max_score
            file_scores.append((file_score * 1.0 / file_max_score, "%s: %.1f/%.1f (%.1f%%)" % (fn, file_score, file_max_score, 100.0 * file_score / file_max_score)))

        if show_files:
            file_scores.sort(reverse=True)
            for x, s in file_scores:
                if x > .95:
                    c = '34'
                elif x > .80:
                    c = '32'
                elif x > .50:
                    c = '33'
                else:
                    c = '31'
                print '\033[%sm%s\033[0m' % (c, s)

        if not max_score:
            print "no annotations to score"
        else:
            print "score: %.1f/%.1f (%.1f%%)" % (score, max_score, 100.0 * score / max_score)

    def queue_scope(self, node, locals_=None):
        if node not in self.cfgs:
            if isinstance(node, _ast.FunctionDef):
                if ast_utils.has_yields(node):
                    body = node.body
                else:
                    body = node.body + [_ast.Return(_ast.Name("None", _ast.Load(), not_real=True), not_real=True)]
            elif isinstance(node, _ast.Lambda):
                body = [_ast.Return(node.body, lineno=node.lineno, col_offset=node.col_offset, not_real=True)]
            elif isinstance(node, _ast.Module):
                body = node.body
            elif isinstance(node, _ast.ClassDef):
                body = node.body
            else:
                raise Exception(node)

            self.cfgs[node] = cfg = cfa.cfa(node, body)
            # cfg.show()

            for nid in cfg.blocks:
                assert not (node, nid) in self._dependencies
                if nid == cfg.end:
                    continue

                s = set()
                self._dependencies[(node, nid)] = s
                assert nid in cfg.connects_to, (cfg.connects_to.keys(), nid, cfg.start, cfg.end)
                for n2 in cfg.connects_to[nid]:
                    s.add((node, n2))

            assert not (node, cfg.end) in self._dependencies
            self._dependencies[(node, cfg.end)] = set()

        cfg = self.cfgs[node]

        key = (node, cfg.start)
        if locals_ is None:
            locals_ = {}
        self.update_input(key, locals_)

    def update_input(self, key, locals_):
        assert isinstance(locals_, dict)

        changed = False
        if key not in self.input_states:
            # print "changed due to new key"
            changed = True
            self.input_states[key] = BlockState({}, key)
            self.fn_to_blocks.setdefault(self.scopes[key[0]].filename(), []).append(key)
        new_input = self.input_states[key].locals_

        for n,u in locals_.iteritems():
            if n not in new_input:
                # print "changed due to new name", n
                changed = True
                new_input[n] = u
            else:
                new_u = Union.make_union(new_input[n], u)
                # Try to avoid calling __ne__ I guess
                changed = changed or (new_u != new_input[n])
                new_input[n] = new_u

        if changed:
            self.mark_changed(key, not_dependent=True)

    def mark_changed(self, key, not_dependent=False):
        if not not_dependent:
            assert self._cur_key
            self._dependencies.setdefault(self._cur_key, set()).add(key)
        self.queue.mark_changed(key)

    def _do_basic_block(self, node, block_id):
        key = (node, block_id)
        self.errors[key] = {}

        state = self.input_states[key].copy()
        cfg = self.cfgs[node]
        scope = self.scopes[node]
        ast_utils.crawl_ast(cfg.blocks[block_id], Analyzer(self, scope, state), err_missing=True, fn=scope.filename())
        if DEBUG >= 2:
            for k,v in state.locals_.iteritems():
                assert isinstance(v, Union)
        return state

    class AnalysisQueue(object):
        def __init__(self):
            self.buffer = collections.deque()
            self.not_buffered = set()
            self.in_queue = set()
            self.last_run = {}
            self.time_est = {}

            self.prev_run = None
            self.prev_run_start = None

            self.scc = None
            self.scc_iteration = -1e9

        def mark_changed(self, k):
            if k in self.in_queue:
                return
            self.not_buffered.add(k)
            self.in_queue.add(k)

        def num_to_evaluate(self):
            return len(self.in_queue)

        def _fill_buffer(self, iteration, total, engine):
            NUM_TO_FILL = (500 + len(self.in_queue)) / 50
            ADD_REGARDLESS = 1e9
            MAX_SCC = len(engine._dependencies)

            FACTOR = 5
            if self.scc_iteration < iteration - (total + 500) / FACTOR:
                if VERBOSE:
                    print "calculating scc"
                scc, scc_nodes = engine._calc_scc()
                self.scc = scc
                self.scc_iteration = iteration

            priorities = []
            for k in self.not_buffered:
                if self.last_run.get(k, -1e9) < iteration - total:
                    p = ADD_REGARDLESS
                else:
                    p = MAX_SCC - self.scc.get(k, MAX_SCC) + 0.1 / (0.1 + self.time_est.get(k, 0))
                    # I feel like it should be beneficial to either prioritize running recent on non-recent nodes.  doesnt seem to be.
                    # p += 100.0 / (100.0 + iteration - self.last_run[k])

                priorities.append(((-p, random.random()), k))
            heapq.heapify(priorities)

            while priorities:
                k = heapq.heappop(priorities)[1]
                self.not_buffered.remove(k)
                self.buffer.append(k)

                if len(self.buffer) >= NUM_TO_FILL and (priorities and priorities[0][0] > -ADD_REGARDLESS):
                    break

        def get_next(self, iteration, total, engine):
            assert len(self.in_queue) == len(self.not_buffered) + len(self.buffer)

            if self.prev_run:
                elapsed = time.time() - self.prev_run_start
                if self.prev_run in self.time_est:
                    est = self.time_est[self.prev_run]
                else:
                    est = elapsed
                self.time_est[self.prev_run] = .5 * (elapsed + est)

            if not self.in_queue:
                return None

            if not self.buffer:
                self._fill_buffer(iteration, total, engine)

            r = self.buffer.popleft()
            self.in_queue.remove(r)
            self.last_run[r] = iteration
            self.prev_run = r
            self.prev_run_start = time.time()
            return r

    def analyze(self):
        success = True
        iterations = 0
        time_buckets = {}
        to_get = 0
        analyze_start = time.time()
        while True:
            if DEBUG >= 2:
                for k,v in self.input_states.iteritems():
                    assert v.queue_key == k, (k, v.queue_key)

            start = time.time()
            key = self.queue.get_next(iterations, len(self.input_states), self)
            to_get += (time.time() - start)
            if key is None:
                break

            node, block_id = key
            cfg = self.cfgs[node]
            if block_id == cfg.end:
                continue

            assert self._cur_key is None
            self._cur_key = (node, block_id)
            start = time.time()
            end_block_state = self._do_basic_block(node, block_id)
            elapsed = time.time() - start
            bucket = (int(100.0 * elapsed) * 10)
            time_buckets[bucket] = time_buckets.get(bucket, 0) + 1
            if elapsed > .1:
                print "slow block: %.1f ms at %s" % (1000.0 * elapsed, self._get_block_pos(self._cur_key))

            if DEBUG >= 2:
                assert not any(end_block_state is v for v in self.input_states.itervalues())

            next_nodes = cfg.connects_to[block_id]
            # TODO convert to all-at-once?
            for nid in next_nodes:
                self.update_input((node, nid), end_block_state.locals_)

            assert self._cur_key == (node, block_id)
            self._cur_key = None

            if DEBUG >= 2:
                for k,v in self.input_states.items():
                    for k2, v2 in self.input_states.items():
                        if v is v2:
                            assert k is k2

            iterations += 1
            # if iterations % 5000 == 0:
                # self.print_score()

            if iterations % 100 == 0:
                print "%d: %d / %d" % (iterations, self.queue.num_to_evaluate(), len(self.input_states))

        if DEBUG >= 1:
            for k,v in self.input_states.iteritems():
                assert v.queue_key == k, (k, v.queue_key)

        if DEBUG >= 1:
            # make sure types haven't changed since being annotated,
            # since that would imply a dependency failure
            for fn, annotations in self.annotations.iteritems():
                for (r,c), (t,s) in annotations.iteritems():
                    if t.display() != s:
                        print "WARNING"
                        print "At %s:%s:%s, got annotation:" % (fn, r, c)
                        print s
                        print "But type has been updated to"
                        print t.display()
                        print
                        success = False
        if DEBUG >= 2:
            for k,v in self.input_states.items():
                for k2, v2 in self.input_states.items():
                    if v is v2:
                        assert k is k2
        if VERBOSE:
            print "finished after %d iterations (%.2f evaluations/node)" % (iterations, 1.0 * iterations / len(self.input_states))
            for k in sorted(time_buckets):
                print "% 3dms: %s" % (k, time_buckets[k])
            print "Spent %.1fms calculating next node" % (1000.0 * to_get)
            source_len = sum(len(v) for v in self.sources.itervalues())
            total_elapsed = time.time() - analyze_start
            print "Analyzed %d LOC in %d basic blocks in %.1fs" % (source_len, len(self.input_states), total_elapsed)
            print "%.1f LOC/sec (%.1f BB/sec)" % (1.0 * source_len / total_elapsed, 1.0 * len(self.input_states) / total_elapsed)
        return success

    def load_modules(self, name, python_path):
        if not name:
            assert len(python_path) == 1
            [path] = python_path
            fn = os.path.join(path, "__init__.py")
            if not os.path.exists(fn):
                assert self._allow_import_errors, ("Error importing %s" % path)
                return []
            r = [self._load(fn, os.path.basename(path))]
            if not r[0]:
                assert self._allow_import_errors, ("Error importing %s" % path)
                return []
            return r

        assert name

        assert isinstance(name, str)
        to_load = name.split('.')

        found_path = None
        for p in python_path:
            fn = os.path.join(p, to_load[0])
            exist_fn = filter(os.path.exists, (os.path.join(fn, "__init__.py"), fn + ".py"))
            if exist_fn:
                found_path = p
                break
            elif filter(os.path.exists, (fn + ".pyc", fn + ".pyo")):
                print "WARNING: found only a pyc file for", fn

        if not found_path:
            names = name.split('.')
            if names[0] not in KNOWN_MODULES:
                assert self._allow_import_errors, ("Error importing %s; could not find and is not builtin" % names[0])
                return []
            modules = [KNOWN_MODULES[names[0]]]
            for n in names[1:]:
                m = modules[-1].get_name(n)
                if m is None:
                    assert self._allow_import_errors, ("Error importing %s, not present in module" % n)
                    return modules
                assert len(m.types()) == 1
                m = m.types()[0]
                if not isinstance(m, Module):
                    assert self._allow_import_errors, ("Error importing %s, not a module" % n)
                    return modules
                modules.append(m)
            return modules

        prev_m = None
        cur_path = found_path
        rtn = []
        for n in to_load:
            assert n, (to_load, name)
            fn = os.path.join(cur_path, n)
            exist_fn = filter(os.path.exists, (os.path.join(fn, "__init__.py"), fn + ".py"))
            if not exist_fn:
                if filter(os.path.exists, (fn + ".pyc", fn + ".pyo")):
                    print "WARNING: found only a pyc file for", fn
                assert self._allow_import_errors, ("Error importing %s, no such module" % n)
                return rtn
            fn = exist_fn[0]
            m = self._load(fn, n)
            if not m:
                assert self._allow_import_errors, ("Error importing %s, no such attribute" % n)
                break

            assert isinstance(m, Module)
            if prev_m:
                prev_m.setattr(n, Union(m))
            rtn.append(m)
            prev_m = m

            if fn.endswith("/__init__.py"):
                cur_path = os.path.dirname(fn)
            else:
                break
        return rtn

    def _load(self, fn, module_name=None):
        fn = os.path.abspath(fn)
        if module_name is None:
            module_name = re.search("([^/]+).py$", fn).group(1)
            assert module_name != "__init__", fn

        if not fn in self._loaded_modules:
            source = open(fn).read()
            self.load_source(fn, source)
            try:
                node = ast_utils.parse(source, fn)
                assert isinstance(node, _ast.Module), node
                assert not node in self.scopes
                t = Module(module_name, fn)
                self.scopes[node] = ModuleScope(fn, t)
                self.queue_scope(node)
                if VERBOSE:
                    print "loaded", fn
            except SyntaxError:
                print "failed to load %s due to a syntax error" % fn
                t = None

            self._loaded_modules[fn] = t

        t = self._loaded_modules[fn]
        if t:
            assert t.name == module_name, (t.name, module_name)
        return t

    def format_html(self, fn, link_func, static_dir=None):
        if PRETTY_DISPLAY:
            type_info = sorted((l,n,t.prettify().display()) for (l,n),(t,s) in self.annotations.get(fn, {}).iteritems())
        else:
            type_info = sorted((l,n,t.display()) for (l,n),(t,s) in self.annotations.get(fn, {}).iteritems())
        errors = {}
        for k in self.fn_to_blocks.get(fn, []):
            d = self.errors.get(k, {})
            for err_key, msg in d.iteritems():
                errors[err_key] = msg
        error_info = sorted((l,start,end,error) for (l,start,end),error in errors.iteritems())
        links = {}

        def gen_link(t):
            if isinstance(t, Module):
                if t.fn != "__builtin__":
                    links[(l,n)] = link_func(t.fn)
            elif t in self.type_definitions:
                t_fn, t_lineno = self.type_definitions[t]
                if t_fn == fn and l == t_lineno:
                    return
                links[(l, n)] = link_func(t_fn) + "#line%d" % t_lineno
            elif isinstance(t, InstanceMethod):
                gen_link(t._f)

        for (l,n),(u,s) in self.annotations.get(fn, {}).iteritems():
            if len(u.types()) == 1:
                [t] = u.types()
                gen_link(t)
        return annotate(fn, type_info, error_info, links, static_dir=static_dir)

    def _get_block_pos(self, k):
        fn = self.scopes[k[0]].filename()
        cfg = self.cfgs[k[0]]
        if k[1] == cfg.end:
            # lineno = cfg.blocks[cfg.end-1][-1].lineno
            lineno = "virtual_end"
        elif k[1] == cfg.start:
            if isinstance(k[0], _ast.Module):
                lineno = 0
            else:
                lineno = k[0].lineno
        else:
            block = cfg.blocks[k[1]]
            if hasattr(block[0], "not_real"):
                lineno = "virtual_added"
            else:
                lineno = block[0].lineno

        return (fn, lineno)

    def _calc_scc(self):
        scc, scc_nodes = get_scc(self._dependencies)
        return scc, scc_nodes

    def _test_calc_scc(self):
        edges = {}

        num_map = {}
        def getnum(k):
            if k not in num_map:
                num_map[k] = len(num_map)
            return num_map[k]

        for node in sorted(self.cfgs, key=lambda x: self._get_block_pos((x, 0))):
            cfg = self.cfgs[node]
            for nid in sorted(cfg.blocks):
                getnum((node, nid))
            getnum((node, cfg.start))
            getnum((node, cfg.end))
        for node, cfg in self.cfgs.iteritems():
            # edges.setdefault((node, cfg.start), set())
            # edges.setdefault((node, cfg.end), set())
            # for n1, s in cfg.connects_to.iteritems():
                # edges.setdefault((node, n1), set())
                # for n2 in s:
                    # edges[(node, n1)].add((node, n2))
            edges.setdefault(getnum((node, cfg.start)), set())
            edges.setdefault(getnum((node, cfg.end)), set())
            for n1, s in cfg.connects_to.iteritems():
                edges.setdefault(getnum((node, n1)), set())
                for n2 in s:
                    edges[getnum((node, n1))].add(getnum((node, n2)))
        for k, s in self._dependencies.iteritems():
            if k is None:
                continue
            for k2 in s:
                # edges[k].add(k2)
                edges[getnum(k)].add(getnum(k2))
        # assert edges == self._dependencies
        for k in edges:
            edges[k] = sorted(edges[k])

        assert None not in num_map
        key_map = {}
        for k, n in num_map.iteritems():
            key_map[n] = k

        scc, scc_nodes = get_scc(edges)

        print key_map
        print edges

        print hash(tuple(scc.items()))
        print scc_nodes

        # test_scc(scc, scc_nodes, edges)
        for n, s in edges.iteritems():
            for n2 in s:
                assert scc[n2] >= scc[n]

        node_linenos = {} # node num -> fn, lineno
        for k in num_map:
            pos = self._get_block_pos(k)
            # if pos[1] == "virtual":
                # continue
            node_linenos[num_map[k]] = pos

        for i, l in scc_nodes.iteritems():
            l2 = []
            for n in l:
                if n in node_linenos:
                    l2.append((node_linenos[n], n))
            if len(l2) > 5:
                print i
                for x in sorted(l2):
                    print x
                print

        def cost(sz):
            return sz ** 2
        print "original cost:", cost(len(edges))
        print "optimized cost:", sum(cost(len(c)) for c in scc_nodes.values())

    def add_overrides(self, overrides):
        # I get this wrong a surprising amount of the time:
        for k, v in overrides.iteritems():
            assert isinstance(v, Union)

        self.overrides.update(overrides)
        for k in self.input_states:
            self.mark_changed(k, not_dependent=True)

if __name__ == "__main__":
    fn = "test/2.py"
    if len(sys.argv) >= 2:
        fn = sys.argv[1]
    if len(sys.argv) >= 3:
        out_fn = sys.argv[2]
    else:
        out_fn = "/tmp/out.html"

    fn = os.path.abspath(fn)

    cfa.ADD_IF_ASSERTS = True

    success = True
    try:
        engine = Engine()

        engine.python_path.append(os.path.abspath(os.path.join(__file__, "../../../stdlib/type_mocks")))
        engine.python_path.append(os.path.abspath(os.path.join(__file__, "../../../stdlib/compiler")))
        # engine.python_path.append(os.path.abspath("/home/kmod/icbd_3rdparty/prod"))

        import plugins
        plugins.sqlalchemy.load(engine)
        plugins.pylons.load(engine)

        engine._load(fn, "__main__")
        success = engine.analyze() and success

        type_info = sorted((l,n,s) for (l,n),(t,s) in engine.annotations.get(fn, {}).iteritems())

        out_func = lambda fn:os.path.join("/tmp", os.path.basename(fn).replace(".py", ".html"))

        # Running it again:
        # TODO double-check that this doesn't do anything
        for i in xrange(ITERATIONS):
            old_type_info = list(type_info)
            print "running it again..."
            for k in engine.input_states:
                engine.mark_changed(k, not_dependent=True)
            success = engine.analyze() and success

            type_info = sorted((l,n,s) for (l,n),(t,s) in engine.annotations.get(fn, {}).iteritems())
            if type_info != old_type_info:
                print "WARNING"
                print "types changed after running again"
                print "new:"
                print set(type_info).difference(set(old_type_info))
                print "old:"
                print set(old_type_info).difference(set(type_info))
                print
                success = False


        def output(fn, out_fn=None):
            if out_fn is None:
                out_fn = out_func(fn)
            html = engine.format_html(fn, out_func)
            open(out_fn, 'w').write(html)
            print "%s -> %s (%s)" % (fn, out_fn, hashlib.sha1(html).hexdigest())

        output(fn, out_fn)
        for fn in engine._loaded_modules:
            output(fn)

        print
        engine.print_score(show_files=True, filter=lambda fn:"stdlib/type_mocks" not in fn)

        # engine._test_calc_scc()

    finally:
        # Union.__del__ = lambda self:None
        # Variable.__del__ = lambda self:None
        pass

    if not success:
        sys.exit(1)
