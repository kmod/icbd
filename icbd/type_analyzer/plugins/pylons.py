import ast as _ast

from icbd.type_analyzer.type_system import (
        Union,

        Type,
        TopType, TOP,
        FloatType, FLOAT,
        IntType, INT,
        StrType, STR,
        NoneType, NONE,
        BoolType, BOOL,

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
        CustomClass,
        CustomInstance,

        UserClassType,

        translate_call,
        _FuncArgsError,
        get_iter_type,

        Subtype,
        InstanceArg,
        Var,
        FixedArg,
        ANY,
        BOT,
        )

from icbd.type_analyzer.builtins import (BUILTINS, KNOWN_MODULES, make_class)


pylons = Module("pylons", "__builtin__")
controllers = Module("controllers", "__builtin__")
pylons.setattr("controllers", Union(controllers))
WSGIController = UserClassType("WSGIController", (ObjectClass,))
controllers.setattr("WSGIController", Union(WSGIController))

StackedObjectProxy = UserClassType("StackedObjectProxy", (ObjectClass,))
class StackedObjectProxyType(CustomInstance):
    def __init__(self):
        super(StackedObjectProxyType, self).__init__(StackedObjectProxy, [])
    def getattr(self, attr, context):
        u = super(StackedObjectProxyType, self).get_name(attr, context)
        if u:
            return u

        context.log_error("Warning: undefined attribute '%s' would default to a string" % (attr,))
        return Union.EMPTY
        # context.log_error("Warning: undefined attribute '%s' is defaulting to a string" % (attr,))
        # return Union(STR)

pylons.setattr("c", Union(StackedObjectProxyType()))

def load(e):
    KNOWN_MODULES["pylons"] = pylons
