import collections
from type_system import (
        Union,

        Type,
        TopType, TOP,
        FloatType, FLOAT,
        IntType, INT,
        StrType, STR,
        NoneType, NONE,
        BoolType, BOOL,
        SliceType, SLICE,

        Param,
        InstanceType,
        ClassType,
        Module,

        PolymorphicFunction,
        FixedFunction,
        ObjectClass,
        TypeClass,
        Iterable,
        Iterator,
        ListClass,
        DictClass,
        TupleClass,
        SuperClass,
        SpecialFunction,
        StaticMethodClass,
        ClassMethodClass,
        PropertyClass,
        GeneratorClass,
        InstanceMethod,
        UserFunctionClass,
        UserFunction,

        UserClassType,

        translate_call,
        _FuncArgsError,
        get_iter_type,
        FakeContext,

        Subtype,
        InstanceArg,
        Var,
        FixedArg,
        ANY,
        BOT,
        )

ObjectClass.setattr("__init__", Union(FixedFunction([InstanceArg(ObjectClass, [], update=True)], NONE)))
ObjectClass.setattr("__nonzero__", Union(FixedFunction([ANY], BOOL)))
ObjectClass.setattr("__eq__", Union(FixedFunction([Subtype(Var(8)), ANY], BOOL)))
ObjectClass.setattr("__ne__", Union(FixedFunction([Subtype(Var(8)), ANY], BOOL)))

TypeClass.setattr("__init__", Union(FixedFunction([InstanceArg(TypeClass, [], update=True), ANY], NONE)))
TypeClass.setattr("__name__", Union(STR))

Iterator.setattr("next", Union(FixedFunction([InstanceArg(Iterator, [Var(0)])], Var(0))))
Iterator.setattr("__iter__", Union(FixedFunction([Var(0)], Var(0))))

GeneratorClass.setattr("next", Union(FixedFunction([InstanceArg(GeneratorClass, [Var(0)])], Var(0))))
GeneratorClass.setattr("__iter__", Union(FixedFunction([Var(0)], Var(0))))

ListClass.setattr("__init__", Union(FixedFunction([InstanceArg(ListClass, [Var(0)], update=True), Subtype(InstanceArg(Iterable, [Var(0)]))], NONE, defaults=[InstanceArg(ListClass, [BOT])])))
ListClass.setattr("append", Union(FixedFunction([InstanceArg(ListClass, [Var(0)], update=True), Subtype(Var(0))], NONE)))
ListClass.setattr("insert", Union(FixedFunction([InstanceArg(ListClass, [Var(0)], update=True), INT, Subtype(Var(0))], NONE)))
ListClass.setattr("__contains__", Union(FixedFunction([InstanceArg(ListClass, [Var(0)]), Subtype(Var(0))], BOOL)))
ListClass.setattr("__iter__", Union(FixedFunction([InstanceArg(ListClass, [Var(0)])], InstanceArg(Iterator, [Var(0)]))))
ListClass.setattr("extend", Union(FixedFunction([InstanceArg(ListClass, [Var(0)], update=True), Subtype(InstanceArg(Iterable, [Var(0)]))], NONE)))
ListClass.setattr("remove", Union(FixedFunction([InstanceArg(ListClass, [Var(0)]), Subtype(Var(0))], NONE)))
ListClass.setattr("__getitem__", Union(PolymorphicFunction(
    FixedFunction([InstanceArg(ListClass, [Var(0)]), INT], Var(0)),
    FixedFunction([InstanceArg(ListClass, [Var(0)]), SLICE], InstanceArg(ListClass, [Var(0)])),
)))
ListClass.setattr("pop", Union(FixedFunction([InstanceArg(ListClass, [Var(0)]), INT], Var(0), ndefaults=1)))
ListClass.setattr("__setitem__", Union(PolymorphicFunction(
    FixedFunction([InstanceArg(ListClass, [Var(0)], update=True), INT, Subtype(Var(0))], NONE),
    FixedFunction([InstanceArg(ListClass, [Var(0)], update=True), SLICE, InstanceArg(ListClass, [Subtype(Var(0))])], NONE)
)))
ListClass.setattr("__add__", Union(FixedFunction([InstanceArg(ListClass, [Subtype(Var(0))]), InstanceArg(ListClass, [Subtype(Var(0))])], InstanceArg(ListClass, [Var(0)]))))
ListClass.setattr("count", Union(FixedFunction([InstanceArg(ListClass, [Var(0)]), Subtype(Var(0))], INT)))
ListClass.setattr("__delitem__", Union(PolymorphicFunction(
    FixedFunction([InstanceArg(ListClass, [Var(0)]), INT], NONE),
    FixedFunction([InstanceArg(ListClass, [Var(0)]), SLICE], NONE)
)))
# TODO actual args are l.sort(cmp=None, key=None, reverse=False)
def sort_effects(args, context):
    assert len(args) == 1, args
    a, = args
    assert len(a.types()) == 1, a.display()
    t, = a.types()
    assert t.cls is ListClass
    assert len(t.unions) == 1, t.unions
    elt_u, = t.unions
    lt = elt_u.getattr("__lt__", context)
    lt.call([elt_u], {}, None, context, False, None)
