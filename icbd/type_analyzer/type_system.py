MAX_UNION_SIZE = 200
MAX_COMPLEXITY = 100
DEBUG_LISTENERS = 0
DEBUG = 1

import _ast
import collections
import sys
import traceback
import types as _types

class Union(object):
    __slots__ = ("_types",)

    def __init__(self, *types):
        if DEBUG:
            assert isinstance(types, tuple), repr(types)
            assert len(types) <= MAX_UNION_SIZE, [t.display() for t in types]
            for t in types:
                assert isinstance(t, Type), t
            assert len(set(types)) == len(types)
            if TOP in types:
                assert len(types) == 1

        self._types = types

    def __getstate__(self):
        return self._types

    def __setstate__(self, types):
        self._types = types

    # TODO replace things with this
    def types(self):
        return self._types

    def display(self):
        d = sorted([t.display() for t in self._types])
        # TODO do some display-time filtering of the list
        # ex filter out any subtypes (incl equivalent types)
        if len(d) == 0:
            return "<unknown>"
        if len(d) == 1:
            return d[0]
        return '<%s>' % ('|'.join(d))

    def __eq__(self, rhs):
        if not isinstance(rhs, Union):
            return False
        return sorted(self._types) == sorted(rhs._types)

    # Apparently this adds overhead...
    # def __ne__(self, rhs):
        # return not (self == rhs)

    def __ne__(self, rhs):
        if not isinstance(rhs, Union):
            return True
        return sorted(self._types) != sorted(rhs._types)

    def __hash__(self):
        raise Exception()

    def getattr(self, attr, context):
        return Union.make_union(*[v.getattr(attr, context) for v in self._types])
        r = []
        for t in self._types:
            u = t.getattr(attr, context)
            assert isinstance(u, Union), t
            r.append(u)
        return Union.make_union(*r)

    def setattr(self, attr, v):
        for t in self._types:
            t.setattr(attr, v)

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        return Union.make_union(*[v.call(args, keywords, starargs, context, dryrun, orig_args) for v in self._types])

    def add_listener(self, l):
        for t in self._types:
            t.add_listener(l)

    def score(self):
        if not self._types:
            return 0
        return sum(t.score() for t in self._types) / len(self._types) ** 2

    def prettify(self):
        new_t = []
        # (cls, nunions) -> instance
        instances = {}
        # TODO filter out ClassTypes that are subtypes of other ones

        if TOP in self.types():
            return Union(TOP)

        for t in self.types():
            if t.is_custom():
                new_t.append(t)
                continue

            if not isinstance(t, InstanceType):
                if isinstance(t, FixedFunction):
                    # t = FixedFunction([u.prettify() for u in t._args], t._rtn.prettify(), {}, defaults=t._defaults)
                    pass
                elif isinstance(t, InstanceMethod):
                    # TODO hax
                    t = InstanceMethod(Union(t._f).prettify().types()[0], Union(t._bind).prettify().types()[0])
                elif isinstance(t, (ConstType, Param)):
                    pass
                elif isinstance(t, (ClassType,)):
                    pass
                elif isinstance(t, (Module,)):
                    pass
                elif isinstance(t, (SpecialFunction,)):
                    pass
                elif isinstance(t, PolymorphicFunction):
                    pass
                elif isinstance(t, (ClassMethod,)):
                    pass
                else:
                    raise Exception(t)
                new_t.append(t)
                continue

            key = (t.cls, len(t.unions), (t.cls is UserFunctionClass and t.is_generator))
            if not key in instances:
                # TODO dont really care about fixedfunctions vs userfunctions
                if t.cls is UserFunctionClass:
                    instances[key] = UserFunction(t.arg_names, [Union.EMPTY for u in t.unions[:len(t.arg_names)]], t.ndefault, t.unions[t.vararg_idx] if t.vararg else None, t.unions[t.kwarg_idx] if t.kwarg else None, t.unions[t.rtn_idx], temp=True, is_generator=t.is_generator)
                elif isinstance(t, SuperInstanceType):
                    # TODO this won't look right
                    # TODO superhax
                    instances[key] = SuperInstanceType(getattr(t, "_SuperInstanceType__cls"), getattr(t, "_SuperInstanceType__inst"), temp=True)
                else:
                    instances[key] = InstanceType(t.cls, [Union.EMPTY for u in t.unions], temp=True)
            t2 = instances[key]

            assert len(t2.unions) == len(t.unions), (t.display(), t2.display())
            for i in xrange(len(t.unions)):
                t2.update(i, t.unions[i], allow_vars=1)

        for (c, _, _), t in instances.iteritems():
            is_subclass = False
            for (c2, _, _) in instances.iterkeys():
                if c is c2:
                    continue
                if c.is_subclass_of(c2):
                    is_subclass = True
                    break
            # TODO not sure if I should turn this on or not
            # if is_subclass:
                # continue

            for i in xrange(len(t.unions)):
                t.unions[i] = t.unions[i].prettify()
            new_t.append(t)

        d = {}
        for t in new_t:
            d[t.display()] = t
        return Union(*d.values())

    @staticmethod
    def make_union(*unions):
        if not unions:
            return Union.EMPTY
        if len(unions) == 1:
            return unions[0]

        for u in unions:
            assert isinstance(u, Union), u

        types = set()
        for u in unions:
            types.update(u._types)

        if not types:
            return Union.EMPTY

        # Taking this out won't matter for forward-propagation, but it might help us make inferences
        if TOP in types:
            return Union(TOP)

        if len(types) >= 2 and NONE in types:
            types.remove(NONE)

        if FLOAT in types and INT in types:
            types.remove(INT)

        if len(types) > MAX_UNION_SIZE:
            return Union(TOP)

        if len(types) > 1 and sum(complexity(t) for t in types) > MAX_COMPLEXITY:
            return Union(TOP)

        return Union(*types)

class Type(object):
    def __init__(self):
        self.__listeners = set()
        if DEBUG_LISTENERS:
            self.stacks = {}

    def __getstate__(self):
        rtn = dict(self.__dict__)
        for k, v in rtn.iteritems():
            if k.endswith('listeners'):
                assert hasattr(v, '__iter__')
                rtn[k] = []
        for n in ('display_func', '_display_func'):
            if n in rtn:
                del rtn[n]
        return rtn

    def is_custom(self):
        return False

    def add_listener(self, l):
        assert l
        assert callable(l), l

        if l in self.__listeners:
            return
        self.__listeners.add(l)
        # if len(self.__listeners) > 50:
            # traceback.print_stack()
            # print
        if DEBUG_LISTENERS and len(self.__listeners) > 0:
            st = ''.join(traceback.format_stack(limit=6)[:-1])
            self.stacks[st] = self.stacks.get(st, 0) + 1
            if len(self.__listeners) % 1000 == 0:
                print '*'*100
                for s, n in sorted(self.stacks.iteritems(), key=lambda (s,n):n):
                    print n
                    print s
                    print
                print len(self.stacks), repr(self), self.display()
                sys.exit(-1)
        assert len(self.__listeners) < 10000, (self, type(self), self.display()) # just a sanity check

    def fire_listeners(self):
        for l in self.__listeners:
            l()

    def __repr__(self):
        return "<%s>" % (type(self).__name__,)

