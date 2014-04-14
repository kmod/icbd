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

        UserClassType,
        CustomInstance,
        CustomClass,

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

sqlalchemy = Module("sqlalchemy", "__builtin__")
schema = Module("schema", "__builtin__")
sqlalchemy.setattr("schema", Union(schema))

MetaData = UserClassType("MetaData", (ObjectClass,))

class TableClassType(CustomClass):
    def __init__(self):
        super(TableClassType, self).__init__("Table")

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        assert isinstance(orig_args[0], _ast.Str)
        assert args[0] == Union(STR)
        if args[1] == Union.EMPTY:
            context.log_error("no metadata specified")
            return Union.EMPTY
        assert args[1] == Union(MetaData.instance()), (args[1].display(), args[1].types())

        cols = []
        for a in args[2:]:
            if not a.types():
                return Union.EMPTY
            assert len(a.types()) == 1
            t, = a.types()

            assert isinstance(t, ColumnType)
            cols.append(t)

        t = context.get_cached(self.call)
        if not t:
            t = TableType(orig_args[0].s, cols)
            context.set_cached(self.call, t)
        else:
            assert t._cols == cols, (t._cols, cols)

        return Union(t)

class TableType(CustomInstance):
    def __init__(self, name, cols):
        assert isinstance(name, str)
        for c in cols:
            assert isinstance(c, ColumnType)
        super(TableType, self).__init__(Table, [])

        self._name = name
        self._cols = cols
        for c in cols:
            c._table = self
        col_collection = Union(ColumnCollectionType(cols))
        self.setattr("c", col_collection)
        self.setattr("columns", col_collection)

    def display(self):
        return "Table '%s'" % (self._name,)

class ColumnCollectionType(CustomInstance):
    def __init__(self, cols):
        for c in cols:
            assert isinstance(c, ColumnType)
        super(ColumnCollectionType, self).__init__(ColumnCollection, [])

        for c in cols:
            self.setattr(c._name, Union(c))
        self._cols = cols

class ColumnClassType(CustomClass):
    def __init__(self):
        super(ColumnClassType, self).__init__("Column")

    def call(self, args, keywords, starargs, context, dryrun, orig_args):
        assert isinstance(orig_args[0], _ast.Str)
        assert args[0] == Union(STR)

        t = context.get_cached(self.call)
        if not t:
            if args[1] == Union.EMPTY:
                context.log_error("no column type specified")
                return Union.EMPTY
            t = ColumnType(orig_args[0].s, args[1].types()[0], context)
            context.set_cached(self.call, t)
        else:
            assert t._name == orig_args[0].s
            assert isinstance(args[1].types()[0], FixedFunction) or t._type == args[1].types()[0], (t._type, args[1].types()[0])

        return Union(t)

class ColumnType(CustomInstance):
    def __init__(self, name, coltype, context):
        assert isinstance(name, str)
        if not isinstance(coltype, ColtypeType):
            coltype = coltype.call([], {}, None, context, False, None).types()[0]
        assert isinstance(coltype, ColtypeType), coltype
        super(ColumnType, self).__init__(Column, [])

        self._name = name
        self._type = coltype
        self._table = None # gets set when the table gets created

    def display(self):
        return "Column '%s' (%s)" % (self._name, self._type._t.display())


Table = TableClassType()
Column = ColumnClassType()
ColumnCollection = UserClassType("ColumnCollection", (ObjectClass,))
ColumnCollection.setattr("keys", Union(FixedFunction([InstanceArg(ColumnCollection, [])], InstanceArg(ListClass, [STR]))))

Expression = UserClassType("Expression", (ObjectClass,))
class ExpressionType(CustomInstance):
    def __init__(self, cols):
        assert cols, cols
        assert isinstance(cols, list), cols
        super(ExpressionType, self).__init__(Expression, [])

        self._cols = cols

        f = FixedFunction([ANY], FixedArg(Union(self)), ndefaults=1)
        for n in ("order_by", "limit", "asc", "desc", "not_", "null", "group_by", "offset"):
            self.setattr(n, Union(f))

    def display(self):
        return "Expression (%s)" % (self._cols[0]._table._name)