ListClass.setattr("sort", Union(FixedFunction([InstanceArg(ListClass, [Var(0)])], NONE, implicit_behavior_funcs=[sort_effects])))
ListClass.setattr("reverse", Union(FixedFunction([InstanceArg(ListClass, [Var(0)])], NONE)))
ListClass.setattr("index", Union(FixedFunction([InstanceArg(ListClass, [Var(0)]), Subtype(Var(0)), INT, INT], INT, ndefaults=2)))
ListClass.setattr("__mul__", Union(FixedFunction([InstanceArg(ListClass, [Var(0)]), INT], InstanceArg(ListClass, [Var(0)]))))



def _dict_kw(args, keywords, starargs, context, dryrun, orig_args):
    try:
        args, keywords, vararg = translate_call(args, keywords, starargs, ["self"], 0, None, context)
    except _FuncArgsError, e:
        context.log_error(e.message)
        return Union.EMPTY
    u = Union.make_union(*keywords.values())

    for t in args[0].types():
        if not isinstance(t, InstanceType) or t.cls != DictClass:
            print "WTF"
            continue
        if t.unions is None:
            t.unions = [Union.EMPTY, Union.EMPTY]

        t.update(0, Union(STR))
        t.update(1, u)
    return Union(NONE)


DictClass.setattr("__init__", Union(PolymorphicFunction(
    FixedFunction([InstanceArg(DictClass, [BOT, BOT], update=True)], NONE),
    FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)], update=True), Subtype(InstanceArg(DictClass, [Var(0), Var(1)]))], NONE),
    FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)], update=True), Subtype(InstanceArg(Iterable, [InstanceArg(TupleClass, [Var(0), Var(1)])]))], NONE),
    # TODO this needs to be a special function because fixedfunctions don't support kwargs
    SpecialFunction(_dict_kw),
)))
DictClass.setattr("__setitem__", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)], update=True), Subtype(Var(0)), Subtype(Var(1))], NONE)))
DictClass.setattr("update", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)], update=True), Subtype(InstanceArg(DictClass, [Var(0), Var(1)]))], NONE)))
DictClass.setattr("__getitem__", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)]), Subtype(Var(0))], Subtype(Var(1)))))
DictClass.setattr("__iter__", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)])], InstanceArg(Iterator, [Var(0)]))))
DictClass.setattr("keys", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)])], InstanceArg(ListClass, [Var(0)]))))
DictClass.setattr("iterkeys", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)])], InstanceArg(Iterator, [Var(0)]))))
DictClass.setattr("values", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)])], InstanceArg(ListClass, [Var(1)]))))
DictClass.setattr("itervalues", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)])], InstanceArg(Iterator, [Var(1)]))))
DictClass.setattr("items", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)])], InstanceArg(ListClass, [InstanceArg(TupleClass, [Var(0), Var(1)])]))))
DictClass.setattr("iteritems", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)])], InstanceArg(Iterator, [InstanceArg(TupleClass, [Var(0), Var(1)])]))))
DictClass.setattr("get", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Subtype(Var(1))]), Subtype(Var(0)), Subtype(Var(1))], Var(1), defaults=[NONE])))
DictClass.setattr("pop", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Subtype(Var(1))]), Subtype(Var(0)), Subtype(Var(1))], Var(1), defaults=[NONE])))
DictClass.setattr("__contains__", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)]), Subtype(Var(0))], BOOL)))
DictClass.setattr("has_key", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)]), Subtype(Var(0))], BOOL)))
DictClass.setattr("clear", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)])], NONE)))
DictClass.setattr("copy", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)])], InstanceArg(DictClass, [Var(0), Var(1)]))))
DictClass.setattr("__delitem__", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)]), Subtype(Var(0))], NONE)))
DictClass.setattr("popitem", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)])], InstanceArg(TupleClass, [Var(0), Var(1)]))))
DictClass.setattr("setdefault", Union(FixedFunction([InstanceArg(DictClass, [Var(0), Var(1)], update=True), Subtype(Var(0)), Subtype(Var(1))], Var(1), defaults=[NONE])))
# fromkeys (staticmethod)