class ConstType(Type):
    def __init__(self):
        type(self).__init__ = None
        super(ConstType, self).__init__()
        self._cached_attrs = {}

    def add_listener(self, l):
        pass

    def setattr(self, attr, value):
        # TODO this should be an error
        pass

    def getattr(self, attr, context):
        # call _getattr even if we already got it, to preserve errors
        # TODO probably can do this more efficiently
        if isinstance(attr, tuple):
            return Union.make_union(*[self.getattr(a, context) for a in attr])
        assert isinstance(attr, str)

        r = self._getattr(attr, context)
        if not attr in self._cached_attrs:
            self._cached_attrs[attr] = r
        return self._cached_attrs[attr]

    def score(self):
        return 1.0

class TopType(ConstType):
    def display(self):
        return "<mixed>"

    def score(self):
        return 0.0

    def _getattr(self, attr, context):
        if attr in "__eq__":
            return Union(FixedFunction([ANY], BOOL))

        # context.log_error("%s not guaranteed to have %s" % (self.display(), attr))
        return Union(TOP)

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        # context.log_error("%s not guaranteed to be callable" % (self.display(),))
        return Union(TOP)
TOP = TopType()

# Union.__init__ depends on TOP
Union.EMPTY = Union()

class BoolType(ConstType):
    def display(self):
        return "bool"

    def _getattr(self, attr, context):
        if attr == "__nonzero__":
            return Union(FixedFunction([], BOOL))

        if attr in ("__eq__", "__neq__"):
            return Union(FixedFunction([BOOL], BOOL))

        if attr in ("__or__", "__and__", "__ior__"):
            return Union(FixedFunction([BOOL], BOOL))

        context.log_error("%s has no attr '%s'" % (self, attr))
        return Union.EMPTY

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        context.log_error("why did you call %s?" % (self.display(),))
        return Union.EMPTY

BOOL = BoolType()

class StrType(ConstType):
    def display(self):
        return "str"

    def _getattr(self, attr, context):
        if attr == "__getitem__":
            return Union(PolymorphicFunction(
                FixedFunction([INT], STR),
                FixedFunction([SLICE], STR),
            ))

        if attr in ("lower", "upper"):
            return Union(FixedFunction([], STR))
        if attr in ("strip", "rstrip"):
            return Union(FixedFunction([STR], STR, ndefaults=1))
        if attr in ("__mul__", "ljust", "rjust"):
            return Union(FixedFunction([INT], STR))
        if attr in ("split",):
            return Union(FixedFunction([STR, INT], InstanceArg(ListClass, [STR]), ndefaults=2))
        if attr == "__iter__":
            return Union(FixedFunction([], InstanceArg(Iterator, [STR])))
        if attr in ("__add__", "__iadd__"):
            return Union(FixedFunction([STR], STR))
        if attr in ("replace",):
            return Union(FixedFunction([STR, STR, INT], STR, ndefaults=1))
        if attr in ("__eq__", "__ne__",):
            return Union(FixedFunction([ANY], BOOL))
        # TODO strs can probably be compared to anything, but that's probably an error
        if attr in ("__contains__", "__le__", "__lt__", "__ge__", "__gt__", "startswith", "endswith"):
            return Union(FixedFunction([STR], BOOL))
        if attr in ("__nonzero__", "isalpha", "isspace", "isdigit", "isalnum", "islower", "istitle", "isupper"):
            return Union(FixedFunction([], BOOL))
        if attr == "__mod__":
            return Union(FixedFunction([ANY], STR))
        if attr == "join":
            return Union(FixedFunction([Subtype(InstanceArg(Iterable, [STR]))], STR))
        if attr in ("find", "count", "rfind"):
            return Union(FixedFunction([STR, INT, INT], INT, ndefaults=2))
        if attr == "splitlines":
            return Union(FixedFunction([BOOL], InstanceArg(Iterable, [STR]), ndefaults=1))
        if attr == "encode":
            return Union(FixedFunction([STR, STR], STR, ndefaults=2))

        context.log_error("%s has no attr '%s'" % (self, attr))
        return Union.EMPTY

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        context.log_error("why did you call %s?" % (self.display(),))
        return Union.EMPTY

STR = StrType()

class FloatType(ConstType):
    def display(self):
        return "float"

    def _getattr(self, attr, context):
        if attr in ["__%s__" % s for s in ("add", "mul", "sub", "pow", "mod", "div", "floordiv")]:
            return Union(FixedFunction([FLOAT], FLOAT))
        if attr in ["__i%s__" % s for s in ("add", "mul", "sub", "pow", "mod", "div", "floordiv")]:
            return Union(FixedFunction([FLOAT], FLOAT))

        if attr in ["__%s__" % s for s in ("neg", "pos", "invert")]:
            return Union(FixedFunction([], FLOAT))
        if attr == "__nonzero__":
            return Union(FixedFunction([], BOOL))

        if attr in ("__iadd__", "__imul__", "__isub__"):
            return Union(FixedFunction([FLOAT], FLOAT))

        if attr in ("__eq__", "__ne__",):
            return Union(FixedFunction([ANY], BOOL))
        # TODO nums can probably be compared to anything, but that's probably an error
        if attr in ("__le__", "__lt__", "__ge__", "__gt__"):
            return Union(FixedFunction([FLOAT], BOOL))

        context.log_error("%s has no attr '%s'" % (self, attr))
        return Union.EMPTY

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        context.log_error("why did you call %s?" % (self.display(),))
        return Union.EMPTY

FLOAT = FloatType()

class IntType(ConstType):
    def display(self):
        return "int"

    def _getattr(self, attr, context):
        if attr in ["__%s__" % s for s in ("add", "mul", "sub", "pow", "mod", "div", "floordiv")]:
            return Union(PolymorphicFunction(
                FixedFunction([INT], INT),
                FixedFunction([FLOAT], FLOAT),
            ))
        if attr in ["__i%s__" % s for s in ("add", "mul", "sub", "pow", "mod", "div", "floordiv")]:
            return Union(FixedFunction([INT], INT))
        if attr in ["__%s__" % s for s in ("and", "or", "xor", "lshift", "rshift")]:
            return Union(FixedFunction([INT], INT))
        if attr in ["__i%s__" % s for s in ("and", "or", "xor", "lshift", "rshift")]:
            return Union(FixedFunction([INT], INT))

        if attr in ["__%s__" % s for s in ("neg", "pos", "invert")]:
            return Union(FixedFunction([], INT))
        if attr == "__nonzero__":
            return Union(FixedFunction([], BOOL))

        if attr in ("__iadd__", "__imul__", "__isub__"):
            return Union(FixedFunction([INT], INT))

        if attr in ("__eq__", "__ne__",):
            return Union(FixedFunction([ANY], BOOL))
        # TODO nums can probably be compared to anything, but that's probably an error
        if attr in ("__le__", "__lt__", "__ge__", "__gt__"):
            return Union(FixedFunction([FLOAT], BOOL))

        context.log_error("%s has no attr '%s'" % (self, attr))
        return Union.EMPTY

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        context.log_error("why did you call %s?" % (self.display(),))
        return Union.EMPTY

INT = IntType()

class SliceType(ConstType):
    def display(self):
        return "slice"

    def _getattr(self, attr, context):
        if attr == "__nonzero__":
            return Union(FixedFunction([], BOOL))

        context.log_error("%s has no attr '%s'" % (self, attr))
        return Union.EMPTY

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        context.log_error("why did you call %s?" % (self.display(),))
        return Union.EMPTY

