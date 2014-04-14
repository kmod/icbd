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

        UserFunction,
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

        UserClassType,
        CustomClass,
        CustomInstance,

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

def _load(e, fn):
    generated = {}
    type_map = {
            "int64":Union(INT),
            "int32":Union(INT),
            "string":Union(STR),
            "bytes":Union(STR),
            "double":Union(FLOAT),
            "bool":Union(BOOL),
            }
    with open(fn) as f:
        stack = []
        type_stack = []
        field_names = []
        for l in f:
            if '//' in l:
                l = l[:l.find('//')]
            sp = l.split()
            if not sp:
                continue
            if sp[0] == "message":
                cls = Union(UserClassType(sp[1], (ObjectClass,)))
                if stack:
                    type_stack[-1][sp[1]] = cls
                    stack[-1].setattr(sp[1], cls)
                else:
                    generated[sp[1]] = cls

                stack.append(cls)
                type_stack.append({})
                field_names.append([])
            elif sp[0] in ("required", "optional", "repeated"):
                t = None

                for types in [type_map] + list(reversed(type_stack)) + [generated]:
                    t = types.get(sp[1])
                    if t:
                        break

                assert t, sp[1]
                assert isinstance(t, Union)
                name = sp[2]

                if sp[0] == "repeated":
                    t = Union(InstanceType(ListClass, [t]))
                stack[-1].setattr(name, t)
                field_names[-1].append(name)
            elif sp[0] == "enum":
                assert stack
                # stack[-1].setattr(sp[1], Union(INT))
                type_stack[-1][sp[1]] = Union(INT)
                stack.append(None)
                type_stack.append(None)
                field_names.append(None)
            elif len(sp) >= 2 and sp[1] == '=':
                assert stack[-1] is None
                stack[-2].setattr(sp[0], Union(INT))
            elif sp[0] == "}":
                fields = field_names.pop()
                c = stack.pop()
                if isinstance(c, Union):
                    [c] = c.types()
                    field_types = [c._attributes[f] for f in fields]
                    args = []
                    for u in field_types:
                        assert len(u.types()) == 1
                        [t] = u.types()
                        if isinstance(t, UserClassType):
                            args.append(FixedArg(Union(t.instance())))
                        else:
                            args.append(FixedArg(u))
                    c.setattr("__init__", Union(FixedFunction([InstanceArg(c, [])] + args, NONE, ndefaults=len(field_types), arg_names=["self"] + fields)))
                type_stack.pop()
            else:
                raise Exception(l)

    assert not stack
    assert not type_stack

    e.add_overrides(generated)