TupleClass.setattr("__init__", Union(PolymorphicFunction(
    FixedFunction([InstanceArg(TupleClass, [], update=True)], NONE),
    FixedFunction([InstanceArg(TupleClass, [], update=True), InstanceArg(TupleClass, [])], NONE),
    FixedFunction([InstanceArg(TupleClass, [Var(0)], update=True), InstanceArg(TupleClass, [Var(0)])], NONE),
    FixedFunction([InstanceArg(TupleClass, [Var(0), Var(1)], update=True), InstanceArg(TupleClass, [Var(0), Var(1)])], NONE),
    FixedFunction([InstanceArg(TupleClass, [Var(0), Var(1), Var(2)], update=True), InstanceArg(TupleClass, [Var(0), Var(1), Var(2)])], NONE),
)))
def tuple_add(args, keywords, starargs, context, dryrun, orig_args):
    try:
        args, keywords, vararg = translate_call(args, keywords, starargs, [" lhs", " rhs"], 0, None, context)
    except _FuncArgsError, e:
        context.log_error(e.message)
        return Union.EMPTY
    if keywords or vararg:
        context.log_error("wtf")
        return Union.EMPTY
    if len(args) != 2 or len(args[0].types()) != 1 or len(args[1].types()) != 1:
        context.log_error("wtf")
        return Union.EMPTY
    t1 = args[0].types()[0]
    t2 = args[1].types()[0]
    if not isinstance(t1, InstanceType) or not t1.cls is TupleClass:
        context.log_error("wtf")
        return Union.EMPTY
    if not isinstance(t2, InstanceType) or not t1.cls is TupleClass:
        context.log_error("wtf")
        return Union.EMPTY

    t = context.get_cached("__add__")
    n1 = len(t1.unions)
    n2 = len(t2.unions)
    if t is None:
        t = InstanceType(TupleClass, [Union.EMPTY for i in xrange(n1 + n2)])
        context.set_cached("__add__", t)
    if len(t.unions) != n1 + n2:
        print >>sys.stderr, "WTF"
        return Union.EMPTY
    for i in xrange(n1):
        t.update(i, t1.unions[i])
    for i in xrange(n2):
        t.update(n1 + i, t2.unions[i])
    return Union(t)
TupleClass.setattr("__add__", Union(SpecialFunction(tuple_add)))
TupleClass.setattr("__lt__", Union(TOP)) # TODO not the right definition



BUILTINS = {}

BUILTINS['__name__'] = BUILTINS['__file__'] = Union(STR)

BUILTINS['object'] = Union(ObjectClass)
BUILTINS['type'] = Union(TypeClass)
BUILTINS['list'] = Union(ListClass)
BUILTINS['dict'] = Union(DictClass)
BUILTINS['tuple'] = Union(TupleClass)
BUILTINS['super'] = Union(SuperClass)

BUILTINS['None'] = Union(NONE)
BUILTINS['True'] = Union(BOOL)
BUILTINS['False'] = Union(BOOL)

# TODO this should be a class?  type(bool) = type
BUILTINS['bool'] = Union(FixedFunction([ANY], BOOL))

BUILTINS['chr'] = Union(FixedFunction([INT], STR))
BUILTINS['ord'] = Union(FixedFunction([STR], INT))
BUILTINS['xrange'] = BUILTINS['range'] = Union(FixedFunction([INT, INT, INT], InstanceArg(ListClass, [INT]), ndefaults=2))

BUILTINS['sorted'] = Union(FixedFunction([Subtype(InstanceArg(Iterable, [Var(0)])), ANY], InstanceArg(ListClass, [Var(0)]), defaults=[BOT], arg_names=["iterable", "key"]))
BUILTINS['reversed'] = Union(FixedFunction([Subtype(InstanceArg(Iterable, [Var(0)]))], InstanceArg(Iterator, [Var(0)])))