SLICE = SliceType()

class NoneType(ConstType):
    def display(self):
        return "None"

    def _getattr(self, attr, context):
        if attr == "__nonzero__":
            return Union(FixedFunction([], BOOL))

        if attr in ("__eq__", "__ne__"):
            context.log_warning("use 'is' or 'not is' to compare against None")
            return Union(FixedFunction([ANY], BOOL))

        context.log_error("%s has no attr '%s'" % (self, attr))
        return Union.EMPTY

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        context.log_error("why did you call %s?" % (self.display(),))
        return Union.EMPTY

NONE = NoneType()

def get_iter_type(t, context):
    assert isinstance(t, Union), t
    if len(t.types()) == 0:
        return Union.EMPTY

    # TODO reusing context??
    iter_f = t.getattr("__iter__", context)
    if len(iter_f.types()) == 0:
        context.log_error("'%s' is not iterable" % (t.display(),))
        return Union.EMPTY
    iter = iter_f.call([], {}, None, context, False, None)

    next_f = iter.getattr("next", context)
    elt_type = next_f.call([], {}, None, context, False, None)

    return elt_type

def make_subtype3(spec, to_fit, d, context):
    if isinstance(spec, Var):
        u = Union.make_union(d.get(spec.id, Union.EMPTY), to_fit)
        d[spec.id] = u
        return

    if isinstance(spec, InstanceArg):
        if spec.cls is Iterable:
            elt_type = get_iter_type(to_fit, context)
            assert len(spec.args) == 1
            make_subtype3(spec.args[0], elt_type, d, context)
            return

        for a in spec.args:
            make_subtype3(a, Union.EMPTY, d, context)

        for t in to_fit.types():
            if not isinstance(t, InstanceType):
                if context:
                    context.log_error("Unable to cast %s as %s (not an instance)" % (t.display(), spec.cls.name))
                continue
            if spec.cls not in t.cls._mro:
            # if spec.cls != t.cls:
                if context:
                    context.log_error("Unable to cast %s as %s (not same class)" % (t.display(), spec.cls.name))
                continue
            if len(spec.args) != len(t.unions):
                if context:
                    context.log_error("Unable to cast %s as %s (not same parametricity)" % (t.display(), spec.cls.name))
                continue

            for i in xrange(len(spec.args)):
                make_subtype3(spec.args[i], t.unions[i], d, context)
        return

    if isinstance(spec, ConstType):
        if Union(spec) != to_fit and not (spec is FLOAT and to_fit == Union(INT)):
            context.log_error("Unable to cast %s to %s (wrong const type)" % (to_fit.display(), spec.display()))
        return

    raise Exception(spec)

def make_fit3(spec, to_fit, d, context, dryrun=False, allow_new=False):
    assert isinstance(spec, (Arg, ConstType))
    assert isinstance(to_fit, Union)

    if isinstance(spec, InstanceArg):
        assert spec.cls != Iterable, "You probably wanted this to be a subtype"
        rtn = []
        for t in to_fit.types():
            if not isinstance(t, InstanceType):
                if context:
                    context.log_error("Unable to cast %s as %s (not an instance)" % (t.display(), spec.cls.name))
                continue
            if spec.cls not in t.cls._mro:
                if context:
                    context.log_error("Unable to cast %s as %s (not same class)" % (t.display(), spec.cls.name))
                continue

            if t.unions is None:
                assert spec.update, spec.cls.name
                if not dryrun:
                    t.unions = [Union.EMPTY for a in spec.args]

            if isinstance(t.cls, UserClassType):
                unions = [Union(TOP) for a in spec.args]
            else:
                unions = t.unions
                if unions is None:
                    assert dryrun
                    unions = [Union.EMPTY for a in spec.args]

            if len(spec.args) != len(unions):
                if context:
                    context.log_error("Unable to cast %s as %s (not same parametricity)" % (t.display(), spec.cls.name))
                continue

            for i in xrange(len(spec.args)):
                u = make_fit3(spec.args[i], unions[i], d, context, dryrun=dryrun, allow_new=True)
                if u != unions[i]:
                    if spec.update:
                        if not dryrun and not isinstance(t.cls, UserClassType):
                            t.update(i, u)
                    else:
                        # print [(_n, _t.display()) for (_n, _t) in d.items()]
                        if context:
                            context.log_error("Unable to cast %s as %s (arg %s)" % (t.display(), evaluate3(spec, d, None, allow_vars=True).display(), i))
                            # context.log_error("Unable to cast %s as %s (arg %s)" % (t.display(), spec.display(), i))
            rtn.append(t)
        return Union(*rtn)

    if isinstance(spec, Var):
        u = Union.make_union(d.get(spec.id, Union.EMPTY), to_fit)
        d[spec.id] = u
        if u != to_fit and not allow_new:
            if context:
                context.log_error("Unable to match %s to %s (set to %s)" % (to_fit.display(), spec.display(), u.display()))
        return u

    if isinstance(spec, Subtype):
        make_subtype3(spec.a, to_fit, d, context)
        return to_fit

    if isinstance(spec, ConstType):
        u = Union.make_union(Union(spec), to_fit)
        # if u != Union(spec) and not allow_new:
        if u != Union(spec) and not allow_new and not (spec is FLOAT and to_fit == Union(INT)):
            if context:
                context.log_error("Unable to fit %s into %s" % (to_fit.display(), spec.display()))
        return u
        # return Union(spec)

    if isinstance(spec, FixedArg):
        u = Union.make_union(spec.u, to_fit)
        if u != spec.u and not allow_new and not (spec.u == Union(FLOAT) and to_fit == Union(INT)):
            if context:
                context.log_error("Unable to fit %s into %s" % (to_fit.display(), spec.u.display()))
        return u

    raise Exception(spec)

def evaluate3(spec, d, context, allow_vars=False, default_bottom=False):
    assert isinstance(spec, (Arg, ConstType))
    assert not (allow_vars and default_bottom)

    if allow_vars:
        # This is because if context is not none, this is real (not temp) object, so we shouldnt put vars in it
        assert context is None

    if isinstance(spec, ConstType):
        return Union(spec)

    if isinstance(spec, Var):
        if spec.id in d:
            return d[spec.id]
        elif allow_vars:
            return Union(Param(spec.id))
        elif default_bottom:
            return Union.EMPTY
        context.log_error("internal error, didn't get type for var %s" % (spec.display(),))
        return Union.EMPTY

    if isinstance(spec, InstanceArg):
        if not context:
            assert allow_vars
            t = InstanceType(spec.cls, [Union.EMPTY for u in spec.args], temp=True)
        elif context.get_cached(spec):
            t = context.get_cached(spec)
            assert isinstance(t, InstanceType)
            assert t.cls is spec.cls
            assert len(t.unions) == len(spec.args)
        else:
            t = InstanceType(spec.cls, [Union.EMPTY for u in spec.args])
            # context.register_definition(t)
            context.set_cached(spec, t)

        if allow_vars:
            assert t.temp

        for i in xrange(len(spec.args)):
            t.update(i, evaluate3(spec.args[i], d, context, allow_vars=allow_vars, default_bottom=default_bottom), allow_vars=allow_vars)

        return Union(t)

    if isinstance(spec, Subtype):
        # TODO ensure this is only used for display purposes
        return evaluate3(spec.a, d, context, allow_vars=allow_vars, default_bottom=default_bottom)

    if isinstance(spec, FixedArg):
        return spec.u

    raise Exception(spec)