Expression.setattr("where", Union(FixedFunction([Var(0), ANY], Var(0), ndefaults=1)))

def _table_select_rtn(args, keywords, starargs, context, dryrun, orig_args):
    t = args[0].types()[0]

    r = context.get_cached(_table_select_rtn)
    if not r:
        r = ExpressionType(t._cols)
        context.set_cached(_table_select_rtn, r)
    else:
        if r._cols != t._cols:
            context.log_error("don't pass in different tables, can't analyze that")
            return Union(TOP)
    return Union(r)
def _table_select_display(bind=None):
    if not bind:
        return "() -> Expression"
    else:
        assert isinstance(bind, TableType)
        return "() -> Expression (%s)" % (bind._name)
Table.setattr("select", Union(SpecialFunction(_table_select_rtn, _table_select_display)))





types = Module("types", "__builtin__")
sqlalchemy.setattr("types", Union(types))

# TODO this could be objects, and then we could map the objects to something outside rather than inside the object
class ColtypeType(CustomInstance):
    def __init__(self, t):
        assert isinstance(t, Type)
        super(ColtypeType, self).__init__(ObjectClass, [])
        self._t = t

    def display(self):
        return "ColumnType(%s)" % (self._t.display())

class DateTime(CustomInstance):
    def __init__(self):
        super(DateTime, self).__init__(ObjectClass, [])

    def display(self):
        return "fake_datetime"

for n, t in (
        ("Integer", ColtypeType(INT)),
        ("Boolean", ColtypeType(BOOL)),
        ("Numeric", ColtypeType(FLOAT)),
        ("DateTime", ColtypeType(DateTime())),
        ("Unicode", FixedFunction([INT], FixedArg(Union(ColtypeType(STR))), ndefaults=1)),
        ("String", FixedFunction([INT], FixedArg(Union(ColtypeType(STR))), ndefaults=1)),
        ("Text", FixedFunction([INT], FixedArg(Union(ColtypeType(STR))), ndefaults=1)),
        ):
    types.setattr(n, Union(t))
    sqlalchemy.setattr(n, Union(t))

databases = Module("databases", "__builtin__")
sqlalchemy.setattr("databases", Union(databases))
mysql = Module("mysql", "__builtin__")
databases.setattr("mysql", Union(mysql))

for n, t in (
        ("MSBigInteger", ColtypeType(INT)),
        ("MSTinyInteger", ColtypeType(INT)),
        ("MSText", FixedFunction([INT], FixedArg(Union(ColtypeType(STR))), ndefaults=1)),
        ("MSString", FixedFunction([INT], FixedArg(Union(ColtypeType(STR))), ndefaults=1)),
        ("MSMediumText", FixedFunction([INT], FixedArg(Union(ColtypeType(STR))), ndefaults=1)),
        ("MSTinyText", FixedFunction([INT], FixedArg(Union(ColtypeType(STR))), ndefaults=1)),
        ("MSBlob", FixedFunction([INT], FixedArg(Union(ColtypeType(STR))), ndefaults=1)),
        ("MSTinyBlob", FixedFunction([INT], FixedArg(Union(ColtypeType(STR))), ndefaults=1)),
        ("MSMediumBlob", FixedFunction([INT], FixedArg(Union(ColtypeType(STR))), ndefaults=1)),
        ):
    mysql.setattr(n, Union(t))
    sqlalchemy.setattr(n, Union(t))

for n, t in (
        ("Table", Table),
        ("Column", Column),
        ("Index", FixedFunction([STR, InstanceArg(Column, [])], NONE)),
        ("MetaData", MetaData),
        ):
    schema.setattr(n, Union(t))
    sqlalchemy.setattr(n, Union(t))


engine = Module("engine", "__builtin__")
Engine = UserClassType("Engine", (ObjectClass,))
engine.setattr("create_engine", Union(FixedFunction([STR], FixedArg(Union(Engine.instance())))))
sqlalchemy.setattr("engine", Union(engine))