BUILTINS['cmp'] = Union(FixedFunction([Subtype(Var(0)), Subtype(Var(1))], INT))

BUILTINS['len'] = Union(FixedFunction([Subtype(InstanceArg(Iterable, [Var(0)]))], INT))
BUILTINS['str'] = Union(FixedFunction([ANY], STR, ndefaults=1))
BUILTINS['repr'] = Union(FixedFunction([ANY], STR))
BUILTINS['hash'] = Union(FixedFunction([ANY], INT))

BUILTINS['abs'] = Union(PolymorphicFunction(
    FixedFunction([INT], INT),
    FixedFunction([FLOAT], FLOAT),
))
BUILTINS['complex'] = Union(FixedFunction([FLOAT], FLOAT))
BUILTINS['long'] = BUILTINS['int'] = Union(PolymorphicFunction(
    FixedFunction([STR, INT], INT, ndefaults=1),
    FixedFunction([FLOAT], INT),
))
BUILTINS['float'] = Union(PolymorphicFunction(
    FixedFunction([FLOAT], FLOAT),
    FixedFunction([STR], FLOAT),
))
BUILTINS['oct'] = BUILTINS['hex'] = Union(FixedFunction([INT], STR))

BUILTINS['callable'] = Union(FixedFunction([ANY], BOOL))
BUILTINS['hasattr'] = Union(FixedFunction([ANY, STR], BOOL))
BUILTINS['getattr'] = Union(FixedFunction([ANY, STR, TOP], TOP, ndefaults=1))
BUILTINS['setattr'] = Union(FixedFunction([ANY, STR, Subtype(Var(8))], TOP))

BUILTINS['round'] = Union(FixedFunction([FLOAT, INT], FLOAT, ndefaults=1))
BUILTINS['abs'] = Union(PolymorphicFunction(
    FixedFunction([INT], INT),
    FixedFunction([FLOAT], FLOAT),
))

BUILTINS['sum'] = Union(PolymorphicFunction(
    FixedFunction([Subtype(InstanceArg(Iterable, [INT]))], INT),
    FixedFunction([Subtype(InstanceArg(Iterable, [FLOAT]))], FLOAT),
))

BUILTINS['max'] = BUILTINS['min'] = Union(PolymorphicFunction(
    FixedFunction([Subtype(InstanceArg(Iterable, [INT]))], INT),
    FixedFunction([INT, INT], INT),
    FixedFunction([Subtype(InstanceArg(Iterable, [FLOAT]))], FLOAT),
    FixedFunction([FLOAT, FLOAT], FLOAT),
    FixedFunction([Subtype(InstanceArg(Iterable, [Var(0)]))], Var(0)),
))

BUILTINS['divmod'] = Union(FixedFunction([INT, INT], InstanceArg(TupleClass, [INT, INT])))

def _map_rtn(args, keywords, starargs, context, dryrun, orig_args):
    assert not keywords
    assert not starargs
    f = args[0]
    elts = []
    for a in args[1:]:
        elts.append(get_iter_type(a, context))

    r = context.get_cached(_map_rtn)
    if not r:
        r = InstanceType(ListClass, [Union.EMPTY])
        context.set_cached(_map_rtn, r)

    u = f.call(elts, {}, None, context, dryrun, orig_args)
    r.update(0, u)
    return Union(r)

BUILTINS['map'] = Union(SpecialFunction(_map_rtn))

def _filter_rtn(args, keywords, starargs, context, dryrun, orig_args):
    assert not keywords
    assert not starargs
    assert len(args) == 2
    f = args[0]

    r = context.get_cached(_filter_rtn)
    if not r:
        r = InstanceType(ListClass, [Union.EMPTY])
        context.set_cached(_filter_rtn, r)

    rtn = []
    for t in args[1].types():
        elt_type = get_iter_type(Union(t), context)
        if f != Union(NONE):
            f.call([elt_type], {}, None, context, dryrun, orig_args)

        if t is STR:
            rtn.append(Union(STR))
        else:
            r.update(0, elt_type)
            rtn.append(Union(r))

    return Union.make_union(*rtn)

BUILTINS['filter'] = Union(SpecialFunction(_filter_rtn))