class InstanceMethod(Type):
    def __init__(self, f, bind):
        assert isinstance(f, (FixedFunction, UserFunction, PolymorphicFunction, SpecialFunction))
        assert isinstance(bind, (ClassType, InstanceType))
        if DEBUG:
            assert not has_params(bind)
        super(InstanceMethod, self).__init__()
        self._f = f
        self._bind = bind

        # TODO not sure if these are necessary?
        self._f.add_listener(self.fire_listeners)
        self._bind.add_listener(self.fire_listeners)

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        if isinstance(self._bind, InstanceType):
            return self._f.call([Union(self._bind)] + args, keywords, starargs, context, dryrun, orig_args)
        else:
            assert isinstance(self._bind, ClassType)
            if len(args) < 1:
                context.log_error("Unbound method expected arguments")
                return Union.EMPTY
            for t in args[0].types():
                if not isinstance(t, InstanceType) or not self._bind in t.cls._mro:
                    context.log_error("Expected instance of type %s, but got %s" % (self._bind.name, t.display()))
                    return Union.EMPTY
            return self._f.call(args, keywords, starargs, context, dryrun, orig_args)

    def display(self):
        # return "instancemethod %s" % (self._bind.display())
        if isinstance(self._bind, ClassType):
            return self._f.display()

        if isinstance(self._f, FixedFunction):
            return self._f.im_display(self._bind)
        elif isinstance(self._f, UserFunction):
            return self._f.display(bound=True)
        elif isinstance(self._f, SpecialFunction):
            return self._f.display(bind=self._bind)
        else:
            assert isinstance(self._f, PolymorphicFunction), self._f
            return self._f.display(bound=True)

    def getattr(self, attr, context):
        context.log_error("not implemented")
        return Union.EMPTY

    def score(self):
        return .5 * (self._f.score() + self._bind.score())

    def setattr(self, attr, v):
        # TODO should log an error here
        pass

class ClassMethod(Type):
    def __init__(self, f, cls):
        assert isinstance(f, Union), f
        assert isinstance(cls, ClassType)

        super(ClassMethod, self).__init__()

        self._f = f
        self._cls = cls

        self._f.add_listener(self.fire_listeners)
        self._cls.add_listener(self.fire_listeners)

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        return self._f.call([Union(self._cls)] + args, keywords, starargs, context, dryrun, orig_args)

    def display(self):
        d = []
        for t in self._f.types():
            if isinstance(t, FixedFunction):
                d.append(t.im_display(self._cls))
            elif isinstance(t, UserFunction):
                d.append(t.display(bound=True))
            else:
                assert isinstance(t, PolymorphicFunction), t
                d.append(t.display(bound=True))
        # TODO copy-pasted from Union.display
        if len(d) == 0:
            return "<unknown>"
        if len(d) == 1:
            return d[0]
        return '<%s>' % ('|'.join(d))

    def getattr(self, attr, context):
        context.log_error("not implemented2")
        return Union.EMPTY

    def score(self):
        return .5 * (self._f.score() + self._cls.score())


class FakeContext(object):
    def __init__(self, context):
        self.context = context
        self.errors = []

    def listener(self):
        return self.context.listener()

    def get_cached(self, key):
        return self.context.get_cached(key)

    def set_cached(self, key, value):
        return self.context.set_cached(key, value)

    def register_definition(self, t):
        return self.context.register_definition(t)

    def log_error(self, error):
        self.errors.append(error)

    def clear_locals(self):
        pass

class PolymorphicFunction(Type):
    def __init__(self, *fs):
        for f in fs:
            assert isinstance(f, (FixedFunction, SpecialFunction))
        super(PolymorphicFunction, self).__init__()
        self._fs = fs

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        assert not dryrun
        ctx = FakeContext(context)

        errors = []
        rs = []
        for f in self._fs:
            r = f.call(args, keywords, starargs, ctx, True, orig_args)
            if not ctx.errors:
                return f.call(args, keywords, starargs, context, False, orig_args)
            else:
                # print f.display()
                # print ctx.errors
                rs.append(r)
                errors += ctx.errors
                ctx.errors = []
        context.log_error("None of %s matched arguments %s" % (', '.join(f.display() for f in self._fs), ','.join(a.display() for a in args)))
        return Union.EMPTY

    def getattr(self, attr, context):
        context.log_error("not implemented")
        return Union.EMPTY

    def display(self, bound=False):
        return "<polymorphic>"

    def score(self):
        if not self._fs:
            return 0
        return sum(f.score() for f in self._fs) / len(self._fs)

class FixedFunction(Type):
    def __init__(self, args, rtn, ndefaults=None, defaults=None, arg_names=None, implicit_behavior_funcs=None):
        assert isinstance(rtn, (Arg, ConstType))
        for a in args:
            assert isinstance(a, (Arg, ConstType))
        assert ndefaults is None or isinstance(ndefaults, int), ndefaults
        if arg_names is None:
            arg_names = [""] * len(args)
        assert len(arg_names) == len(args)

        super(FixedFunction, self).__init__()

        self._args = args
        self._arg_names = arg_names
        self._rtn = rtn

        self._defaults = []
        if ndefaults is not None and ndefaults:
            assert defaults is None
            self._defaults = self._args[-ndefaults:]
            assert len(self._defaults) == ndefaults, (len(self._defaults), ndefaults, arg_names)
        if defaults is not None:
            assert ndefaults is None
            self._defaults = defaults
            assert len(self._defaults) <= len(self._args)
        for d in self._defaults:
            assert isinstance(d, (Arg, ConstType))

        self.implicit_behavior_funcs = implicit_behavior_funcs or []

    def add_listener(self, l):
        pass

    def getattr(self, attr, context):
        context.log_error("%s has no attr '%s'" % ("function", attr))
        return Union.EMPTY

    def im_bind(self, bind):
        assert isinstance(bind, InstanceType)
        if DEBUG:
            assert not has_params(bind), (self.display(), bind.display())
        d = {}
        bind = Union(bind)
        # TODO code duplication with call() and UserFunction

        while True:
            old_d = dict(d)
            make_fit3(self._args[0], bind, d, None)

            if old_d == d:
                break

        ev_args = [evaluate3(t, d, None, allow_vars=True) for t in self._args[1:]]
        ev_rtn = evaluate3(self._rtn, d, None, allow_vars=True)
        return ev_args, ev_rtn

    def im_display(self, bind):
        ev_args, ev_rtn = self.im_bind(bind)
        return function_display(ev_args, len(self._defaults), None, None, ev_rtn)

    def display(self):
        return function_display(self._args, len(self._defaults), None, None, self._rtn)

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        # probably not strictly necessary, but probably never wrong
        self.add_listener(context.listener())

        try:
            args, keywords, vararg = translate_call(args, keywords, starargs, self._arg_names, len(self._defaults), None, context)
        except _FuncArgsError, e:
            context.log_error(e.message)
            return evaluate3(self._rtn, {}, context, default_bottom=True)

        if keywords:
            context.log_error("Didn't expect to get keyword arguments %s" % (', '.join(keywords.keys())))
            # TODO is it right to just ignore them for now?

        assert not vararg
        for i in xrange(len(args)):
            if args[i] is None:
                assert i >= len(self._args) - len(self._defaults)
                # TODO this is bad
                args[i] = evaluate3(self._defaults[i + len(self._defaults) - len(self._args)], {}, context, default_bottom=True)
            assert isinstance(args[i], Union)
        assert len(args) == len(self._args)
        narg = len(args)

        d = {}
        args = list(args)

        while True:
            old_d = dict(d)
            for i in xrange(narg):
                make_fit3(self._args[i], args[i], d, context, dryrun=dryrun)
                assert isinstance(args[i], Union)
                # assert new_arg == args[i]

            if d == old_d:
                break

        evaluated_args = [evaluate3(a, d, context) for a in self._args]
        for f in self.implicit_behavior_funcs:
            f(evaluated_args, context)

        return evaluate3(self._rtn, d, context)

    def score(self):
        return 1.0