orm = Module("orm", "__builtin__")
sqlalchemy.setattr("orm", Union(orm))
ScopedSession = UserClassType("ScopedSession", (ObjectClass,))
orm.setattr("scoped_session", Union(FixedFunction([ANY], FixedArg(Union(InstanceType(ScopedSession, []))))))
Connection = UserClassType("Connection", (ObjectClass,))
ScopedSession.setattr("connection", Union(FixedFunction([InstanceArg(ScopedSession, [])], FixedArg(Union(InstanceType(Connection, []))))))

ResultProxy = UserClassType("ResultProxy", (ObjectClass,))
RowProxy = UserClassType("RowProxy", (ObjectClass,))

class ResultProxyType(CustomInstance):
    def __init__(self, cols):
        assert cols, cols
        assert isinstance(cols, list), cols
        for c in cols:
            assert isinstance(c, ColumnType)
        super(ResultProxyType, self).__init__(ResultProxy, [])

        self._cols = cols
        self.setattr("scalar", Union(FixedFunction([], FixedArg(Union(cols[0]._type._t)))))
        self._rptype = RowProxyType(self._cols)
        self.setattr("__iter__", Union(FixedFunction([], FixedArg(Union(InstanceType(Iterator, [Union(self._rptype)]))))))

    def display(self):
        return "ResultProxy (%s)" % (self._cols[0]._table._name)

class RowProxyType(CustomInstance):
    def __init__(self, cols):
        assert cols, cols
        assert isinstance(cols, list), cols
        for c in cols:
            assert isinstance(c, ColumnType)
        super(RowProxyType, self).__init__(RowProxy, [])

        self._cols = cols
        for c in cols:
            self.setattr(c._name, Union(c._type._t))

    def display(self):
        return "RowProxy (%s)" % (self._cols[0]._table._name)

def _fetchone_rtn(args, keywords, starargs, context, dryrun, orig_args):
    r = args[0].types()[0]
    assert isinstance(r, ResultProxyType)
    return Union(r._rptype)
def _fetchone_display(bind=None):
    if not bind:
        return "() -> RowProxy"
    else:
        assert isinstance(bind, ResultProxyType), bind
        return "() -> RowProxy (%s)" % (bind._cols[0]._table._name)
ResultProxy.setattr("fetchone", Union(SpecialFunction(_fetchone_rtn, _fetchone_display)))
ResultProxy.setattr("first", Union(SpecialFunction(_fetchone_rtn, _fetchone_display)))

def _fetchall_rtn(args, keywords, starargs, context, dryrun, orig_args):
    r = args[0].types()[0]
    assert isinstance(r, ResultProxyType)

    t = context.get_cached(_fetchall_rtn)
    if not t:
        t = InstanceType(ListClass, [Union(r._rptype)])
        context.set_cached(_fetchall_rtn, t)

    return Union(t)

def _fetchall_display(bind=None):
    if not bind:
        return "() -> [RowProxy]"
    else:
        assert isinstance(bind, ResultProxyType), bind
        return "() -> [RowProxy (%s)]" % (bind._cols[0]._table._name)

def _fetchmany_display(bind=None):
    if not bind:
        return "(int?) -> [RowProxy]"
    else:
        assert isinstance(bind, ResultProxyType), bind
        return "(int?) -> [RowProxy (%s)]" % (bind._cols[0]._table._name)

ResultProxy.setattr("fetchall", Union(SpecialFunction(_fetchall_rtn, _fetchall_display)))
ResultProxy.setattr("fetchmany", Union(SpecialFunction(_fetchall_rtn, _fetchmany_display)))

ResultProxy.setattr("isinsert", Union(BOOL))

# For insert constructs:
# .inserted_primary_key: list of scalar values corresponding to the list of primary key columns
# .last_inserted_ids(): same as above?

# TODO this only exists For update/delete:
ResultProxy.setattr("rowcount", Union(INT))