def _reduce_rtn(args, keywords, starargs, context, dryrun, orig_args):
    assert not keywords
    assert not starargs
    assert len(args) == 3, args

    f, l, initial = args

    elt_type = get_iter_type(l, context)

    cur = initial
    MAX_TRIES = 10
    for i in xrange(MAX_TRIES):
        next = f.call([cur, elt_type], {}, None, context, dryrun, orig_args)
        if next == cur:
            return next
        cur = next
    else:
        return Union(TOP)
BUILTINS['reduce'] = Union(SpecialFunction(_reduce_rtn))

def _cast_rtn(args, keywords, starargs, context, dryrun, orig_args):
    assert len(args) == 2
    assert not keywords
    assert not starargs

    r = get_instance_type(args[1])
    assert isinstance(r, Union), (r, args[1].types())
    return r

BUILTINS['__cast__'] = Union(SpecialFunction(_cast_rtn))

BUILTINS['any'] = BUILTINS['all'] = Union(FixedFunction([Subtype(InstanceArg(Iterable, [Var(0)]))], BOOL))

BUILTINS['enumerate'] = BUILTINS['ienumerate'] = Union(FixedFunction([Subtype(InstanceArg(Iterable, [Var(0)]))], InstanceArg(ListClass, [InstanceArg(TupleClass, [INT, Var(0)])])))

# TODO This isn't correct
BUILTINS['isinstance'] = Union(FixedFunction([Subtype(Var(8)), ANY], BOOL))

BUILTINS['execfile'] = Union(FixedFunction([STR, InstanceArg(DictClass, [STR, TOP]), InstanceArg(DictClass, [STR, TOP])], NONE))

BUILTINS['raw_input'] = Union(FixedFunction([STR], STR, ndefaults=1))

def make_class(name, base):
    return ClassType(name, (base,), lambda _:name, True)

ExceptionClass = make_class("Exception", ObjectClass)
ExceptionClass.setattr("__init__", Union(FixedFunction([InstanceArg(ExceptionClass, [], update=True), ANY], NONE, ndefaults=1)))
BUILTINS["Exception"] = Union(ExceptionClass)
BUILTINS["NotImplementedError"] = Union(make_class("NotImplementedError", ExceptionClass))

SetClass = ClassType("set", (ObjectClass,), lambda (t,):"set(%s)" % (t.display(),), True)
SetClass.setattr("__init__", Union(FixedFunction([InstanceArg(SetClass, [Var(0)], update=True), Subtype(InstanceArg(Iterable, [Var(0)]))], NONE, defaults=[InstanceArg(Iterator, [FixedArg(Union())])])))
SetClass.setattr("add", Union(FixedFunction([InstanceArg(SetClass, [Var(0)], update=True), Subtype(Var(0))], NONE)))
SetClass.setattr("__iter__", Union(FixedFunction([InstanceArg(SetClass, [Var(0)])], InstanceArg(Iterator, [Var(0)]))))
BUILTINS["set"] = Union(SetClass)
SetClass.setattr("__contains__", Union(FixedFunction([InstanceArg(SetClass, [Var(0)]), Subtype(Var(0))], BOOL)))
SetClass.setattr("clear", Union(FixedFunction([InstanceArg(SetClass, [Var(0)])], NONE)))
SetClass.setattr("difference", Union(FixedFunction([InstanceArg(SetClass, [Var(0)]), Subtype(InstanceArg(Iterable, [Var(1)]))], InstanceArg(SetClass, [Var(0)]))))
SetClass.setattr("difference_update", Union(FixedFunction([InstanceArg(SetClass, [Var(0)]), Subtype(InstanceArg(Iterable, [Var(1)]))], NONE)))
# These are interesting; theoretically, the result should be a common subtype of the two types
SetClass.setattr("intersection", Union(FixedFunction([InstanceArg(SetClass, [Var(0)]), Subtype(InstanceArg(Iterable, [Var(1)]))], InstanceArg(SetClass, [Var(0)]))))
SetClass.setattr("intersection_update", Union(FixedFunction([InstanceArg(SetClass, [Var(0)]), Subtype(InstanceArg(Iterable, [Var(1)]))], NONE)))
SetClass.setattr("pop", Union(FixedFunction([InstanceArg(SetClass, [Var(0)])], Var(0))))
SetClass.setattr("remove", Union(FixedFunction([InstanceArg(SetClass, [Var(0)]), Subtype(Var(0))], NONE)))
SetClass.setattr("discard", Union(FixedFunction([InstanceArg(SetClass, [Var(0)]), Subtype(Var(0))], NONE)))
SetClass.setattr("symmetric_difference", Union(FixedFunction([InstanceArg(SetClass, [Subtype(Var(0))]), Subtype(InstanceArg(Iterable, [Var(0)]))], InstanceArg(SetClass, [Var(0)]))))
SetClass.setattr("symmetric_difference_update", Union(FixedFunction([InstanceArg(SetClass, [Var(0)], update=True), Subtype(InstanceArg(Iterable, [Var(0)]))], NONE)))
SetClass.setattr("union", Union(FixedFunction([InstanceArg(SetClass, [Subtype(Var(0))]), Subtype(InstanceArg(Iterable, [Var(0)]))], InstanceArg(SetClass, [Var(0)]))))
SetClass.setattr("update", Union(FixedFunction([InstanceArg(SetClass, [Var(0)], update=True), Subtype(InstanceArg(Iterable, [Var(0)]))], NONE)))
# TODO: issubset, issuperset
SetClass.setattr("issubset", Union(FixedFunction([InstanceArg(SetClass, [Subtype(Var(0))]), Subtype(InstanceArg(Iterable, [Var(0)]))], BOOL)))
SetClass.setattr("issuperset", Union(FixedFunction([InstanceArg(SetClass, [Var(0)]), Subtype(InstanceArg(Iterable, [Var(0)]))], BOOL)))