class SpecialFunction(Type):
    def __init__(self, f, display_func=None):
        assert callable(f)
        if not display_func:
            display_func = lambda t: "<special:%s>" % (f)
        assert callable(display_func)
        super(SpecialFunction, self).__init__()
        self._f = f
        self._d = display_func

    def getattr(self, attr, context):
        context.log_error("have no idea how to getattr from a specialfunction")
        return Union.EMPTY

    def add_listener(self, l):
        pass

    def score(self):
        return 1.0

    def display(self, bind=None):
        return self._d(bind)

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        return self._f(args, keywords, starargs, context, dryrun, orig_args)

# Bootstrapping hack:
# need to initialize the UserFunctionClass before the initial object class is created.  shouldn't be an issue?
UserFunctionClass = None
SuperClass = None
class InstanceType(Type):
    def __init__(self, cls, unions, temp=False):
        assert isinstance(cls, ClassType), (cls, type(cls), type(cls).mro())
        if cls is UserFunctionClass:
            assert isinstance(self, UserFunction), type(self)
        # if cls is ModuleClass:
            # assert isinstance(self, Module)
        if cls is SuperClass:
            assert isinstance(self, SuperInstanceType)
        if cls is Iterator:
            assert len(unions) == 1, unions
        if unions is not None:
            for u in unions:
                assert isinstance(u, Union), u
        super(InstanceType, self).__init__()
        self.cls = cls
        self.unions = unions

        if unions is not None:
            for u in unions:
                assert not has_reference(u, self)

        self._cached_attrs = {}
        self._attrs = {}

        self.__firing = False

        self.temp = temp
        if not temp:
            if unions is not None:
                for u in unions:
                    u.add_listener(self.fire_listeners)
            cls.add_name_listener(None, self.fire_name_listeners)

        self.__name_listeners = {}
        self.__sub_listeners = set()

    def update(self, argn, u, allow_vars=False):
        assert 0 <= argn < len(self.unions), (argn, len(self.unions))
        assert isinstance(u, Union), u

        if has_reference(u, self):
            u = Union(TOP)

        if not allow_vars and DEBUG:
            assert not has_params(u), (self.display(), u.display())

        if not self.temp:
            u.add_listener(self.fire_listeners)

        old_u = self.unions[argn]
        self.unions[argn] = Union.make_union(u, self.unions[argn])
        changed = (old_u != self.unions[argn])

        if changed:
            self.fire_listeners()

    def add_name_listener(self, name, l):
        assert isinstance(name, str) or name is None
        assert callable(l)
        if name:
            self.__name_listeners.setdefault(name, set()).add(l)
        else:
            self.__sub_listeners.add(l)

    def fire_name_listeners(self, name):
        for l in self.__name_listeners.get(name, []):
            l()
        for l in self.__sub_listeners:
            l(name)

    def fire_listeners(self):
        if not self.__firing:
            self.__firing = True
            super(InstanceType, self).fire_listeners()
            self.__firing = False

    def display(self):
        if self.unions is None:
            return "<half-created '%s'>" % (self.cls.name,)
        return self.cls._display_func(self.unions)

    def setattr(self, attr, v):
        assert isinstance(attr, str)
        assert isinstance(v, Union)
        old = self._attrs.get(attr)
        self._attrs[attr] = Union.make_union(self._attrs.get(attr, Union.EMPTY), v)
        if old != self._attrs[attr]:
            self.fire_name_listeners(attr)

    def get_name(self, attr, context):
        if isinstance(attr, tuple):
            for a in attr:
                v = self.get_name(a, context)
                if v:
                    return v
            return None
        assert isinstance(attr, str)
        self.add_name_listener(attr, context.listener())
        return self._attrs.get(attr)

    def getattr(self, attr, context):
        if attr == "__class__":
            return Union(self.cls)
        v = self.get_name(attr, context)
        if v is not None:
            return v

        # TODO shouldn't special-case this, but I'm not sure how common it'll be
        if self.cls is TupleClass:
            # TODO these don't handle when self.unions gets updated
            if attr == "__iter__":
                if "__iter__" not in self._cached_attrs:
                    self._cached_attrs["__iter__"] = FixedFunction([], InstanceArg(Iterator, [FixedArg(Union.make_union(*self.unions))]))
                return Union(self._cached_attrs["__iter__"])
            if attr == "__contains__":
                if "__iter__" not in self._cached_attrs:
                    self._cached_attrs["__iter__"] = FixedFunction([FixedArg(Union.make_union(*self.unions))], BOOL)
                return Union(self._cached_attrs["__iter__"])

        u = self.cls.get_name(attr, context.listener())
        if u is None:
            context.log_error("%s has no attribute %s" % (self.display(), attr))
            u = Union.EMPTY

        return bindall(self, u, self._cached_attrs, context)

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        # probably not strictly necessary, but probably never wrong
        self.add_listener(context.listener())

        return self.getattr("__call__", context).call(args, keywords, starargs, context, dryrun, orig_args)

    def score(self):
        return (self.cls.score() + sum(u.score() for u in self.unions)) / (1.0 + len(self.unions))

def bindall(bind, u, bind_cache, context):
    assert isinstance(bind, (ClassType, InstanceType))
    assert isinstance(u, Union), u
    rtn = []
    for t in u.types():
        if t in bind_cache:
            rtn.append(Union(bind_cache[t]))
            continue

        if isinstance(t, (FixedFunction, UserFunction, PolymorphicFunction, SpecialFunction)):
            r = InstanceMethod(t, bind)
        elif isinstance(t, InstanceType) and t.cls is ClassMethodClass:
            if isinstance(bind, InstanceType):
                r = ClassMethod(t.unions[0], bind.cls)
            else:
                r = ClassMethod(t.unions[0], bind)
        elif isinstance(t, InstanceType) and t.cls is StaticMethodClass:
            assert len(t.unions) == 1
            rtn.append(t.unions[0])
            continue
        elif isinstance(t, InstanceType) and t.cls is PropertyClass:
            assert len(t.unions) == 1
            r = bindall(bind, t.unions[0], bind_cache, context).call([], {}, None, context, False, None)
            rtn.append(r)
            continue
        else:
            r = t

        bind_cache[t] = r
        rtn.append(Union(r))
    return Union.make_union(*rtn)