def _execute_rtn(args, keywords, starargs, context, dryrun, orig_args):
    if starargs:
        context.log_error("why??")
        return Union.EMPTY

    c = args[0].types()[0]
    assert isinstance(c, InstanceType)
    assert c.cls in (Connection, Engine)
    if len(args[1].types()) != 1:
        context.log_error("bad first arg to execute")
        return Union.EMPTY
    a = args[1].types()[0]
    if a is STR:
        return Union(TOP)

    if a is TOP:
        return Union(TOP)

    if isinstance(a, InstanceType):
        if a.cls is ListClass:
            cols = []
            for t in a.unions[0].types():
                if isinstance(t, ColumnType):
                    cols.append(t)
        elif a.cls is Expression:
            cols = a._cols
        elif a.cls is TupleClass:
            cols = [u.types()[0] for u in a.unions]
        elif a.cls is Column:
            cols = [a]
        else:
            context.log_error("don't understand argument: %s" % (a.display(),))
            return Union.EMPTY
    else:
        context.log_error("didn't expect a %s" % (a.display(),))
        return Union.EMPTY

    t = context.get_cached(_execute_rtn)
    if not t:
        t = ResultProxyType(cols)
        context.set_cached(_execute_rtn, t)
    else:
        assert t._cols == cols
    return Union(t)

Connection.setattr("execute", Union(SpecialFunction(_execute_rtn, lambda *args:"(Expression) -> ResultProxy")))
Engine.setattr("execute", Union(SpecialFunction(_execute_rtn, lambda *args:"(Expression) -> ResultProxy")))

def _select_rtn(args, keywords, starargs, context, dryrun, orig_args):
    if args[0] == Union.EMPTY:
        context.log_error("Don't know what this is a select of")
        return Union.EMPTY

    l = args[0].types()[0]

    if not isinstance(l, InstanceType):
        context.log_error("Passed in a '%s'?" % (l.display(),))
        return Union.EMPTY

    if l.cls is ListClass:
        if l.unions[0] == Union.EMPTY:
            context.log_error("Passed in an empty list of columns")
            return Union.EMPTY
        cols = list(l.unions[0].types())
    elif l.cls is TupleClass:
        # if not all(u.types() for u in l.unions):
            # context.log_error("Passed in a potentially-undefined column")
            # return Union.EMPTY
        cols = [u.types()[0] for u in l.unions if u.types() and isinstance(u.types()[0], ColumnType)]
        if not cols:
            context.log_error("Passed in no analyzable columns")
            return Union.EMPTY
    elif l.cls is Column:
        cols = [l]
    elif l.cls is ColumnCollection:
        cols = list(l._cols)
        assert all(isinstance(c, ColumnType) for c in cols), cols
    else:
        raise Exception(l.cls.name)

    assert cols
    for c in cols:
        if not isinstance(c, ColumnType):
            context.log_error("Passed in '%s' instead of a column?" % (c.display(),))
            return Union.EMPTY

    t = context.get_cached(_select_rtn)
    if not t:
        t = ExpressionType(cols)
        context.set_cached(_select_rtn, t)
    else:
        if cols != t._cols:
            context.log_error("don't pass in different columns, can't analyze that")
            return Union(TOP)
    return Union(t)

sql = Module("sql", "__builtin__")
sqlalchemy.setattr("sql", Union(sql))
select = SpecialFunction(_select_rtn, lambda *args:"([cols],where) -> ResultProxy")
sqlalchemy.setattr("select", Union(select))
sql.setattr("select", Union(select))

sqlalchemy.setattr("and_", Union.EMPTY)

def _mapper_rtn(args, keywords, starargs, context, dryrun, orig_args):
    if args[0] == Union.EMPTY or args[1] == Union.EMPTY:
        return Union.EMPTY

    cls = args[0].types()[0]
    table = args[1].types()[0]

    for col in table._cols:
        cls.setattr(col._name, Union(col._type._t))
    return Union.EMPTY
mapper = SpecialFunction(_mapper_rtn)

def load(e):
    KNOWN_MODULES["sqlalchemy"] = sqlalchemy