frozenset = ClassType("frozenset", (SetClass,), lambda (k,):"frozenset(%s)" % (k.display(),), True)
BUILTINS["frozenset"] = Union(frozenset)






KNOWN_MODULES = {}

collections_ = Module('collections', "__builtin__")
KNOWN_MODULES['collections'] = collections_

DequeClass = ClassType("deque", (ObjectClass,), lambda (t,):"deque(%s)" % t.display(), True)
collections_.setattr("deque", Union(DequeClass))

DequeClass.setattr("__init__", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)], update=True), Subtype(InstanceArg(Iterable, [Var(0)]))], NONE, defaults=[InstanceArg(Iterator, [FixedArg(Union())])])))
DequeClass.setattr("pop", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)])], Var(0))))
DequeClass.setattr("popleft", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)])], Var(0))))
DequeClass.setattr("append", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)], update=True), Subtype(Var(0))], NONE)))
DequeClass.setattr("appendleft", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)], update=True), Subtype(Var(0))], NONE)))
DequeClass.setattr("extend", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)], update=True), Subtype(InstanceArg(Iterable, [Var(0)]))], NONE)))
DequeClass.setattr("extendleft", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)], update=True), Subtype(InstanceArg(Iterable, [Var(0)]))], NONE)))
DequeClass.setattr("__contains__", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)]), Subtype(Var(0))], BOOL)))
DequeClass.setattr("__iter__", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)])], InstanceArg(Iterator, [Var(0)]))))
DequeClass.setattr("__getitem__", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)]), INT], Var(0))))
DequeClass.setattr("clear", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)])], NONE)))
DequeClass.setattr("count", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)]), Subtype(Var(0))], INT)))
DequeClass.setattr("remove", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)]), Subtype(Var(0))], NONE)))
DequeClass.setattr("rotate", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)]), INT], NONE, ndefaults=1)))
DequeClass.setattr("reverse", Union(FixedFunction([InstanceArg(DequeClass, [Var(0)])], NONE)))


Queue = Module('Queue', "__builtin__")
KNOWN_MODULES['Queue'] = Queue

QueueClass = ClassType("Queue", (ObjectClass,), lambda (t,):"Queue(%s)" % t.display(), True)
Queue.setattr("Queue", Union(QueueClass))

QueueClass.setattr("__init__", Union(FixedFunction([InstanceArg(QueueClass, [Var(0)], update=True), Subtype(InstanceArg(Iterable, [Var(0)]))], NONE, defaults=[InstanceArg(Iterator, [FixedArg(Union())])])))
QueueClass.setattr("get", Union(FixedFunction([InstanceArg(QueueClass, [Var(0)])], Var(0))))
QueueClass.setattr("put", Union(FixedFunction([InstanceArg(QueueClass, [Var(0)]), Var(0)], NONE)))
QueueClass.setattr("task_done", Union(FixedFunction([InstanceArg(QueueClass, [Var(0)])], NONE)))
QueueClass.setattr("unfinished_tasks", Union(INT))
# TODO hmm queue.all_tasks_done is a threading.condition