# TODO this is very similar to an Instance.  some differences though (no function->instancemethod conversion)
class Module(Type):
    __created = set()
    def __init__(self, name, fn):
        assert fn.startswith('/') or fn == "__builtin__", fn
        if fn == "__builtin__":
            key = fn + name
        else:
            key = fn
        assert not key in Module.__created, (Module.__created, name, fn)
        Module.__created.add(key)

        assert isinstance(name, str)
        assert isinstance(fn, str)

        super(Module, self).__init__()
        self.name = name
        self.fn = fn

        self._attrs = {}

        self.__name_listeners = {}
        self.__sub_listeners = set()

    def add_name_listener(self, name, l):
        assert isinstance(name, str) or name is None
        assert callable(l)
        if name:
            self.__name_listeners.setdefault(name, set()).add(l)
        else:
            self.__sub_listeners.add(l)

    def fire_listeners(self, name):
        for l in self.__name_listeners.get(name, []):
            l()
        for l in self.__sub_listeners:
            l(name)
        # super(Module, self).fire_listeners()

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        context.log_error("module is not callable")
        return Union.EMPTY

    def all_names(self):
        return self._attrs.keys()

    def get_name(self, attr):
        assert isinstance(attr, str)
        return self._attrs.get(attr)

    def getattr(self, attr, context):
        assert isinstance(attr, str)
        self.add_name_listener(attr, context.listener())

        if attr in self._attrs:
            return self._attrs[attr]

        context.log_error("%s has no attribute %s" % (self.display(), attr))
        return Union.EMPTY

    def setattr(self, attr, v):
        assert isinstance(attr, str)
        assert isinstance(v, Union)
        old = self._attrs.get(attr)
        self._attrs[attr] = Union.make_union(self._attrs.get(attr, Union.EMPTY), v)
        if old != self._attrs[attr]:
            self.fire_listeners(attr)

    def display(self):
        return "module '%s'" % (self.name,)

    def score(self):
        return 1.0

class _FuncArgsError(Exception):
    pass

def translate_call(args, keywords, starargs, f_names, f_ndefault, f_vararg, context):
    assert isinstance(args, list)
    for a in args:
        assert isinstance(a, Union), a
    assert isinstance(keywords, dict), keywords
    for k, v in keywords.iteritems():
        assert isinstance(k, str)
        assert isinstance(v, Union)
    assert starargs is None or isinstance(starargs, Union)
    assert isinstance(f_names, list)
    for n in f_names:
        assert isinstance(n, str)
    assert isinstance(f_ndefault, int)
    assert f_ndefault <= len(f_names)
    assert f_vararg is None or isinstance(f_vararg, Union), f_vararg

    args = list(args)
    keywords = dict(keywords)

    if starargs:
        gen_args = []
        for t in starargs.types():
            if isinstance(t, InstanceType) and t.cls is TupleClass:
                for i, u in enumerate(t.unions):
                    while len(gen_args) <= i:
                        gen_args.append(Union.EMPTY)
                    gen_args[i] = Union.make_union(gen_args[i], u)
            else:
                elt_type = get_iter_type(starargs, context)
                # Add an extra arg to make sure that it goes into the vararg
                num_args = len(f_names) + 1 if f_vararg else len(f_names)
                while len(gen_args) + len(args) < num_args:
                    gen_args.append(Union.EMPTY)
                for i in xrange(len(gen_args)):
                    gen_args[i] = Union.make_union(gen_args[i], elt_type)

        args.extend(gen_args)

    ngiven = len(args)
    ndefined = len(f_names)

    if ngiven > ndefined and not f_vararg:
        raise _FuncArgsError("function takes a maximum of %d parameters, but got %d" % (ndefined, ngiven))

    for i in xrange(ndefined):
        n = f_names[i]
        if n in keywords:
            if i < ngiven:
                raise _FuncArgsError("doubly-given parameter %s" % (n,))
            assert i == ngiven, "should have inserted a None"
            args.append(keywords.pop(n))
            ngiven += 1
        elif i == ngiven:
            if i < ndefined - f_ndefault:
                raise _FuncArgsError("didn't get an argument for arg %d" % (i,))
            args.append(None)
            ngiven += 1

    vararg = None
    if f_vararg:
        vararg = Union.make_union(*args[ndefined:])
        args = args[:ndefined]
        ngiven = len(args)
    assert ndefined - f_ndefault <= ngiven <= ndefined, "%d given, %d expected (%d default)" % (ngiven, ndefined, f_ndefault)

    return args, keywords, vararg

def function_display(args, ndefault, vararg, kwarg, rtn):
    d = [t.display() for t in args]
    assert ndefault <= len(d), (ndefault, d)
    for i in xrange(ndefault):
        d[-1 - i] += '?'
    if vararg is not None:
        d.append("*[%s]" % vararg.display())
    if kwarg is not None:
        d.append("**{str:%s}" % kwarg.display())
    return "(%s) -> %s" % (','.join(d), rtn.display())

class UserFunction(InstanceType):
    def __init__(self, arg_names, arg_types, ndefault, vararg, kwarg, return_type, temp=False, is_generator=False):
        assert len(arg_names) == len(arg_types), (arg_names, arg_types)
        for a in arg_names:
            assert isinstance(a, str)
        for a in arg_types:
            assert isinstance(a, Union)
        assert isinstance(ndefault, int)
        assert vararg is None or isinstance(vararg, Union)
        assert kwarg is None or isinstance(kwarg, Union)
        assert isinstance(return_type, Union)
        unions = arg_types
        if vararg:
            unions += [vararg]
            self.vararg_idx = len(unions) - 1
        if kwarg:
            unions += [kwarg]
            self.kwarg_idx = len(unions) - 1
        unions += [return_type]
        self.rtn_idx = len(unions) - 1
        super(UserFunction, self).__init__(UserFunctionClass, unions, temp=temp)

        self.arg_names = arg_names
        self.ndefault = ndefault
        self.vararg = bool(vararg)
        self.kwarg = bool(kwarg)
        self.is_generator = is_generator

        if self.is_generator:
            assert self.unions[self.rtn_idx].types()[0].cls is GeneratorClass

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        # probably not strictly necessary, but probably never wrong
        self.add_listener(context.listener())

        try:
            args, keywords, vararg = translate_call(args, keywords, starargs, self.arg_names, self.ndefault, self.unions[self.vararg_idx] if self.vararg else None, context)
        except _FuncArgsError, e:
            context.log_error(e.message)
            return self.unions[self.rtn_idx]

        if keywords:
            if not self.kwarg:
                context.log_error("Got unexpected keyword arguments: %s" % (keywords.keys(),))
                # TODO break out entirely?
                return self.unions[self.rtn_idx]

            for k, v in keywords.items():
                assert isinstance(k, str)
                assert isinstance(v, Union)
                self.update(self.kwarg_idx, v)

        for i in xrange(len(args)):
            a = args[i]
            if a is None:
                continue
            if not dryrun:
                self.update(i, a)

        if vararg is not None and not dryrun:
            self.update(self.vararg_idx, vararg)

        # This function call could do arbitrary things to the local state, so clear it
        context.clear_locals()

        return self.unions[self.rtn_idx]

    def update(self, argn, u, allow_vars=False):
        if argn == self.rtn_idx and self.is_generator:
            assert u.types() == (NONE,) or u.types()[0].cls == GeneratorClass, u.display()
        return super(UserFunction, self).update(argn, u, allow_vars=allow_vars)

    def update_yield(self, u):
        assert not has_reference(u, self)
        if not self.is_generator:
            types = self.unions[self.rtn_idx].types()
            assert types == () or types == (NONE,), self.unions[self.rtn_idx].types()
            self.unions[self.rtn_idx] = Union(InstanceType(GeneratorClass, [Union.EMPTY]))
            self.unions[self.rtn_idx].add_listener(self.fire_listeners)
            self.is_generator = True
            self.fire_listeners()

        it = self.unions[self.rtn_idx]
        assert len(it.types()) == 1
        [t] = it.types()
        assert isinstance(t, InstanceType)
        assert t.cls is GeneratorClass

        t.update(0, u)

    def display(self, bound=False):
        args = self.unions[:-1]
        rtn = self.unions[self.rtn_idx]
        if bound:
            # It's possible to have no positional arguments on an instancemethod, since the 'self' parameter can go into the vararg
            if not self.arg_names:
                # but if there's no vararg, it's never going to work
                if not self.vararg:
                    return "<invalid instancemethod>"
                assert self.vararg
            else:
                assert len(args) > 0
                args = args[1:]

        k = None
        if self.kwarg:
            k = args.pop()
        v = None
        if self.vararg:
            v = args.pop()

        if self.ndefault > len(args):
            assert bound
            assert self.ndefault == len(args) + 1
            ndefault = self.ndefault - 1
        else:
            ndefault = self.ndefault

        r = function_display(args, ndefault, v, k, rtn)
        if self.is_generator:
            r = "GENERATOR " + r
        return r

    def is_dead(self):
        return any(not u.types() for u in self.unions)