FileClass = make_class("file", ObjectClass)
BUILTINS["file"] = Union(FileClass)
BUILTINS["open"] = Union(FixedFunction([STR, STR], InstanceArg(FileClass, []), ndefaults=1))
FileClass.setattr("read", Union(FixedFunction([InstanceArg(FileClass, []), INT], STR, ndefaults=1)))
FileClass.setattr("readline", Union(FixedFunction([InstanceArg(FileClass, []), INT], STR, ndefaults=1)))
FileClass.setattr("next", Union(FixedFunction([InstanceArg(FileClass, [])], STR)))
FileClass.setattr("write", Union(FixedFunction([InstanceArg(FileClass, []), STR], NONE)))
FileClass.setattr("__iter__", Union(FixedFunction([InstanceArg(FileClass, [])], InstanceArg(Iterator, [STR]))))
FileClass.setattr("__enter__", Union(FixedFunction([InstanceArg(FileClass, [])], InstanceArg(FileClass, []))))
FileClass.setattr("__exit__", Union(FixedFunction([InstanceArg(FileClass, []), Subtype(Var(0)), Subtype(Var(1)), Subtype(Var(2))], BOOL)))
FileClass.setattr("close", Union(FixedFunction([InstanceArg(FileClass, [])], NONE)))
FileClass.setattr("closed", Union(BOOL))
FileClass.setattr("flush", Union(FixedFunction([InstanceArg(FileClass, [])], NONE)))
FileClass.setattr("readlines", Union(FixedFunction([InstanceArg(FileClass, []), INT], InstanceArg(ListClass, [STR]), ndefaults=1)))
FileClass.setattr("writelines", Union(FixedFunction([InstanceArg(FileClass, []), Subtype(InstanceArg(Iterable, [STR]))], NONE)))
FileClass.setattr("seek", Union(FixedFunction([InstanceArg(FileClass, []), INT, INT], NONE, ndefaults=1)))
FileClass.setattr("tell", Union(FixedFunction([InstanceArg(FileClass, [])], INT)))
FileClass.setattr("fileno", Union(FixedFunction([InstanceArg(FileClass, [])], INT)))

for k, v in BUILTINS.iteritems():
    assert isinstance(k, str), (k, v.display())
    assert isinstance(v, Union), (k, v.display())

BUILTINS["staticmethod"] = Union(StaticMethodClass)
StaticMethodClass.setattr("__init__", Union(FixedFunction([InstanceArg(StaticMethodClass, [Var(0)], update=True), Subtype(Var(0))], NONE)))

BUILTINS["classmethod"] = Union(ClassMethodClass)
ClassMethodClass.setattr("__init__", Union(FixedFunction([InstanceArg(ClassMethodClass, [Var(0)], update=True), Subtype(Var(0))], NONE)))

BUILTINS["property"] = Union(PropertyClass)
PropertyClass.setattr("__init__", Union(FixedFunction([InstanceArg(PropertyClass, [Var(0)], update=True), Subtype(Var(0))], NONE)))

builtin_module = Module('__builtin__', "__builtin__")
KNOWN_MODULES["__builtin__"] = builtin_module
for k, v in BUILTINS.iteritems():
    builtin_module.setattr(k, v)


# TODO hacky to put this in this file, but it needs to be able to access BUILTINS and also be a part of BUILTINS (for __cast__)
def get_instance_type(u):
    types = []
    q = collections.deque(u.types())
    while q:
        t = q.pop()
        if Union(t) == BUILTINS['int']:
            types.append(INT)
        elif Union(t) == BUILTINS['str']:
            types.append(STR)
        elif Union(t) == BUILTINS['float']:
            types.append(FLOAT)
        elif Union(t) == BUILTINS['bool']:
            types.append(BOOL)
        elif isinstance(t, InstanceType) and t.cls is TupleClass:
            for elt in t.unions:
                q.extend(elt.types())
        elif isinstance(t, InstanceType):
            pass
        elif isinstance(t, UserClassType):
            types.append(t.instance())
        elif isinstance(t, ClassType):
            pass
        elif isinstance(t, (FixedFunction, SpecialFunction, PolymorphicFunction, InstanceMethod, UserFunction)):
            pass
        else:
            print repr(t)
            print repr(t.display())
            raise Exception(t.display())
            # raise Exception(t.display(), ast_utils.format_node(e.args[1]))
    return Union(*set(types))