class InvalidClassHierarchyException(Exception):
    pass

def merge(mros):
    r = []
    mros = [list(m) for m in mros if m]

    while mros:
        found = None
        for m in mros:
            b = m[0]
            bad = False
            for m2 in mros:
                if b in m2[1:]:
                    bad = True
                    break
            if bad:
                continue

            r.append(b)
            m.pop(0)
            found = b
            break

        if not found:
            raise InvalidClassHierarchyException()
        for m in mros:
            if found in m:
                m.remove(found)
        mros = [m for m in mros if m]

    return r

# Implements the algorithm from here:
# http://www.python.org/download/releases/2.3/mro/
def _get_mro(c):
    parent_mros = [_get_mro(b) for b in c._bases] + [c._bases]
    return [c] + merge(parent_mros)

class ClassType(Type):
    def __init__(self, name, bases, display_func, closed):
        assert bases or (name == "object" and type(self) == ClassType)
        for b in bases:
            assert isinstance(b, ClassType), b
        assert isinstance(closed, bool)
        super(ClassType, self).__init__()
        self.name = name
        self._bases = bases
        self._display_func = display_func
        self._attributes = {}
        self.closed = closed

        self._default_ctor = None

        self.__name_listeners = {}
        self.__sub_listeners = set()

        self._mro = _get_mro(self)
        self.__bind_cache = {}

        for b in bases:
            b.add_name_listener(None, self.fire_listeners)

    def add_name_listener(self, name, l):
        assert isinstance(name, str) or name is None
        assert callable(l)
        if name:
            self.__name_listeners.setdefault(name, set()).add(l)
        else:
            self.__sub_listeners.add(l)

    def fire_listeners(self, name):
        for l in self.__name_listeners.get(name, []):
            l()
        for l in self.__sub_listeners:
            l(name)
        # super(ClassType, self).fire_listeners()

    def add_listener(self, l):
        # As a performance optimization, don't add listeners on a class if it doesn't change, like list.  Kind of silly.
        if not self.closed:
            super(ClassType, self).add_listener(l)
            # s = ''.join(traceback.format_stack(limit=5))
            # if " get_expr_type" not in s and "pre_import" not in s:
                # print s

    def setattr(self, attr, value):
        assert isinstance(attr, str)
        assert isinstance(value, Union)

        # TODO disallow setting attrs on closed classes (except in the beginning)

        old = self._attributes.get(attr)
        self._attributes[attr] = Union.make_union(self._attributes.get(attr, Union.EMPTY), value)

        if old != self._attributes[attr]:
            self.fire_listeners(attr)

    @staticmethod
    def _get_name(attr, listener, mro):
        assert callable(listener)
        for c in mro:
            c.add_name_listener(attr, listener)

            if attr in c._attributes:
                return c._attributes[attr]

        if attr == "__str__":
            return ClassType._get_name("__repr__", listener, mro)
        return None

    def get_name(self, attr, listener):
        if isinstance(attr, tuple):
            for a in attr:
                v = self.get_name(a, listener)
                if v:
                    return v
            return None
        assert isinstance(attr, str)
        return ClassType._get_name(attr, listener, self._mro)

    def getattr(self, attr, context):
        assert isinstance(attr, str)
        v = self.get_name(attr, context.listener())
        if v is None:
            context.log_error("%s doesnt have attr '%s'" % (self.name, attr))
            return Union.EMPTY
        assert isinstance(v, Union)
        r = bindall(self, v, self.__bind_cache, context)
        return r

    def display(self):
        return "class '%s'" % (self.name,)

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        inst = context.get_cached(self.call)
        if not inst:
            inst = InstanceType(self, None)
            context.set_cached(self.call, inst)

        init = self.get_name("__init__", context.listener())
        if not init:
            context.log_error("%s doesn't have an __init__ method??" % self.name)
            return Union.EMPTY
        r = init.call([Union(inst)] + args, keywords, starargs, context, dryrun, orig_args)

        if inst.unions is None:
            return Union.EMPTY

        if r not in (Union.EMPTY, Union(NONE)):
            context.log_error("__init__ didn't return None, returned %s" % r.display())
        assert inst.unions is not None
        return Union(inst)

    def is_subclass_of(self, rhs):
        return rhs in self._mro

    def score(self):
        return 1.0

class UserClassType(ClassType):
    def __init__(self, name, bases):
        assert bases
        super(UserClassType, self).__init__(name, bases, lambda _:name, False)
        self._instance = InstanceType(self, [])
        self._instance.setattr("__dict__", Union(InstanceType(DictClass, [Union(STR), Union(TOP)])))

        for b in bases:
            b.add_name_listener(None, self.fire_listeners)

    def instance(self):
        return self._instance

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        init = self.get_name("__init__", context.listener())
        if init:
            # TODO this might not always hold if you manually set __init__ to something else.  hmm.
            # for t in init.types():
                # assert isinstance(t, (UserFunction, FixedFunction, PolymorphicFunction)), (t, repr(t), t.display())
            r = init.call([Union(self._instance)] + args, keywords, starargs, context, dryrun, orig_args)
            if r not in (Union.EMPTY, Union(NONE)):
                context.log_error("__init__ didn't return None, returned %s" % r.display())

        return Union(self._instance)

def has_params(t, d=None):
    if d is None:
        d = {}
    if isinstance(t, Union):
        return _has_params(t, d)

    if t in d:
        return d[t]

    d[t] = False
    r = _has_params(t, d)
    d[t] = r
    return r

def _has_params(t, d):
    if isinstance(t, Param):
        return True

    if isinstance(t, Union):
        return any(has_params(t2, d) for t2 in t.types())

    if isinstance(t, InstanceType):
        return any(has_params(t2, d) for t2 in t.unions)

    if isinstance(t, ConstType):
        return False

    if isinstance(t, ClassType):
        has = False
        for b in t._bases:
            has = has or has_params(b, d)
        return has

    if isinstance(t, Module):
        return False

    if isinstance(t, InstanceMethod):
        return has_params(t._f, d) or has_params(t._bind, d)

    if isinstance(t, (FixedFunction, PolymorphicFunction, SpecialFunction, ClassMethod)):
        return False

    raise Exception(t)

def has_reference(u, t):
    assert isinstance(t, Type)

    if isinstance(u, Union):
        return any(has_reference(t2, t) for t2 in u.types())

    if u is t:
        return True

    # Note: objects can have references to themselves in their attrs.  not sure how to classify that distinction
    if isinstance(u, InstanceType):
        return any(has_reference(u2, t) for u2 in u.unions)

    if isinstance(u, InstanceMethod):
        return has_reference(u._f, t) or has_reference(u._bind, t)

    if isinstance(u, (UserFunction, ConstType, ClassType, PolymorphicFunction, FixedFunction, Param, Module, ClassMethod, SpecialFunction)):
        return False

    raise Exception(u)

def complexity(u):
    if isinstance(u, Union):
        if len(u.types()) == 0:
            return 1.0
        return sum(complexity(t) for t in u.types())

    if isinstance(u, InstanceType):
        return 1.0 + sum(complexity(u2) for u2 in u.unions)

    return 1.0

# TODO This is a surprising amount of hard-coding, but I guess it makes sense
class SuperClassType(ClassType):
    def __init__(self):
        super(SuperClassType, self).__init__("super", (ObjectClass,), None, True)
        SuperClassType.__init__ = None

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        try:
            args, keywords, vararg = translate_call(args, keywords, starargs, ["_cls", "_inst"], 0, None, context)
        except _FuncArgsError, e:
            context.log_error(e.message)
            return Union.EMPTY

        cls = args[0]
        inst = args[1]
        if not cls.types() or not inst.types():
            return Union.EMPTY
        if len(cls.types()) > 1 or len(inst.types()) > 1:
            context.log_error("don't handle unions here yet")
            return Union.EMPTY

        [cls] = cls.types()
        [inst] = inst.types()

        if not isinstance(cls, ClassType):
            context.log_error("expected a type as the first argument")
            return Union.EMPTY

        if not isinstance(inst, InstanceType):
            context.log_error("expected an instance as the second argument")
            return Union.EMPTY

        if not inst.cls.is_subclass_of(cls):
            context.log_error("%s is not a supertype of %s" % (cls.name, inst.cls.name))
            return Union.EMPTY

        key = (cls, inst)
        rtn = context.get_cached(key)
        if rtn is None:
            rtn = Union(SuperInstanceType(cls, inst))
            context.set_cached(key, rtn)
        return rtn

class SuperInstanceType(InstanceType):
    def __init__(self, cls, inst, temp=False):
        assert isinstance(cls, ClassType)
        assert isinstance(inst, InstanceType)
        super(SuperInstanceType, self).__init__(SuperClass, [Union(cls), Union(inst)], temp=temp)
        self.__cls = cls
        self.__inst = inst
        # TODO share this between instances?
        self.__bind_cache = {}

    def display(self):
        return "<super: %s, %s>" % (self.__cls.display(), self.__inst.display())

    def setattr(self, attr, v):
        print "cant setattr on a super (or display an error for it)"

    def getattr(self, attr, context):
        assert isinstance(attr, str)
        u = self.__inst.get_name(attr, context)
        if u:
            return u

        # TODO lots of duplication with instancetype.getattr
        u = ClassType._get_name(attr, context.listener(), self.__cls._mro[1:])
        if u is None:
            u = Union.EMPTY
            context.log_error("%s has no attribute %s" % (self.display(), attr))

        return bindall(self.__inst, u, self.__bind_cache, context)

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        context.log_error("super object is not callable")
        return Union.EMPTY

class Arg(object):
    pass

class InstanceArg(Arg):
    def __init__(self, cls, args, update=False):
        assert isinstance(cls, ClassType)
        for a in args:
            assert isinstance(a, (ConstType, Arg)), a

        self.cls = cls
        self.args = args
        self.update = update

    def display(self):
        return self.cls._display_func(self.args)

class Var(Arg):
    def __init__(self, id):
        super(Var, self).__init__()
        self.id = id

    def display(self):
        return "T%d" % (self.id,)

class Subtype(Arg):
    def __init__(self, a):
        assert isinstance(a, (Arg, ConstType))
        super(Subtype, self).__init__()
        self.a = a

    def display(self):
        return "<=%s" % (self.a.display(),)

class FixedArg(Arg):
    def __init__(self, u):
        assert isinstance(u, Union)
        super(FixedArg, self).__init__()
        self.u = u

    def display(self):
        return self.u.display()

class Param(Type):
    def __init__(self, id):
        super(Param, self).__init__()
        self.id = id

    def add_listener(self, l):
        pass

    def display(self):
        return "T%d" % (self.id,)

    def score(self):
        raise Exception()

class CustomInstance(InstanceType):
    def is_custom(self):
        return True

    def score(self):
        return 1.0

class CustomClass(ClassType):
    def __init__(self, name):
        super(CustomClass, self).__init__(name, (ObjectClass,), lambda _:name, True)

    def is_custom(self):
        return True

    def score(self):
        return 1.0

ANY = Subtype(Var(9))
BOT = FixedArg(Union.EMPTY)

def _user_func_display(types):
    displays = [t.display() for t in types]
    return "(%s) => %s" % (", ".join(displays[:-1]), displays[-1])

ObjectClass = ClassType("object", (), lambda _: "object", True)
TypeClass = ClassType("type", (ObjectClass,), lambda _: "type", True)
Iterator = ClassType("iterator", (ObjectClass,), lambda (t,):"iterator of %s" % t.display(), True)
GeneratorClass = ClassType("generator", (ObjectClass,), lambda (t,):"generator of %s" % t.display(), True)
Iterable = ClassType("iterable", (ObjectClass,), lambda(t,):"iterable %s" % t.display(), True)
SuperClass = SuperClassType()
UserFunctionClass = ClassType("function", (ObjectClass,), _user_func_display, True)
ListClass = ClassType("list", (ObjectClass,), lambda (t,):"[%s]" % t.display(), True)
DictClass = ClassType("dict", (ObjectClass,), lambda (k,v):"{%s:%s}" % (k.display(), v.display()), True)

def tuple_display(args):
    if len(args) == 0:
        return '()'
    if len(args) == 1:
        return '(%s,)' % (args[0].display(),)
    return '(%s)' % (','.join(a.display() for a in args))
TupleClass = ClassType("tuple", (ObjectClass,), tuple_display, True)
StaticMethodClass = ClassType("staticmethod", (ObjectClass,), lambda _:"<staticmethod object>", True)
ClassMethodClass = ClassType("classmethod", (ObjectClass,), lambda _:"<classmethod object>", True)
PropertyClass = ClassType("property", (ObjectClass,), lambda _:"<property object>", True)
