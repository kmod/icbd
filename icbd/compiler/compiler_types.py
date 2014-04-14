import _ast
import inspect
import re
import sys
import traceback

from . import closure_analyzer
from .code_emitter import CodeEmitter

DEBUG_CHECKS = True

BINOP_MAP = {
        _ast.Add:"__add__",
        _ast.Sub:"__sub__",
        _ast.Mult:"__mul__",
        _ast.BitOr:"__or__",
        _ast.BitXor:"__xor__",
        _ast.BitAnd:'__and__',
        _ast.LShift:'__lshift__',
        _ast.RShift:'__rshift__',
        _ast.Mod:'__mod__',
        _ast.Div:'__div__',
        _ast.Pow:'__pow__',
        }

COMPARE_MAP = {
        _ast.Lt:"__lt__",
        _ast.Gt:"__gt__",
        _ast.LtE:"__le__",
        _ast.GtE:"__ge__",
        _ast.Eq:"__eq__",
        _ast.NotEq:"__ne__",
        _ast.In:"__contains__",
        }

COMPARE_REFLECTIONS = {
        _ast.Lt:_ast.Gt,
        _ast.Gt:_ast.Lt,
        _ast.LtE:_ast.GtE,
        _ast.GtE:_ast.LtE,
        _ast.Eq:_ast.Eq,
        _ast.NotEq:_ast.NotEq,
        }

# The same thing as an AttributeError, but for the compiled code rather than the compiler code
class UserAttributeError(Exception):
    pass

# The same thing as an TypeError, but for the compiled code rather than the compiler code
class UserTypeError(Exception):
    pass

# AN error that you tried to instantiate an object that has no first-class representation (such as a polymorphic function, or module)
class CantInstantiateException(Exception):
    pass

class AttributeAccessType(object):
    """ An enum of the possible ways that an object attribute will
    be generated. """

    # A member variable of the object, that has a persistent memory location
    FIELD = "field"

    # A field that the object has implicitly, and is generated on access (such as __class__)
    IMPLICIT_FIELD = "implicit_field"

    # A class-level method of the object that doesn't change, which is instantiated into an instancemethod on access
    CONST_METHOD = "attr_const_method"

# convert everything to IEEE754 format to make sure we don't lose any precision in serialization
def format_float(f):
    import struct
    import binascii
    s = struct.pack('d', f)
    return "0x" + binascii.hexlify(s[::-1])

def is_emitter(e):
    from .codegen import CodeEmitter
    return e is None or isinstance(e, CodeEmitter)

_cached_templates = {}
def get_template(name):
    if name not in _cached_templates:
        _cached_templates[name] = open("templates/%s.tll" % name).read()
    return _cached_templates[name]

def convert_none_to_void_ll(code):
    code = code.replace("define %none* ", "define void ")
    code = code.replace("declare %none* ", "declare void ")
    code = re.sub("ret (%none\*|void) [^ \n]*", "ret void", code)

    def repl(m):
        return "%s = inttoptr i64 0 to %%none*\n    call void " % (m.group(1),)
    code = re.sub("([^ ]*) = call (%none\*|void) ", repl, code)
    code = code.replace("%none* (", "void (") # function pointers
    return code

_cached_ctemplates = {}
def get_ctemplate(name):
    if name not in _cached_ctemplates:
        _cached_ctemplates[name] = open("templates/%s.tc" % name).read()
    return _cached_ctemplates[name]

def eval_ctemplate(name, em, locals_):
    assert "em" not in locals_
    template = get_ctemplate(name)
    return _eval_template(name, template, em, locals_, output="c")

def eval_template(name, em, locals_):
    assert "em" not in locals_
    template = get_template(name)
    return _eval_template(name, template, em, locals_, output="llvm")

def _make_typeobj(em, llvm_name, display_name=None):
    display_name = display_name or llvm_name
    nameptr = em.get_str_ptr(display_name)
    return ("""@%(n)s_typename = global %%string {i64 1, i64 %(len)s, i8* %(nameptr)s, [0 x i8] zeroinitializer}\n"""
        """@%(n)s_typeobj = global %%type {i64 1, %%string* @%(n)s_typename, %%type* null}""") % {
                'n': llvm_name,
                'nameptr': nameptr,
                'len': len(display_name)
                }

def _eval_template(name, template, _em, locals_, output):
    lines = template.split('\n')
    newlines = []

    locals_['make_typeobj'] = _make_typeobj

    assert isinstance(_em, CodeEmitter)

    if_state = []

    def convert(em, lineno, l):
        ignore = not all(if_state)
        locals_['em'] = em
        get_written = lambda: em.get_llvm().replace('\n', '\n    ') if output == "llvm" else em.get_c()
        assert not get_written(), get_written()

        if '///' in l:
            return convert(em, lineno, l[:l.find('///')])

        m = re.search(r"\$+\(", l)
        if not m:
            if ignore:
                return ""
            return l

        ndollar = len(m.group()) - 1
        assert ndollar in (1, 2, 3)
        nopen = 1
        quote = None
        for i in xrange(m.end(), len(l)):
            if l[i] == '\\':
                assert l[i+1] in "nt", l[i+1]
            if quote:
                if l[i] == quote:
                    quote = None
                continue

            if l[i] in '\'\"':
                quote = l[i]
                continue

            if l[i] == '(':
                nopen += 1
            elif l[i] == ')':
                nopen -= 1
                if nopen == 0:
                    end = i
                    break
        else:
            raise Exception("Unclosed parethesis at line %d" % (lineno+1,))

        to_eval = l[m.end():end]
        if to_eval.startswith("if "):
            if ignore:
                conditional = False
            else:
                conditional = eval(to_eval[3:], globals(), locals_)
            if_state.append(conditional)
            evaled = ""
        elif to_eval == "endif":
            if_state.pop()
            evaled = ""
        elif ndollar == 1:
            if ignore:
                evaled = ""
            else:
                evaled = str(eval(to_eval, globals(), locals_))
            assert not get_written()
        else:
            if not ignore:
                exec to_eval in globals(), locals_

            evaled = get_written()
            em = CodeEmitter(_em)

            if ndollar == 3:
                end += 3
            # assert m.start() == 0, l
            # evaled = "    " + evaled
        assert not get_written(), get_written()

        if ignore:
            return convert(em, lineno, l[end + 1:])
        else:
            return l[:m.start()] + evaled + convert(em, lineno, l[end + 1:])

    in_3dollar = False
    for_3dollar = []
    for lineno, l in enumerate(lines):
        if "$$$(" in l:
            assert not in_3dollar, "can't nest $$$ sections"
            in_3dollar = True

        if in_3dollar:
            for_3dollar.append(l)
            if ")$$$" in l:
                # Strip of leading writespace:
                for i, c in enumerate(for_3dollar[0]):
                    if c != ' ':
                        break
                for_3dollar = [s[i:] for s in for_3dollar]

                l = '\n'.join(for_3dollar)
                for_3dollar = []
                in_3dollar = False
            else:
                continue

        try:
            newlines.append(convert(CodeEmitter(_em), lineno, l))
            if len(newlines) >= 2 and newlines[-1] == newlines[-2] == '':
                newlines.pop()
        except Exception:
            print >>sys.stderr, "failed to convert line %d of %s template '%s', args %s" % (lineno + 1, output, name, locals_)
            # print l
            raise
    assert not in_3dollar, "unterminated $$$ section"
    return '\n'.join(newlines)

def raw_func_name(llvm_func_name):
    if llvm_func_name.startswith('@'):
        return llvm_func_name[1:]
    elif llvm_func_name.startswith("#!"):
        return llvm_func_name
    else:
        raise Exception(llvm_func_name)

class Variable(object):
    def __init__(self, t, v, nrefs, marked):
        assert isinstance(t, MT)
        if isinstance(t, UnboxedFunctionMT):
            assert t.ndefaults == len(v[1])
        if t is Float:
            # Make sure that the compiler doesn't use any potentially-lossy float representations
            assert not isinstance(v, float), v
            if isinstance(v, str):
                assert not re.match("\d*\.?\d*$", v), v

        if isinstance(t, (StrConstantMT, UnboxedInstanceMethod, _SpecialFuncMT, UnboxedFunctionMT, ClassMT, UnboxedTupleMT, PolymorphicFunctionMT)):
            assert isinstance(v, tuple), (t, v)
            if isinstance(t, UnboxedFunctionMT):
                assert len(v) == 3
            assert not marked
        else:
            if isinstance(t, ClosureMT):
                assert isinstance(v, str) or v is None
            else:
                assert isinstance(v, (int, float, str)), (t, v)
        assert isinstance(nrefs, int)
        assert isinstance(marked, bool)
        self.t = t
        self.v = v
        self.nrefs = nrefs
        self.marked = marked

        # def mkwrap(n):
            # _f = getattr(self.t, n)
            # def inner(c, *args):
                # return _f(c, self.v, *args)
            # return inner

    # TODO shouldnt be forgetting about owned references?
    # def __del__(self):
        # if self.owned:
            # import traceback
            # traceback.print_stack()

    if DEBUG_CHECKS:
        def __getattribute__(self, n):
            # Allow Variable methods, but only those, to operate on things with 0 nrefs
            if sys._getframe(1).f_code not in Variable._ok_code:
                assert object.__getattribute__(self, "nrefs") > 0, n
            return object.__getattribute__(self, n)

    def equiv(self, rhs):
        assert self.nrefs > 0
        # hax:
        d1 = dict(self.__dict__)
        d2 = dict(rhs.__dict__)
        v1 = d1.pop('v')
        v2 = d2.pop('v')
        if isinstance(v1, tuple):
            assert isinstance(v2, tuple)
            assert len(v1) == len(v2)
            for i in xrange(len(v1)):
                if isinstance(v1[i], Variable):
                    if not v1[i].equiv(v2[i]):
                        return False
                elif isinstance(v1[i], list):
                    assert isinstance(v2[i], list)
                    l1 = v1[i]
                    l2 = v2[i]
                    if len(l1) != len(l2):
                        return False
                    for j in xrange(len(l1)):
                        if not l1[j].equiv(l2[j]):
                            return False
                elif v1[i] != v2[i]:
                    return False
        else:
            if v1 != v2:
                return False
        return d1 == d2
        # return self.t == rhs.t and self.v == rhs.v and self.nrefs == rhs.nrefs and 

    def split(self, em):
        """
        Split off a copy of this variable, and ensure it's marked
        """

        assert is_emitter(em), em
        """
        assert self.nrefs > 0
        if not self.marked:
            r = self.t.incref_llvm(em, self.v)
            if r:
                em.pl(r)
        else:
            # Optimization: if this was marked, just "transfer" the mark
            self.marked = False
        return Variable(self.t, self.v, 1, True)
        """
        assert self.nrefs > 0
        r = self.t.incref_llvm(em, self.v)
        if r:
            em.pl(r + " ; split")
        r = self.t.incref_c(em, self.v)
        if r:
            em.pc(r + "; // split")
        return Variable(self.t, self.v, 1, True)

    def dup(self, dup_cache):
        """
        Makes a copy of this variable object.
        Only makes sense at a meta level, ie we want to distribute copies of this variable
        to all successor nodes.
        """
        assert self.nrefs > 0
        if self not in dup_cache:
            dup_cache[self] = Variable(self.t, self.t.dup(self.v, dup_cache), self.nrefs, self.marked)
        return dup_cache[self]

    def incvref(self, em):
        assert is_emitter(em), em
        assert self.nrefs > 0
        self.nrefs += 1
        # print "incvref %s" % self, self.nrefs
        # em.pl("; inc: %s now has %d vrefs" % (self.v, self.nrefs))

    def decvref(self, em, note=None):
        assert is_emitter(em)
        # print; import traceback; traceback.print_stack()
        assert self.nrefs > 0, (self, self.t)
        self.nrefs -= 1
        # print "decvref %s" % self, self.nrefs
        # em.pl("; dec: %s now has %d vrefs" % (self.v, self.nrefs))
        if self.nrefs == 0:
            if isinstance(self.v, tuple):
                assert not self.marked
                self.t.free(em, self.v)
            elif self.marked:
                self.nrefs += 2 # for the getattr; add 2 since we don't want it to hit zero again
                f = self.getattr(em, "__decref__")
                f.call(em, [])
                self.nrefs -= 1 # for the extra +1 nrefs
                assert self.nrefs == 0, self.nrefs
                # This shouldn't matter but it's safer:
                self.marked = False

    def getattr(self, em, attr, clsonly=False, decvref=True, **kw):
        assert is_emitter(em)
        assert self.nrefs > 0
        try:
            r = self.t.getattr(em, self, attr, clsonly=clsonly, **kw)
        finally:
            if decvref:
                self.decvref(em, "getattr")
        return r

    def getattrptr(self, em, attr):
        assert is_emitter(em)
        assert self.nrefs > 0
        try:
            r = self.t.getattrptr(em, self, attr)
        finally:
            self.decvref(em, "getattrptr")
        return r

    def setattr(self, em, attr, var):
        assert is_emitter(em)
        assert self.nrefs > 0
        assert isinstance(var, Variable)
        r = self.t.setattr(em, self.v, attr, var)
        self.decvref(em, "setattr")
        return r

    def call(self, em, args, expected_type=None):
        assert is_emitter(em)
        assert self.nrefs > 0
        try:
            r = self.t.call(em, self.v, args, expected_type=expected_type)
        finally:
            self.decvref(em, "call [was func]")
        return r

    def convert_to(self, em, t):
        assert is_emitter(em)
        assert self.nrefs > 0
        assert isinstance(t, MT)
        return self.t.convert_to(em, self, t)

Variable._ok_code = list(func.func_code for name, func in inspect.getmembers(Variable, inspect.ismethod))

class MT(object):
    def __init__(self):
        self.initialized = set()
        self.initializing = set()
        self.__st = ''.join(traceback.format_stack()) # TODO take this out once I'm done debugging

    def __check_initialized(self, stage):
        if stage not in self.initialized:
            print self.__st
            raise Exception(self)

    def c_type(self):
        l = self.llvm_type()
        if l.startswith('%'):
            return l[1:]
        assert l in ('i1', 'i64', "double")
        return l

    def incref_llvm(self, em, v):
        assert is_emitter(em)
        emitter = CodeEmitter(em)
        Variable(self, v, 1, False).getattr(emitter, "__incref__").call(emitter, [])
        return emitter.get_llvm()

    def incref_c(self, em, v):
        assert is_emitter(em)
        emitter = CodeEmitter(em)
        Variable(self, v, 1, False).getattr(emitter, "__incref__").call(emitter, [])
        return emitter.get_c()

    def decref_llvm(self, em, v):
        assert is_emitter(em)
        emitter = CodeEmitter(em)
        Variable(self, v, 1, False).getattr(emitter, "__decref__").call(emitter, [])
        return emitter.get_llvm()

    def decref_c(self, em, v):
        assert is_emitter(em)
        emitter = CodeEmitter(em)
        Variable(self, v, 1, False).getattr(emitter, "__decref__").call(emitter, [])
        return emitter.get_c()

    # All types default to raised types
    def get_instantiated(self):
        return self

    def dup(self, v, dup_cache):
        assert isinstance(v, (float, int, str)), (self, repr(v))
        return v

    def initialize(self, em, stage):
        assert stage in ("attrs", "write")
        if stage == "write":
            self.initialize(em, "attrs")

        assert stage not in self.initializing
        if stage not in self.initialized:
            self.initializing.add(stage)
            self._initialize(em, stage)
            self.initializing.remove(stage)
            self.initialized.add(stage)

    def get_attr_types(self):
        self.__check_initialized("attrs")
        if hasattr(self, "class_methods"):
            r = {}
            for name, v in self.class_methods.iteritems():
                if name in r:
                    continue
                r[name] = (UnboxedInstanceMethod(self, v.t), AttributeAccessType.CONST_METHOD)

            if hasattr(self, "typeobj_name"):
                r["__class__"] = (Type, AttributeAccessType.IMPLICIT_FIELD)
            return r
        raise NotImplementedError(type(self))

    def getattr(self, em, v, attr, clsonly):
        self.__check_initialized("attrs")
        if attr == "__class__" and hasattr(self, "typeobj_name"):
            return Variable(Type, self.typeobj_name, 1, False)
        if hasattr(self, "class_methods"):
            if attr not in self.class_methods:
                raise UserAttributeError((self, attr))

            r = self.class_methods[attr]
            r.incvref(em)
            return UnboxedInstanceMethod.make(em, v, r)
        raise NotImplementedError((type(self), attr))

    def hasattr(self, attr):
        self.__check_initialized("attrs")
        if hasattr(self, "class_methods"):
            return attr in self.class_methods
        raise NotImplementedError(type(self))

    def get_method_name(self, em, name):
        self.__check_initialized("attrs")
        fake_var = Variable(None_, "null", 1, False)
        attr = self.getattr(em, fake_var, name, clsonly=True)
        assert isinstance(attr.t, UnboxedInstanceMethod)
        f = attr.v[1]

        assert isinstance(f, Variable)
        if isinstance(f.t, PolymorphicFunctionMT):
            f = f.v[0][0]
        assert isinstance(f.t, UnboxedFunctionMT), f.t
        assert len(f.v) == 3
        assert f.v[2] is None
        r = f.v[0]
        attr.decvref(em)
        return raw_func_name(r)

    def _can_convert_to(self, t):
        return False

    def can_convert_to(self, t):
        if t is self:
            return True
        if isinstance(t, BoxedMT):
            return t.can_convert_from(self)
        return self._can_convert_to(t)

    def _convert_to(self, em, var, t):
        if isinstance(t, BoxedMT):
            return t.convert_from(em, var)
        raise UserTypeError("Don't know how to convert %s to %s" % (self, t))

    def convert_to(self, em, var, t):
        self.initialize(em, "write")
        assert var.t is self
        if t is self:
            return var

        r = self._convert_to(em, var, t)
        assert r.t is t, (self, t, r.t.__dict__, t.__dict__)
        return r

    def call(self, em, v, args, expected_type=None):
        self.initialize(em, "write")
        return self.getattr(em, Variable(self, v, 1, False), "__call__", clsonly=True).call(em, args, expected_type=expected_type)

def singleton(cls):
    r = cls()
    cls.__init__ = None
    return r

class SliceMT(MT):
    def llvm_type(self):
        return "%slice*"

    @staticmethod
    def setup_class_methods():
        SliceMT.class_methods = {
            "__incref__": Variable(UnboxedFunctionMT(None, None, [Slice], None_), ("@slice_incref", [], None), 1, False),
            "__decref__": Variable(UnboxedFunctionMT(None, None, [Slice], None_), ("@slice_decref", [], None), 1, False),
        }

    def _can_convert_to(self, t):
        return False

    @staticmethod
    def create(em, start, end, step):
        assert start is None or isinstance(start, Variable)
        assert end is None or isinstance(end, Variable)
        assert step is None or isinstance(step, Variable)

        flags = 0
        if start:
            flags |= 1
        if end:
            flags |= 2

        name = "%" + em.mkname()
        start_s = start.v if start else 0
        end_s = end.v if end else 0
        step_s = step.v if step else 1
        em.pl("%s = call %%slice* @slice_alloc(i64 %d, i64 %s, i64 %s, i64 %s)" % (name, flags, start_s, end_s, step_s))
        em.pc("#error unimplemented 0")

        for arg in start, end, step:
            if arg:
                arg.decvref(em)
        return Variable(Slice, name, 1, True)
Slice = singleton(SliceMT)
Slice.initialized = ("attrs", "write")

class StrConstantMT(MT):
    def dup(self, v, dup_cache):
        return v

    def free(self, em, v):
        pass

    def getattr(self, em, v, attr, clsonly):
        if attr == "__mod__":
            return UnboxedInstanceMethod.make(em, v, Variable(StrFormat, (), 1, False))
        # Returning a method that takes a str will cause this StrConstant
        # to get upconverted on every call to the method; not most optimized
        # but it works out:
        return Str.getattr(em, v, attr, clsonly)

    def get_instantiated(self):
        return Str

    def _can_convert_to(self, t):
        return t is Str or Str._can_convert_to(t)

    __converted = {}
    def _convert_to(self, em, var, t):
        if t is not Str:
            str_v = self._convert_to(em, var, Str)
            return Str.convert_to(em, str_v, t)
        assert t is Str, t
        [s] = var.v

        if s not in StrConstantMT.__converted:
            r = "@" + em.mkname("str")
            ptr = em.get_str_ptr(s)
            em.llvm_tail.write("%s = global %%string {i64 1, i64 %d, i8* %s, [0 x i8] zeroinitializer}\n" % (r, len(s), ptr))
            StrConstantMT.__converted[s] = r

        var.decvref(em)
        return Variable(Str, StrConstantMT.__converted[s], 1, False)
StrConstant = singleton(StrConstantMT)
StrConstant.initialized = ("attrs", "write")

class NoneMT(MT):
    def llvm_type(self):
        return "%none*"

    @staticmethod
    def setup_class_methods():
        em = None
        NoneMT.class_methods = {
            "__incref__": Variable(UnboxedFunctionMT(em, None, [None_], None_), ("@none_incref", [], None), 1, False),
            "__decref__": Variable(UnboxedFunctionMT(em, None, [None_], None_), ("@none_decref", [], None), 1, False),
            "__repr__": Variable(UnboxedFunctionMT(em, None, [None_], Str), ("@none_repr", [], None), 1, False),
            "__eq__": Variable(UnboxedFunctionMT(em, None, [None_, None_], Bool), ("@none_eq", [], None), 1, False),
        }
        NoneMT.class_methods["__str__"] = NoneMT.class_methods["__repr__"]

    def c_type(self):
        return "void*"

    def dup(self, v, dup_cache):
        return v

    def _can_convert_to(self, t):
        return t not in (Int, Float, Bool, StrConstantMT, UnboxedTupleMT, UnboxedInstanceMethod, UnboxedFunctionMT)

    def _convert_to(self, em, var, t):
        assert t is not None_
        var.decvref(em)
        return Variable(t, "null", 1, True)
None_ = singleton(NoneMT)
None_.initialized = ("attrs", "write")

class _SpecialFuncMT(MT):
    def __init__(self):
        super(_SpecialFuncMT, self).__init__()
        self.initialized = ("attrs", "write")

    def call(self, em, v, args, expected_type=None):
        raise NotImplementedError()

    def dup(self, v, dup_cache):
        assert not v
        return v

    def free(self, em, v):
        assert v == ()
        return None

    def _can_convert_to(self, t):
        return False

class LenMT(_SpecialFuncMT):
    def call(self, em, v, args, expected_type=None):
        assert not v
        assert len(args) == 1
        [_v] = args
        return _v.getattr(em, "__len__", clsonly=True).call(em, [])
Len = singleton(LenMT)

class StrFuncMT(_SpecialFuncMT):
    def call(self, em, v, args, expected_type=None):
        assert not v
        assert len(args) == 1
        [_v] = args
        return _v.getattr(em, "__str__", clsonly=True).call(em, [])
StrFunc = singleton(StrFuncMT)

class ReprFuncMT(_SpecialFuncMT):
    def call(self, em, v, args, expected_type=None):
        assert not v
        assert len(args) == 1
        [_v] = args
        return _v.getattr(em, "__repr__", clsonly=True).call(em, [])
ReprFunc = singleton(ReprFuncMT)

class NrefMT(_SpecialFuncMT):
    def call(self, em, v, args, expected_type=None):
        assert not v
        assert len(args) == 1
        [_v] = args
        return _v.getattr(em, "__nrefs__", clsonly=True).call(em, [])
Nref = singleton(NrefMT)

class TypeFuncMT(_SpecialFuncMT):
    def call(self, em, v, args, expected_type=None):
        assert not v
        assert len(args) == 1
        [_v] = args
        return _v.getattr(em, "__class__")
TypeFunc = singleton(TypeFuncMT)

class BoolFuncMT(_SpecialFuncMT):
    def call(self, em, v, args, expected_type=None):
        assert not v
        assert len(args) == 1
        [_v] = args
        r = _v.getattr(em, "__nonzero__", clsonly=True).call(em, [])
        assert r.t in (Int, Bool), "__nonzero__ should return bool or int, returned %s" % (r.t,)
        if r.t is Int:
            new_name = "%" + em.mkname()
            em.pl("%s = trunc i64 %s to i1" % (new_name, r.v))
            em.pc("#error unimplemented 1")
            r.decvref(em)
            r = Variable(Bool, new_name, 1, False)
        return r
BoolFunc = singleton(BoolFuncMT)

class IsinstanceMT(_SpecialFuncMT):
    def call(self, em, v, args, expected_type=None):
        assert not v
        assert len(args) == 2
        obj, cls = args

        assert isinstance(cls.t, ClassMT)

        if isinstance(obj.t, InstanceMT):
            r = obj.t.cls is cls.t
            obj.decvref(em)
            cls.decvref(em)
            return Variable(Bool, str(int(r)), 1, False)
        elif isinstance(obj.t, BoxedMT):
            realclass = obj.getattr(em, "__class__")
            r = "%" + em.mkname()
            thisclass = cls.t.get_typeobj(em)

            assert realclass.t is Type
            assert thisclass.t is Type
            em.pl("%s = icmp eq %s %s, %s" % (r, Type.llvm_type(), realclass.v, thisclass.v))
            em.pc("#error unimplemented 2")
            cls.decvref(em)
            return Variable(Bool, r, 1, True)
        else:
            raise Exception(obj.t)
Isinstance = singleton(IsinstanceMT)

class CastMT(_SpecialFuncMT):
    def call(self, em, v, args, expected_type=None):
        assert not v
        assert len(args) == 2
        obj, cls = args

        assert isinstance(cls.t, ClassMT)
        instance_t = cls.t._instance
        if isinstance(obj.t, BoxedMT):
            underlying = obj.t._struct.get(em, obj.v, BoxedMT.UNDERLYING_FIELD_NAME, skip_incref=True)
            name = "%" + em.mkname()

            if instance_t is Float:
                em.pl("%s = call %s @ptr_to_float(%s %s)" % (name, instance_t.llvm_type(), underlying.t.llvm_type(), underlying.v))
            else:
                llvm_cmd = "bitcast"
                if instance_t is Int or instance_t is Bool:
                    llvm_cmd = "ptrtoint"
                em.pl("%s = %s %s %s to %s" % (name, llvm_cmd, underlying.t.llvm_type(), underlying.v, instance_t.llvm_type()))
            em.pc("#error unimplemented 3")
            return Variable(instance_t, name, 1, False)
        else:
            raise Exception(obj.t)
Cast = singleton(CastMT)

class StrFormatMT(_SpecialFuncMT):
    def _extract_format_chars(self, s):
        cur = 0
        rtn = []
        while cur < len(s):
            if s[cur] != '%':
                cur += 1
                continue

            cur += 1
            while s[cur] in " 0123456789+-.#*":
                cur += 1
            c = s[cur]
            cur += 1

            if c == '%':
                continue
            assert c.isalpha()
            rtn.append(c)
        return rtn

    def can_call(self, args):
        return True

    def call(self, em, v, args, expected_type=None):
        assert len(args) == 2
        assert args[0].t is StrConstant, args[0].t
        [fmt] = args[0].v

        if isinstance(args[1].t, UnboxedTupleMT):
            data = list(args[1].v)
        elif isinstance(args[1].t, TupleMT):
            raise NotImplementedError()
        else:
            data = [args[1]]

        chars = self._extract_format_chars(fmt)
        assert len(chars) == len(data), "Wrong number of format arguments specified (need %d but got %d)" % (len(chars), len(data))

        for i in xrange(len(chars)):
            ch = chars[i]
            if ch == 'd':
                assert data[i].t is Int
            elif ch == 's':
                if data[i].t is not Str:
                    data[i] = StrFunc.call(em, (), [data[i]])
                assert data[i].t is Str
            elif ch == 'f':
                assert data[i].t is Float
            else:
                raise Exception("Unsupported format character: '%s'" % ch)

        s = args[0].convert_to(em, Str)
        name = '%' + em.mkname()
        em.pl("%s = call %%string* (%%string*, ...)* @str_format(%s)" % (name, ', '.join(["%s %s" % (v.t.llvm_type(), v.v) for v in [s] + data])))
        em.pc("#error unimplemented 4")

        for d in [s] + data:
            d.decvref(em)

        return Variable(Str, name, 1, True)

StrFormat = singleton(StrFormatMT)

class MapFuncMT(_SpecialFuncMT):
    def call(self, em, v, args, expected_type=None):
        assert len(args) == 2
        args[0] = args[0].convert_to(em, args[0].t.get_instantiated())
        assert isinstance(args[0].t, CallableMT), (args[0].t,)
        assert isinstance(args[1].t, ListMT)

        f = args[0]
        l = args[1]
        assert len(f.t.arg_types) >= 1 and len(f.t.arg_types) - f.t.ndefaults <= 1, (len(f.t.arg_types), f.t.ndefaults)
        assert f.t.arg_types[0] is l.t.elt_type

        name = MapFuncMT.get_name(em, f.t.arg_types[0], f.t.rtn_type)
        callable_type = CallableMT.make_callable([f.t.arg_types[0]], 0, f.t.rtn_type)
        f = args[0] = f.convert_to(em, callable_type)

        r = '%' + em.mkname()
        r_type = ListMT.make_list(f.t.rtn_type)
        r_type.initialize(em, "write")
        em.pl('%s = call %s @%s(%s %s, %s %s)' % (r, r_type.llvm_type(), name, f.t.llvm_type(), f.v, l.t.llvm_type(), l.v))
        em.pc("#error unimplemented 5")

        for a in args:
            a.decvref(em)

        return Variable(r_type, r, 1, True)

    __made_maps = {}
    @staticmethod
    def get_name(em, arg_type, ret_type):
        mem_key = (arg_type, ret_type)
        if mem_key not in MapFuncMT.__made_maps:
            name = "map%d" % len(MapFuncMT.__made_maps)
            template = eval_ctemplate("map", em, {
                'input_type':arg_type,
                'output_type':ret_type,
                'name':name,
                })
            em.c_head.write(template)
            MapFuncMT.__made_maps[mem_key] = name

            ret_list = ListMT.make_list(ret_type)
            ret_list.initialize(em, "write")
            arg_list = ListMT.make_list(arg_type)
            arg_list.initialize(em, "write")
            callable_type = CallableMT.make_callable([arg_type], 0, ret_type)
            callable_type.initialize(em, "write")
            em.llvm_head.write("declare %s @%s(%s, %s)\n" % (ListMT.make_list(ret_type).llvm_type(), name, callable_type.llvm_type(), ListMT.make_list(arg_type).llvm_type()))

        return MapFuncMT.__made_maps[mem_key]

MapFunc = singleton(MapFuncMT)

class ReduceFuncMT(_SpecialFuncMT):
    def call(self, em, v, args, expected_type=None):
        assert len(args) == 3

        f, l, initial = args
        f = f.convert_to(em, f.t.get_instantiated())
        assert isinstance(f.t, CallableMT), (f.t,)
        assert isinstance(l.t, ListMT)

        accum_type = make_common_supertype([f.t.rtn_type, initial.t])
        print accum_type, f.t.rtn_type, initial.t
        elt_type = l.t.elt_type

        assert len(f.t.arg_types) == 2
        assert accum_type.can_convert_to(f.t.arg_types[0]), (accum_type, f.t.arg_types[0])
        assert elt_type.can_convert_to(f.t.arg_types[1])

        name = ReduceFuncMT.get_name(em, accum_type, elt_type)
        callable_type = CallableMT.make_callable([accum_type, elt_type], 0, accum_type)
        converted_f = f.convert_to(em, callable_type)
        converted_initial = initial.convert_to(em, accum_type)

        r = '%' + em.mkname()
        em.pl('%s = call %s @%s(%s %s, %s %s, %s %s)' % (r, accum_type.llvm_type(), name, converted_f.t.llvm_type(), converted_f.v, l.t.llvm_type(), l.v, accum_type.llvm_type(), converted_initial.v))
        em.pc("#error unimplemented 5")

        for a in (converted_f, l, converted_initial):
            a.decvref(em)

        return Variable(accum_type, r, 1, True)

    __made_reduces = {}
    @staticmethod
    def get_name(em, accum_type, elt_type):
        mem_key = (accum_type, elt_type)
        if mem_key not in ReduceFuncMT.__made_reduces:
            name = "reduce%d" % len(ReduceFuncMT.__made_reduces)

            arg_list = ListMT.make_list(elt_type)
            arg_list.initialize(em, "write")
            callable_type = CallableMT.make_callable([accum_type, elt_type], 0, accum_type)
            callable_type.initialize(em, "write")

            template = eval_ctemplate("reduce", em, {
                'accum_type':accum_type,
                'elt_type':elt_type,
                'list_type':arg_list,
                'callable_type':callable_type,
                'name':name,
                })
            em.c_head.write(template)
            ReduceFuncMT.__made_reduces[mem_key] = name

            em.llvm_head.write("declare %s @%s(%s, %s, %s)\n" % (accum_type.llvm_type(), name, callable_type.llvm_type(), ListMT.make_list(elt_type).llvm_type(), accum_type.llvm_type()))

        return ReduceFuncMT.__made_reduces[mem_key]

ReduceFunc = singleton(ReduceFuncMT)

class EnumerateMT(_SpecialFuncMT):
    def call(self, em, v, args, expected_type=None):
        assert len(args) == 1
        args[0] = args[0].convert_to(em, args[0].t.get_instantiated())
        assert isinstance(args[0].t, ListMT), (args[0].t,)

        l = args[0]

        name = EnumerateMT.get_name(em, l.t)
        rtn_type = ListMT.make_list(TupleMT.make_tuple([Int, l.t.elt_type]))

        r = "%" + em.mkname()
        em.pl("%s = call %s @%s(%s %s)" % (r, rtn_type.llvm_type(), name, l.t.llvm_type(), l.v))
        em.pc("#error unimplemented 6")

        l.decvref(em)
        return Variable(rtn_type, r, 1, True)

    __made_names = {}
    @staticmethod
    def get_name(em, l):
        assert isinstance(l, ListMT)
        mem_key = (l,)
        if mem_key not in EnumerateMT.__made_names:
            name = "enumerate%d" % len(EnumerateMT.__made_names)
            rtn_elt_type = TupleMT.make_tuple([Int, l.elt_type])
            rtn_elt_type.initialize(em, "write")
            rtn_type = ListMT.make_list(rtn_elt_type)
            rtn_type.initialize(em, "write")
            template = eval_ctemplate("enumerate", em, {
                'input_type':l,
                'return_type':rtn_type,
                'name':name,
                })
            em.c_head.write(template)
            EnumerateMT.__made_names[mem_key] = name

            em.llvm_head.write("declare %s @%s(%s)\n" % (rtn_type.llvm_type(), name, l.llvm_type()))

        return EnumerateMT.__made_names[mem_key]
Enumerate = singleton(EnumerateMT)

class MinFuncMT(_SpecialFuncMT):
    def __init__(self, type):
        self._type = type

    def can_call(self, args):
        return len(args) == 1

    def call(self, em, v, args, expected_type=None):
        assert len(args) == 1
        args[0] = args[0].convert_to(em, args[0].t.get_instantiated())
        l = args[0]

        name = self._type + str(MinFuncMT.get_num(em, l.t))

        rtn_type = l.t.get_attr_types()['__iter__'][0].get_instantiated().rtn_type.get_attr_types()['next'][0].get_instantiated().rtn_type
        r = "%" + em.mkname()
        em.pl("%s = call %s @%s(%s %s)" % (r, rtn_type.llvm_type(), name, l.t.llvm_type(), l.v))
        em.pc("#error unimplemented 21")

        l.decvref(em)
        return Variable(rtn_type, r, 1, True)

    __made_names = {}
    @staticmethod
    def get_num(em, t):
        mem_key = (t,)
        if mem_key not in MinFuncMT.__made_names:
            num = len(MinFuncMT.__made_names)
            it_type = t.get_attr_types()['__iter__'][0].get_instantiated().rtn_type
            elt_type = it_type.get_attr_types()['next'][0].get_instantiated().rtn_type
            template = eval_ctemplate("min", em, {
                't':t,
                'it':it_type,
                'et':elt_type,
                'num':num,
                })
            em.c_head.write(template)
            MinFuncMT.__made_names[mem_key] = num

            em.llvm_head.write("declare %s @min%s(%s)\n" % (elt_type.llvm_type(), num, t.llvm_type()))
            em.llvm_head.write("declare %s @max%s(%s)\n" % (elt_type.llvm_type(), num, t.llvm_type()))

        return MinFuncMT.__made_names[mem_key]
MinFunc = MinFuncMT("min")
MaxFunc = MinFuncMT("max")

class UnboxedFunctionMT(MT):
    def __init__(self, em, closure_type, arg_types, rtn_type, ndefaults=0):
        super(UnboxedFunctionMT, self).__init__()
        self.closure_type = closure_type
        self.arg_types = [a.get_instantiated() for a in arg_types]
        self.rtn_type = rtn_type.get_instantiated()
        self.ndefaults = ndefaults

    def _initialize(self, em, stage):
        self.get_instantiated().initialize(em, stage)

    def dup(self, v, dup_cache):
        func_name, defaults, closure = v
        assert len(defaults) == self.ndefaults
        return func_name, [d.dup(dup_cache) for d in defaults], closure.dup(dup_cache) if closure else None

    def free(self, em, v):
        func_name, defaults, closure = v
        assert len(defaults) == self.ndefaults
        for d in defaults:
            d.decvref(em)
        return None

    def _argtype_str(self):
        return ", ".join(([self.closure_type.llvm_type()] if self.closure_type else []) + [a.llvm_type() for a in self.arg_types])

    def llvm_type(self):
        ret_type = self.rtn_type.llvm_type() if self.rtn_type is not None_ else "void"
        return "%s (%s)*" % (ret_type, self._argtype_str())

    def can_call(self, args):
        # TODO should pass in defaults_types to this type
        if len(args) != len(self.arg_types):
            return False
        for i in xrange(len(args)):
            if not args[i].can_convert_to(self.arg_types[i]):
                return False
        return True

    def call(self, em, v, args, expected_type=None):
        func_name, defaults, closure = v
        assert len(defaults) == self.ndefaults

        assert len(defaults) <= len(self.arg_types)
        for d in defaults:
            assert isinstance(d, Variable)

        assert len(self.arg_types) - len(defaults) <= len(args) <= len(self.arg_types), (args, self.arg_types, defaults)

        args = list(args) # we're going to modify it
        for n in xrange(len(args), len(self.arg_types)):
            arg = defaults[n - len(self.arg_types)]
            assert isinstance(arg, Variable)
            arg.incvref(em)
            args.append(arg)
            # args.append(Variable(Int, arg, 1, False))

        assert len(self.arg_types) == len(args)
        for i in xrange(len(args)):
            args[i] = args[i].convert_to(em, self.arg_types[i])

        if [_v.t for _v in args] != self.arg_types:
            raise UserTypeError([_v.t for _v in args], self.arg_types)

        prologue = ""
        if self.rtn_type is not None_:
            name = "%" + em.mkname()
            prologue = "%s = " % name

        args_plus_closure = ([closure] + args) if closure else args
        rtn_type = self.rtn_type.llvm_type() if self.rtn_type is not None_ else "void"
        em.pl("%scall %s (%s)* %s(%s)" % (prologue, rtn_type, self._argtype_str(), func_name, ", ".join("%s %s" % (_v.t.llvm_type(), _v.v) for _v in args_plus_closure)))

        if self.rtn_type is not None_:
            assert prologue.startswith("%")
            prologue = "%s " % self.rtn_type.c_type() + prologue[1:]
        if func_name.startswith('%'):
            em.pc("#error unimplemented 20")
        else:
            def local(n):
                n = str(n)
                if n.startswith('%'):
                    return n[1:]
                return n
            em.pc("%s %s(%s);" % (prologue, raw_func_name(func_name), ", ".join(local(_v.v) for _v in args_plus_closure)))

        for _v in args:
            _v.decvref(em)

        if self.rtn_type is not None_:
            return Variable(self.rtn_type, name, 1, True)
        else:
            return Variable(self.rtn_type, "null", 1, False)

    def get_instantiated(self):
        return CallableMT.make_callable(self.arg_types, self.ndefaults, self.rtn_type)

    def _can_convert_to(self, t):
        if not isinstance(t, CallableMT):
            return False
        return t.arg_types == self.arg_types and t.rtn_type == self.rtn_type

    def _convert_to(self, em, var, t):
        (func_name, defaults, closure) = var.v
        assert len(defaults) == self.ndefaults
        if isinstance(t, CallableMT):
            if t.arg_types == self.arg_types and t.rtn_type == self.rtn_type:
                assert (closure is None) == (self.closure_type is None)

                assert t.ndefaults <= len(defaults)
                defaults = defaults[:t.ndefaults]

                r = SimpleFunction.make(em, self.arg_types, defaults, self.rtn_type, closure, func_name)
                var.decvref(em)
                return r

            raise UserTypeError((self.arg_types, self.rtn_type, var.v[1], t.arg_types, t.rtn_type))

        raise UserTypeError(t)

class PolymorphicFunctionMT(MT):
    def __init__(self, func_types):
        super(PolymorphicFunctionMT, self).__init__()
        assert isinstance(func_types, (list, tuple))
        assert len(func_types) > 0
        self.func_types = func_types
        self.initialized = ("attrs", "write")

    def dup(self, v, dup_cache):
        funcs, = v
        return ([f.dup(dup_cache) for f in funcs],)

    def free(self, em, v):
        funcs, = v
        assert len(funcs) == len(self.func_types)
        for i in xrange(len(funcs)):
            assert funcs[i].t is self.func_types[i]
        for f in funcs:
            f.decvref(em)

    def call(self, em, v, args, expected_type=None):
        funcs, = v
        assert len(funcs) == len(self.func_types)
        for i in xrange(len(funcs)):
            assert funcs[i].t is self.func_types[i]

        for f in funcs:
            if f.t.can_call([a.t for a in args]):
                f.incvref(em)
                return f.call(em, args)

        raise UserTypeError("Can't call with args %s" % (args,))

    def convert_to(self, em, var, t):
        funcs, = var.v
        assert len(funcs) == len(self.func_types)
        for i in xrange(len(funcs)):
            assert funcs[i].t is self.func_types[i]

        for f in funcs:
            if f.t.can_convert_to(t):
                f.incvref(em)
                var.decvref(em)
                return f.convert_to(em, t)
        raise UserTypeError()

    def get_instantiated(self):
        # TODO this just heuristically picks the first function, but it'd be nice to be able to pick
        # the "right" one (is that the same thing as supporting rank-2 polymorphism?)
        return self.func_types[0].get_instantiated()

    @staticmethod
    def make(funcs):
        for f in funcs:
            assert isinstance(f, Variable)
            # This isn't completely necessary but I haven't thought through how it would work
            assert isinstance(f.t, (UnboxedFunctionMT, _SpecialFuncMT))

        t = PolymorphicFunctionMT([f.t for f in funcs])
        return Variable(t, (funcs,), 1, False)

class UnboxedInstanceMethod(MT):
    def __init__(self, obj_type, func_type):
        super(UnboxedInstanceMethod, self).__init__()
        assert isinstance(obj_type, MT)
        assert isinstance(func_type, MT)
        self._obj_type = obj_type
        self._func_type = func_type

    def _initialize(self, em, stage):
        try:
            self.get_instantiated().initialize(em, stage)
        except CantInstantiateException:
            pass

    @staticmethod
    def make(em, o, f):
        assert is_emitter(em)
        assert isinstance(o, Variable)
        assert isinstance(f, Variable)
        assert isinstance(f.t, (UnboxedFunctionMT, PolymorphicFunctionMT, _SpecialFuncMT)), f.t

        o.incvref(em)
        f.incvref(em)
        t = UnboxedInstanceMethod(o.t, f.t)
        t.initialize(em, "write")
        return Variable(t, (o, f), 1, False)

    def dup(self, v, dup_cache):
        (o, f) = v
        return o.dup(dup_cache), f.dup(dup_cache)

    def can_call(self, args):
        return self._func_type.can_call([self._obj_type] + args)

    def call(self, em, v, args, expected_type=None):
        (o, f) = v
        o.incvref(em) # being passed into the function,
        f.incvref(em) # which consumes one vref
        return f.call(em, [o] + args)

    def free(self, em, v):
        (o, f) = v
        # em.pl("; UIM.decref")
        o.decvref(em)
        f.decvref(em)
        # em.pl("; UIM.decref, done")

    def get_instantiated(self):
        if isinstance(self._func_type, UnboxedFunctionMT):
            return CallableMT.make_callable(self._func_type.arg_types[1:], 0, self._func_type.rtn_type)
        elif isinstance(self._func_type, CallableMT):
            return CallableMT.make_callable(self._func_type.arg_types[1:], 0, self._func_type.rtn_type)
        else:
            raise CantInstantiateException(self._func_type)

    def _can_convert_to(self, t):
        return self.get_instantiated().can_convert_to(t)

    def _convert_to(self, em, var, t):
        if isinstance(t, CallableMT):
            assert isinstance(self._func_type, UnboxedFunctionMT), "unimplemented"
            if t.arg_types == self._func_type.arg_types[1:] and t.rtn_type == self._func_type.rtn_type:
                assert t == self.get_instantiated()
                (o, f) = var.v

                o.incvref(em)
                if o.t != o.t.get_instantiated():
                    o = o.convert_to(em, o.t.get_instantiated())

                r = InstanceMethod.make(em, o, f)
                o.decvref(em, "raised for UIM->IM")
                var.decvref(em, "UIM raised to IM")
                return r

        return var.convert_to(em, self.get_instantiated()).convert_to(em, t)

class InstanceMethod(object):
    __made_funcs = {}

    def __init__(self):
        assert 0

    @staticmethod
    def make(em, o, f):
        assert o.t is o.t.get_instantiated()
        assert isinstance(f.t, UnboxedFunctionMT)

        name = InstanceMethod.get_name(em, o.t, f.t)
        args = f.t.arg_types[1:]
        ret = f.t.rtn_type

        func = CallableMT.make_callable(args, 0, ret)
        func.initialize(em, "write")
        r = "%" + em.mkname()


        o = o.split(em)
        if not isinstance(f.t, UnboxedFunctionMT):
            f = f.split(em)
            raise Exception("test this")
        em.pl("%s = call %s (%s, %s)* @%s_ctor(%s %s, %s %s)" % (r, func.llvm_type(), o.t.llvm_type(), f.t.llvm_type(), name, o.t.llvm_type(), o.v, f.t.llvm_type(), f.v[0]))
        em.pc("#error unimplemented 7")

        return Variable(func, r, 1, True)

    @staticmethod
    def get_name(em, ot, ft):
        assert isinstance(ot, MT)
        assert isinstance(ft, UnboxedFunctionMT)

        assert ot is ot.get_instantiated()
        mem_key = (ot, tuple(ft.arg_types), ft.rtn_type)

        ft.initialize(em, "write")
        ot.initialize(em, "attrs")

        if mem_key not in InstanceMethod.__made_funcs:
            name = "im_%d" % (len(InstanceMethod.__made_funcs),)
            InstanceMethod.__made_funcs[mem_key] = name

            bound_args = ft.arg_types[1:]
            ret = ft.rtn_type
            ret_type = ret.llvm_type()

            callable_mt = CallableMT.make_callable(bound_args, 0, ret)
            callable_mt.initialize(em, "write")
            callable_type = callable_mt.llvm_type()

            o_decref = ot.decref_llvm(em, "%o") or ""

            real_call_type = "%s (%s)*" % (ret_type, ", ".join(["%" + name + "*"] + [a.llvm_type() for a in bound_args]))
            call_type = "%s (%s)*" % (ret_type, ", ".join([callable_type] + [a.llvm_type() for a in bound_args]))
            func_type = ft.llvm_type()
            arg_string = ", ".join(["%s %%o" % ot.llvm_type()] + ["%s %%v%d" % (a.llvm_type(), i) for i, a in enumerate(bound_args)])
            def_args = ", ".join(["%%%s* %%self" % name] + ["%s %%v%d" % (a.llvm_type(), i) for i, a in enumerate(bound_args)])
            evaluated = eval_template("im", em, {
                'n':name,
                'r':ret_type,
                'ft':ft,
                'ot':ot,
                'bound_args':bound_args,
                "callable_type":callable_type,
                "call_type":call_type,
                "real_call_type":real_call_type,
                "arg_string":arg_string,
                "func_type":func_type,
                "def_args":def_args,
                "obj_type":ot.llvm_type(),
                "f_decref":"", # Only supporting UnboxedFunctionMT for now
                "o_decref":o_decref,
                "vtable_t":callable_type[:-1] + "_vtable",
                "alloc_name":em.get_str_ptr(name),
                })
            evaluated = convert_none_to_void_ll(evaluated)
            em.llvm_tail.write(evaluated)

        return InstanceMethod.__made_funcs[mem_key]

class CallableMT(MT):
    __made_funcs = {}

    def __init__(self, args, ndefaults, ret, name):
        super(CallableMT, self).__init__()

        for a in args:
            assert isinstance(a, MT)
        assert isinstance(ret, MT)
        assert isinstance(ndefaults, (int, long))

        assert ret.get_instantiated() is ret
        for a in args:
            assert a.get_instantiated() is a, (a, a.get_instantiated())

        self.arg_types = args
        self.ndefaults = ndefaults
        self.rtn_type = ret
        self.name = name

    def _initialize(self, em, stage):
        if stage == "attrs":
            self.class_methods = {
                "__repr__": Variable(UnboxedFunctionMT(em, None, [self], Str), ("@%s_repr" % self.name, [], None), 1, False),
                "__eq__": Variable(UnboxedFunctionMT(em, None, [self, self], Bool), ("@%s_eq" % self.name, [], None), 1, False),
                "__nonzero__": Variable(UnboxedFunctionMT(em, None, [self], Bool), ("@%s_eq" % self.name, [], None), 1, False),
                "__decref__": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_decref" % self.name, [], None), 1, False),
                "__incref__": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_incref" % self.name, [], None), 1, False),
            }
            self.class_methods["__str__"] = self.class_methods["__repr__"]
        elif stage == "write":
            for a in self.arg_types:
                a.initialize(em, "attrs")
            self.rtn_type.initialize(em, "attrs")
            ret_type = self.rtn_type.llvm_type()

            arg_type_strings = []
            arg_strings = []
            call_types = []
            for i in xrange(len(self.arg_types) - self.ndefaults, len(self.arg_types) + 1):
                arg_type_string = "%s" % (", ".join(["%" + self.name + "*"] + [a.llvm_type() for a in self.arg_types[:i]]))
                arg_string = ", ".join(["%%%s* %%f" % self.name] + ["%s %%v%d" % (a.llvm_type(), i) for i, a in enumerate(self.arg_types[:i])])
                call_type = "%s (%s)" % (ret_type, arg_type_string)
                arg_type_strings.append(arg_type_string)
                arg_strings.append(arg_string)
                call_types.append(call_type)
                del arg_type_string, arg_string, call_type

            evaluated = eval_template("callable", em, {
                'n':self.name,
                'call_types': ", ".join(["%s*" % ct for ct in call_types]),
                "alloc_name":em.get_str_ptr(self.name),
            })
            em.llvm_tail.write(convert_none_to_void_ll(evaluated))

            for i in xrange(self.ndefaults + 1):
                this_nargs = len(self.arg_types) - self.ndefaults + i
                evaluated = eval_template("callable_call", em, {
                    'CHECK_NONE':'',
                    'n':self.name,
                    'this_nargs': this_nargs,
                    'call_ptr_idx': i + 1,
                    'r':ret_type,
                    "this_call_type":call_types[i],
                    "this_arg_string":arg_strings[i],
                })
                evaluated = convert_none_to_void_ll(evaluated)
                em.llvm_tail.write(evaluated)


            ctemplate = eval_ctemplate("callable", em, {
                'n':self.name,
                'nargs': len(self.arg_types),
                'ndefaults': self.ndefaults,
                })
            em.c_head.write(ctemplate)
        else:
            raise Exception(stage)

    def llvm_type(self):
        return "%%%s*" % (self.name,)

    def can_call(self, args):
        if not (len(self.arg_types) - self.ndefaults <= len(args) <= len(self.arg_types)):
            return False
        for i in xrange(len(args)):
            if not args[i].can_convert_to(self.arg_types[i]):
                return False
        return True

    def call(self, em, v, args, expected_type=None):
        assert len(self.arg_types) - self.ndefaults <= len(args) <= len(self.arg_types), (args, self.arg_types, self.ndefaults)
        args = list(args)
        for i in xrange(len(args)):
            args[i] = args[i].convert_to(em, self.arg_types[i])
        assert [_v.t for _v in args] == self.arg_types[:len(args)], ([_v.t for _v in args], self.arg_types)

        prologue = ""
        if self.rtn_type is not None_:
            rtn_name = "%" + em.mkname()
            prologue = "%s = " % rtn_name
            ret_type = self.rtn_type.llvm_type()
            # TODO duplication
        else:
            ret_type = "void"
        type_string = "%s (%s)" % (ret_type, ", ".join([self.llvm_type()] + [a.llvm_type() for a in self.arg_types[:len(args)]]))
        arg_string = ", ".join(["%s %s" % (self.llvm_type(), v)] + ["%s %s" % (a.t.llvm_type(), a.v) for a in args])
        em.pl("%scall %s* @%s_call%d(%s)" % (prologue, type_string, self.name, len(args), arg_string))
        em.pc("#error unimplemented 8")

        for _v in args:
            _v.decvref(em)

        if self.rtn_type is not None_:
            return Variable(self.rtn_type, rtn_name, 1, True)
        else:
            return Variable(self.rtn_type, "null", 1, False)

    def _can_convert_to(self, t):
        if not isinstance(t, CallableMT):
            return False
        if t.arg_types != self.arg_types:
            return False
        if not self.rtn_type.can_convert_to(t.rtn_type):
            return False
        return True

    @staticmethod
    def make_callable(args, ndefaults, ret):
        for a in args:
            assert isinstance(a, MT)
        assert isinstance(ret, MT)
        mem_key = (tuple(args), ndefaults, ret)
        if mem_key not in CallableMT.__made_funcs:
            name = "c_%d" % (len(CallableMT.__made_funcs),)
            CallableMT.__made_funcs[mem_key] = CallableMT(args, ndefaults, ret, name)

        return CallableMT.__made_funcs[mem_key]

    def _convert_to(self, em, var, t):
        assert isinstance(t, CallableMT)
        if t.ndefaults <= self.ndefaults and len(t.arg_types) - t.ndefaults == len(self.arg_types) - self.ndefaults:
            if self.arg_types[:len(t.arg_types)] == t.arg_types and self.rtn_type == t.rtn_type:
                name = "%" + em.mkname()
                em.pl("%s = bitcast %s %s to %s" % (name, self.llvm_type(), var.v, t.llvm_type()))
                rtn = Variable(t, name, 1, True)
                rtn.incvref(em)
                rtn.getattr(em, "__incref__").call(em, [])
                var.decvref(em)
                return rtn
        return _Reboxer.make(em, var, t)

    def vtable_type(self):
        return self.llvm_type()[:-1] + "_vtable"

class _Reboxer(object):
    __made_reboxers = {}

    __init__ = None

    @staticmethod
    def make(em, var, new_type):
        assert is_emitter(em)
        assert isinstance(var.t, CallableMT)
        assert isinstance(new_type, CallableMT)

        key = (var.t, new_type)
        if key not in _Reboxer.__made_reboxers:
            name = em.mkname(prefix="reboxer_")
            call_type = UnboxedFunctionMT(em, None, [new_type] + new_type.arg_types, new_type.rtn_type)

            _Reboxer.__made_reboxers[key] = name

            evaluated = eval_template("reboxer", em, {
                'n':name,
                'orig_type':var.t,
                'new_type':new_type,
                'call_type':call_type,
                })
            em.llvm_tail.write(evaluated)

        name = _Reboxer.__made_reboxers[key]
        em.pc("#error unimplemented 9")

        r = "%" + em.mkname()
        em.pl("%s = call %s @%s_ctor(%s %s)" % (r, new_type.llvm_type(), name, var.t.llvm_type(), var.v))
        var.decvref(em)
        return Variable(new_type, r, 1, True)

class SimpleFunction(object):
    __made_funcs = {}

    __init__ = None

    @staticmethod
    def make(em, arg_types, defaults, ret_type, closure, func_name):
        ndefaults = len(defaults)
        for i in xrange(ndefaults):
            arg_idx = len(arg_types) - ndefaults + i
            defaults[i].incvref(em)
            defaults[i] = defaults[i].convert_to(em, arg_types[arg_idx])

        callable_type = CallableMT.make_callable(arg_types, ndefaults, ret_type)
        callable_type.initialize(em, "write")
        unboxed = UnboxedFunctionMT(em, closure.t if closure else None, arg_types, ret_type)
        func_type = unboxed.llvm_type()
        default_types = ''.join(", %s" % (d.t.llvm_type(),) for d in defaults)
        mem_key = (tuple(arg_types), ndefaults, ret_type, closure.t if closure else None)
        closure_def_type = ", %s" % closure.t.llvm_type() if closure else ""

        if mem_key not in SimpleFunction.__made_funcs:
            name = "f_%d" % (len(SimpleFunction.__made_funcs),)
            vtable_t = callable_type.llvm_type()[:-1] + "_vtable"

            ret_name = ret_type.llvm_type() if ret_type is not None_ else "void"

            call_types = []
            for i in xrange(len(arg_types) - ndefaults, len(arg_types) + 1):
                arg_type_string = "%s" % (", ".join([callable_type.llvm_type()] + [a.llvm_type() for a in arg_types[:i]]))
                call_type = "%s (%s)" % (ret_name, arg_type_string)
                call_types.append(call_type)
                del arg_type_string, call_type

            defaults_argstr = ''.join(", %s %%default%d" % (d.t.llvm_type(), i) for (i, d) in enumerate(defaults))
            call_funcs = ", ".join("%s* @%s_call%d" % (call_types[i], name, len(arg_types) - ndefaults + i) for i in xrange(ndefaults + 1))
            defaults_start = 4 if closure else 3
            store_defaults = "\n    ".join("%%dptr%d = getelementptr inbounds %%%s* %%made, i32 0, i32 %d\n    store %s %%default%d, %s* %%dptr%d\n    %s" % (i, name, i + defaults_start, defaults[i].t.llvm_type(), i, defaults[i].t.llvm_type(), i, defaults[i].t.incref_llvm(em, "%%default%d" % (i,))) for i in xrange(len(defaults)))
            decref_defaults = "\n    ".join("%%dptr%d = getelementptr inbounds %%%s* %%self, i32 0, i32 %d\n    %%default%d = load %s* %%dptr%d\n    %s" % (i, name, i + defaults_start, i, defaults[i].t.llvm_type(), i, defaults[i].t.decref_llvm(em, "%%default%d" % (i,))) for i in xrange(len(defaults)))

            evaluated = eval_template("function", em, {
                    'n': name,
                    'vtable_t': vtable_t,
                    'callable_type': callable_type.llvm_type(),
                    'call_types': ', '.join(call_types),
                    'closure_type': closure.t.llvm_type() if closure else "X",
                    'closure_def_type': closure_def_type,
                    'default_types': default_types,
                    'func_type': func_type,
                    'IFCLOSURE': '' if closure else ';',
                    'defaults_argstr': defaults_argstr,
                    'closure_incref': closure.t.incref_llvm(em, "%closure") if closure else 'closure_incref',
                    'closure_decref': closure.t.decref_llvm(em, "%closure") if closure else 'closure_decref',
                    'call_funcs': call_funcs,
                    'store_defaults': store_defaults,
                    'decref_defaults': decref_defaults,
                    'alloc_name': em.get_str_ptr(name),
                })
            em.llvm_tail.write(evaluated)

            for i in xrange(ndefaults + 1):
                this_nargs = len(arg_types) - ndefaults + i
                this_defaults = len(arg_types) - this_nargs
                call_args = ", ".join(["%s %%self" % callable_type.llvm_type()] + ["%s %%v%d" % (a.llvm_type(), i) for i, a in enumerate(arg_types[:this_nargs])])
                func_args = ", ".join(["%s %%v%d" % (a.llvm_type(), i) for i, a in enumerate(arg_types[:this_nargs])])
                if func_args:
                    if closure:
                        func_args = ", " + func_args
                    if this_defaults:
                        func_args += ", "
                elif closure and this_defaults:
                    func_args = ","
                load_defaults = "\n    ".join("%%dptr%d = getelementptr inbounds %%%s* %%f, i32 0, i32 %d\n    %%default%d = load %s* %%dptr%d\n    ;%s" % (i, name, i + defaults_start, i, defaults[i].t.llvm_type(), i, defaults[i].t.incref_llvm(em, "%%default%d" % (i,))) for i in xrange(ndefaults - this_defaults, ndefaults))
                decref_defaults = "\n    ".join(";%s" % (defaults[i].t.decref_llvm(em, "%%default%d" % (i,)), ) for i in xrange(ndefaults - this_defaults, ndefaults))
                defaults_argstr = ', '.join("%s %%default%d" % (defaults[i].t.llvm_type(), i) for i in xrange(ndefaults - this_defaults, ndefaults))
                evaluated = eval_template("function_call", em, {
                    'n':name,
                    'this_nargs': this_nargs,
                    'r':ret_name,
                    'func_type': func_type,
                    "call_args": call_args,
                    "func_args": func_args,
                    'closure_type': closure.t.llvm_type() if closure else "X",
                    'IFCLOSURE': '' if closure else ';',
                    "load_defaults": load_defaults,
                    "decref_defaults": decref_defaults,
                    "defaults_args": defaults_argstr,
                    'callable_type': callable_type.llvm_type(),
                })
                em.llvm_tail.write(convert_none_to_void_ll(evaluated))

            SimpleFunction.__made_funcs[mem_key] = name

        name = SimpleFunction.__made_funcs[mem_key]
        r = '%' + em.mkname()
        # TODO upconvert here
        closure_args = ", %s %s" % (closure.t.llvm_type(), closure.v) if closure else ""
        defaults_args = "".join(", %s %s" % (defaults[i].t.llvm_type(), defaults[i].v) for i in xrange(ndefaults))
        em.pl("%s = call %s (%s %s %s)* @%s_ctor(%s %s %s %s)" % (r, callable_type.llvm_type(), func_type, closure_def_type, default_types, name, func_type, func_name, closure_args, defaults_args))
        em.pc("#error unimplemented 10")
        for i in xrange(ndefaults):
            defaults[i].decvref(em)
        return Variable(callable_type, r, 1, True)

class UnboxedTupleMT(MT):
    def __init__(self, elt_types):
        super(UnboxedTupleMT, self).__init__()
        for e in elt_types:
            assert isinstance(e, MT)
        self.elt_types = tuple(elt_types)
        self.initialized = ("attrs", "write")

    def dup(self, v, dup_cache):
        return tuple([e.dup(dup_cache) for e in v])

    def getattr(self, em, v, attr, clsonly):
        if attr == "__getitem__":
            return UnboxedInstanceMethod.make(em, v, Variable(UnboxedTupleMT.Getitem, (), 1, False))
        return self.get_instantiated().getattr(em, v, attr, clsonly)

    def free(self, em, v):
        assert isinstance(v, tuple)
        for e in v:
            e.decvref(em)

    class GetitemMT(_SpecialFuncMT):
        def call(self, em, v, args, expected_type=None):
            assert len(args) == 2
            assert isinstance(args[0].t, UnboxedTupleMT)
            assert args[1].t is Int
            idx = args[1].v
            assert isinstance(idx, int)
            assert 0 <= idx < len(args[0].t.elt_types)

            assert isinstance(args[0].v, tuple)
            assert len(args[0].t.elt_types) == len(args[0].v)

            r = args[0].v[idx]
            args[0].decvref(em)
            args[1].decvref(em)
            r.incvref(em)
            return r
    Getitem = GetitemMT()

    def get_instantiated(self):
        return TupleMT.make_tuple([e.get_instantiated() for e in self.elt_types])

    def _can_convert_to(self, t):
        if not isinstance(t, TupleMT) or len(t.elt_types) != len(self.elt_types):
            return False

        for i in xrange(len(self.elt_types)):
            if not self.elt_types[i].can_convert_to(t.elt_types[i]):
                return False
        return True

    def _convert_to(self, em, var, t):
        if isinstance(t, TupleMT) and len(t.elt_types) == len(self.elt_types):
            elts = []
            for i, e in enumerate(var.v):
                e.incvref(em)
                elts.append(e.convert_to(em, t.elt_types[i]))
            r = t.alloc(em, elts)
            for e in elts:
                e.decvref(em)
            var.decvref(em)
            return r

        var.incvref(em)
        return var.convert_to(em, self.get_instantiated()).convert_to(em, t)

class TupleMT(MT):
    def __init__(self, name, elt_types):
        super(TupleMT, self).__init__()
        for e in elt_types:
            assert isinstance(e, MT)
            assert e == e.get_instantiated()
        self.elt_types = tuple(elt_types)
        self.name = name

    def _initialize(self, em, stage):
        if stage == "attrs":
            for e in self.elt_types:
                e.initialize(em, "attrs")

            self.class_methods = {
                "__getitem__": Variable(TupleMT.Getitem, (), 1, False),
                "__repr__": Variable(UnboxedFunctionMT(em, None, [self], Str), ("@%s_repr" % (self.name,), [], None), 1, False),
                "__len__": Variable(UnboxedFunctionMT(em, None, [self], Int), ("@%s_len" % (self.name,), [], None), 1, False),
                "__eq__": Variable(UnboxedFunctionMT(em, None, [self, self], Bool), ("@%s_eq" % (self.name,), [], None), 1, False),
                "__lt__": Variable(UnboxedFunctionMT(em, None, [self, self], Bool), ("@%s_lt" % (self.name,), [], None), 1, False),
                "__incref__": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_incref" % (self.name,), [], None), 1, False),
                "__decref__": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_decref" % (self.name,), [], None), 1, False),
            }
            self.class_methods["__str__"] = self.class_methods["__repr__"]
            self.typeobj_name = "@%s_typeobj" % self.name

            if not all(e.hasattr("__eq__") for e in self.elt_types):
                del self.class_methods["__eq__"]
                del self.class_methods["__lt__"]
            elif not all(e.hasattr("__lt__") for e in self.elt_types):
                del self.class_methods["__lt__"]
        elif stage == "write":
            type_str = ", ".join(["i64"] + [e.llvm_type() for e in self.elt_types])
            arg_str = ", ".join(["%s %%arg%d" % (e.llvm_type(), i) for i, e in enumerate(self.elt_types)])
            carg_str = ", ".join(["%s" % (e.c_type(),) for i, e in enumerate(self.elt_types)])

            assign_all = ""
            for i in xrange(len(self.elt_types)):
                e = self.elt_types[i]
                assign_all += "%%ptr%d = getelementptr inbounds %s %s, i64 0, i32 %d\n" % (i, self.llvm_type(), "%rtn", i + 1)
                inc = self.elt_types[i].incref_llvm(em, "%%arg%d" % i)
                if inc:
                    assign_all += inc + '\n'
                assign_all += "store %s %%arg%d, %s* %%ptr%d\n" % (e.llvm_type(), i, e.llvm_type(), i)
            assign_all = assign_all.replace('\n', '\n    ')

            decref_all = ""
            for i in xrange(len(self.elt_types)):
                e = self.elt_types[i]
                d = e.decref_llvm(em, "%%elt%d" % (i,))
                if not d:
                    continue
                decref_all += "%%ptr%d = getelementptr inbounds %s %%self, i64 0, i32 %d\n" % (i, self.llvm_type(), i + 1)
                decref_all += "%%elt%d = load %s* %%ptr%d\n" % (i, e.llvm_type(), i)
                decref_all += d + '\n'
            decref_all = decref_all.replace('\n', '\n    ')

            add_all_str = ""
            for i in xrange(len(self.elt_types)):
                e = self.elt_types[i]
                assert e == e.get_instantiated()
                if i > 0:
                    add_all_str += "call void @list_string_append(%%list_string* %%list, %%string* %%commaspace)\n" % ()
                add_all_str += "%%ptr%d = getelementptr inbounds %s %%self, i64 0, i32 %d\n" % (i, self.llvm_type(), i + 1)
                add_all_str += "%%elt%d = load %s* %%ptr%d\n" % (i, e.llvm_type(), i)

                emitter = CodeEmitter(em)
                elt_repr_func = Variable(e, "%%elt%d" % i, 1, False).getattr(emitter, "__repr__", clsonly=True)
                repr_r = elt_repr_func.call(emitter, [])
                assert repr_r.t is Str

                add_all_str += emitter.get_llvm() + '\n'
                add_all_str += "call void @list_string_append(%%list_string* %%list, %%string* %s)\n" % (repr_r.v,)
                add_all_str += "call void @str_decref(%%string* %s)\n" % (repr_r.v,)
            if len(self.elt_types) == 1:
                add_all_str += "call void @list_string_append(%%list_string* %%list, %%string* %%comma)\n" % ()
            add_all_str = add_all_str.replace('\n', '\n    ')


            em.llvm_tail.write(eval_template("tuple", em, {
                'n':self.name,
                'type_str':type_str,
                'arg_str':arg_str,
                'assign_all':assign_all,
                'decref_all':decref_all,
                'add_all_str':add_all_str,
                'DEBUG_CHECKS':' ' if DEBUG_CHECKS else ';',
                'NO_DEBUG_CHECKS':' ' if not DEBUG_CHECKS else ';',
                'len':len(self.elt_types),
                'alloc_name':em.get_str_ptr(self.name),
                }))

            ctemplate = eval_ctemplate("tuple", em, {
                't':self,
                'n':self.name,
                'args':carg_str,
                })
            em.c_head.write(ctemplate)
        else:
            raise Exception(stage)

    def llvm_type(self):
        return "%%%s*" % self.name

    def get_ctor_name(self):
        return "@%s_ctor" % (self.name,)

    def alloc(self, em, elts):
        assert self.elt_types == tuple([e.t for e in elts]), (self.elt_types, tuple([e.t for e in elts]))
        name = '%' + em.mkname()
        em.pl("%s = call %s %s(%s)" % (name, self.llvm_type(), self.get_ctor_name(), ", ".join(["%s %s" % (v.t.llvm_type(), v.v) for v in elts])))
        em.pc("#error unimplemented 11")
        return Variable(self, name, 1, True)

    def _can_convert_to(self, t):
        return False

    # TODO merge this with the Unboxed version
    class GetitemMT(_SpecialFuncMT):
        def call(self, em, v, args, expected_type=None):
            assert len(args) == 2
            assert isinstance(args[0].t, TupleMT)
            assert args[1].t is Int
            idx = args[1].v
            assert isinstance(idx, int)
            assert 0 <= idx < len(args[0].t.elt_types)

            assert isinstance(args[0].v, str)

            t = args[0].t.elt_types[idx]
            pl = '%' + em.mkname()
            r = '%' + em.mkname()
            em.pl("%s = getelementptr inbounds %s %s, i64 0, i32 %d" % (pl, args[0].t.llvm_type(), args[0].v, idx + 1))
            em.pl("%s = load %s* %s" % (r, t.llvm_type(), pl))
            inc = t.incref_llvm(em, r)
            if inc:
                em.pl(inc + " ; tuple getitem")
            em.pc("#error unimplemented 12")

            args[0].decvref(em)
            args[1].decvref(em)
            return Variable(t, r, 1, True)

    Getitem = GetitemMT()

    __tuples = {}
    @staticmethod
    def make_tuple(elt_types):
        elt_types = tuple(elt_types)
        for e in elt_types:
            assert isinstance(e, MT)

        if elt_types not in TupleMT.__tuples:
            name = "_".join(["tuple%d" % len(elt_types)] + [e.llvm_type().replace('%', '').replace('*', '') for e in elt_types])
            if len(name) > 40:
                name = "tuple_%d" % len(TupleMT.__tuples)
            TupleMT.__tuples[elt_types] = TupleMT(name, elt_types)
        t = TupleMT.__tuples[elt_types]
        return t

class ListMT(MT):
    def __init__(self, elt_type):
        super(ListMT, self).__init__()
        assert isinstance(elt_type, MT)
        self.elt_type = elt_type
        self.name = ListMT.get_name(elt_type)

        self.iter_type = ListMT.ListIteratorMT(self)

    def _initialize(self, em, stage):
        if stage == "attrs":
            self.elt_type.initialize(em, "attrs")
            self.class_methods = {
                "__add__": Variable(UnboxedFunctionMT(em, None, [self, self], self), ("@%s_add" % (self.name,), [], None), 1, False),
                "append": Variable(UnboxedFunctionMT(em, None, [self, self.elt_type], None_), ("@%s_append" % (self.name,), [], None), 1, False),
                "__contains__": Variable(UnboxedFunctionMT(em, None, [self, self.elt_type], Bool), ("@%s_contains" % (self.name,), [], None), 1, False),
                "__decref__": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_decref" % (self.name,), [], None), 1, False),
                "__eq__": Variable(UnboxedFunctionMT(em, None, [self, self], Bool), ("@%s_eq" % (self.name,), [], None), 1, False),
                "extend": Variable(UnboxedFunctionMT(em, None, [self, self], None_), ("@%s_extend" % (self.name,), [], None), 1, False),
                "__getitem__": PolymorphicFunctionMT.make([
                        Variable(UnboxedFunctionMT(em, None, [self, Int], self.elt_type), ("@%s_getitem" % (self.name,), [], None), 1, False),
                        Variable(UnboxedFunctionMT(em, None, [self, Slice], self), ("@%s_getitem_slice" % (self.name,), [], None), 1, False)]),
                "__iadd__": Variable(UnboxedFunctionMT(em, None, [self, self], self), ("@%s_iadd" % (self.name,), [], None), 1, False),
                "__incref__": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_incref" % (self.name,), [], None), 1, False),
                "insert": Variable(UnboxedFunctionMT(em, None, [self, Int, self.elt_type], None_), ("@%s_insert" % (self.name,), [], None), 1, False),
                "__iter__": Variable(UnboxedFunctionMT(em, None, [self], self.iter_type), ("@%s_iter" % (self.name,), [], None), 1, False),
                "__len__": Variable(UnboxedFunctionMT(em, None, [self], Int), ("@%s_len" % (self.name,), [], None), 1, False),
                "__mul__": Variable(UnboxedFunctionMT(em, None, [self, Int], self), ("@%s_mul" % (self.name,), [], None), 1, False),
                "__nonzero__": Variable(UnboxedFunctionMT(em, None, [self], Bool), ("@%s_nonzero" % (self.name,), [], None), 1, False),
                "__nrefs__": Variable(UnboxedFunctionMT(em, None, [self], Int), ("@%s_nrefs" % (self.name,), [], None), 1, False),
                "pop": Variable(UnboxedFunctionMT(em, None, [self, Int], self.elt_type), ("@%s_pop" % (self.name,), [], None), 1, False),
                "__repr__": Variable(UnboxedFunctionMT(em, None, [self], Str), ("@%s_repr" % (self.name,), [], None), 1, False),
                "reverse": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_reverse" % (self.name,), [], None), 1, False),
                "sort": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_sort" % (self.name,), [], None), 1, False),
                "__setitem__": PolymorphicFunctionMT.make([
                        Variable(UnboxedFunctionMT(em, None, [self, Int, self.elt_type], None_), ("@%s_setitem" % (self.name,), [], None), 1, False),
                        Variable(UnboxedFunctionMT(em, None, [self, Slice, self], None_), ("@%s_setitem_slice" % (self.name,), [], None), 1, False)]),
            }
            self.class_methods["__str__"] = self.class_methods["__repr__"]
            self.typeobj_name = "@%s_typeobj" % self.name

            if not self.elt_type.hasattr("__eq__"):
                del self.class_methods["__eq__"]
                del self.class_methods["__contains__"]
            if not self.elt_type.hasattr("__lt__"):
                del self.class_methods["sort"]
        elif stage == "write":
            initial_size = 10
            elt_incref = self.elt_type.incref_llvm(em, "%elt")
            elt_decref = self.elt_type.decref_llvm(em, "%gone_elt")

            emitter = CodeEmitter(em)
            elt_repr_func = Variable(self.elt_type, "%gone_elt", 1, False).getattr(emitter, "__repr__", clsonly=True)
            repr_r = elt_repr_func.call(emitter, [])
            elt_repr = emitter.get_llvm()

            evaluated = eval_template("list", em, {
                'n':self.name,
                'in_':self.iter_type.name,
                'e':self.elt_type.llvm_type(),
                'elt_repr':elt_repr,
                'repr_r':repr_r.v,
                'initial_size':initial_size,
                'elt_incref':elt_incref,
                'elt_decref':elt_decref,
                'DEBUG_CHECKS':' ' if DEBUG_CHECKS else ';',
                'NO_DEBUG_CHECKS':' ' if not DEBUG_CHECKS else ';',
                'alloc_name':em.get_str_ptr(self.name),
                })
            em.llvm_tail.write(convert_none_to_void_ll(evaluated))

            ctemplate = eval_ctemplate("list", em, {
                'et':self.elt_type,
                'n':self.name,
                'in_':self.iter_type.name,
                })
            em.c_head.write(ctemplate)
        else:
            raise Exception(stage)

    def llvm_type(self):
        return "%%%s*" % (self.name,)

    def get_ctor_name(self):
        return "@%s_ctor" % (self.name,)

    def _can_convert_to(self, t):
        if isinstance(t, ListMT):
            return self.elt_type.can_convert_to(t.elt_type)
        return False

    def __make_conversion(self, em, t):
        assert isinstance(t, ListMT)

        em2 = CodeEmitter(em)

        func_name = "@" + em.mkname("_convert_list")

        em2.pl("define %s %s(%s %%l) {" % (t.llvm_type(), func_name, self.llvm_type()))
        em2.pl("start:")

        starting_block = "start"
        isnull_name = "%" + em2.mkname()
        idx_name = "%" + em2.mkname()
        next_idx_name = "%" + em2.mkname()
        done_name = "%" + em2.mkname()
        newlist_name = "%" + em2.mkname()
        rtn_name = "%" + em2.mkname()
        start_label = em2.mkname(prefix="label")
        cond_label = em2.mkname(prefix="label")
        loop_label = em2.mkname(prefix="label")
        back_label = em2.mkname(prefix="backedge")
        done_label = em2.mkname(prefix="label")

        em2.indent(4)
        em2.pl("; Starting conversion from %s to %s" % (self.llvm_type(), t.llvm_type()))
        em2.pl("%s = icmp eq %s %%l, null" % (isnull_name, self.llvm_type()))
        em2.pl("br i1 %s, label %%%s, label %%%s" % (isnull_name, done_label, start_label))

        em2.indent(-4)
        em2.pl()
        em2.pl("%s:" % (start_label,))
        em2.indent(4)
        em2.blockname = start_label

        var = Variable(self, "%l", 1, False)
        len_v = var.getattr(em2, "__len__", clsonly=True).call(em2, [])
        del var

        ctor_name = t.get_ctor_name()
        em2.pl("%s = call %s %s()" % (newlist_name, t.llvm_type(), ctor_name))
        rtn = Variable(t, newlist_name, 1, True)
        em2.pl("br label %%%s" % (cond_label,))

        em2.indent(-4)
        em2.pl()
        em2.pl("%s:" % (cond_label,))
        em2.indent(4)
        em2.blockname = cond_label
        em2.pl("%s = phi i64 [0, %%%s], [%s, %%%s]" % (idx_name, start_label, next_idx_name, back_label))
        em2.pl("%s = icmp sge i64 %s, %s" % (done_name, idx_name, len_v.v))
        em2.pl("br i1 %s, label %%%s, label %%%s" % (done_name, done_label, loop_label))

        em2.indent(-4)
        em2.pl()
        em2.pl("%s:" % (loop_label,))
        em2.indent(4)
        em2.blockname = loop_label

        var = Variable(self, "%l", 1, False)
        gotten = var.getattr(em2, "__getitem__", clsonly=True).call(em2, [Variable(Int, idx_name, 1, False)])
        del var

        gotten = gotten.convert_to(em2, t.elt_type)
        rtn.incvref(em2) # for the following call
        rtn.getattr(em2, "append").call(em2, [gotten])

        em2.pl("%s = add i64 %s, 1" % (next_idx_name, idx_name))
        em2.pl("br label %%%s" % (back_label,))

        # We use this trampoline to give the backedge a predictable name,
        # so that we can generate the phi instruction beforehand
        em2.indent(-4)
        em2.pl()
        em2.pl("%s:" % (back_label,))
        em2.indent(4)
        em2.blockname = back_label
        em2.pl("br label %%%s" % (cond_label,))

        em2.indent(-4)
        em2.pl()
        em2.pl("%s:" % (done_label,))
        em2.indent(4)
        em2.blockname = done_label
        em2.pl("%s = phi %s [null, %%%s], [%s, %%%s]" % (rtn_name, t.llvm_type(), starting_block, newlist_name, cond_label))
        em2.pl("; Done with conversion from %s to %s" % (self.llvm_type(), t.llvm_type()))
        em2.pl("ret %s %s" % (t.llvm_type(), rtn_name))

        em2.indent(-4)
        em2.pl("}")

        em.llvm_tail.write(em2.get_llvm() + '\n')

        return Variable(UnboxedFunctionMT(em, None, [self], t), (func_name, [], None), 1, False)
        # return Variable(t, rtn_name, 1, True)

    def _convert_to(self, em, var, t):
        if isinstance(t, BoxedMT):
            return t.convert_from(em, var)
        if not isinstance(t, ListMT) or not self.elt_type.can_convert_to(t.elt_type):
            raise UserTypeError(t)

        # TODO don't write out a new function if we already did for this type of conversion
        f = self.__make_conversion(em, t)
        return f.call(em, [var])

    @staticmethod
    def get_name(elt_type):
        return "list_%s" % elt_type.llvm_type().replace('%', '').replace('*', '')

    __lists = {}
    @staticmethod
    def make_list(elt_type):
        assert isinstance(elt_type, MT)
        if elt_type not in ListMT.__lists:
            ListMT.__lists[elt_type] = ListMT(elt_type)
        return ListMT.__lists[elt_type]

    class ListIteratorMT(MT):
        def __init__(self, lst):
            super(ListMT.ListIteratorMT, self).__init__()
            assert isinstance(lst, ListMT)
            self._lst = lst
            assert lst.name.startswith("list")
            self.name = "listiterator" + lst.name[4:]

            self.class_methods = {
                "__decref__": Variable(UnboxedFunctionMT(None, None, [self], None_), ("@%s_decref" % (self.name,), [], None), 1, False),
                "hasnext": Variable(UnboxedFunctionMT(None, None, [self], Bool), ("@%s_hasnext" % (self.name,), [], None), 1, False),
                "__incref__": Variable(UnboxedFunctionMT(None, None, [self], None_), ("@%s_incref" % (self.name,), [], None), 1, False),
                "next": Variable(UnboxedFunctionMT(None, None, [self], self._lst.elt_type), ("@%s_next" % (self.name,), [], None), 1, False),
            }
            self.typeobj_name = "@%s_typeobj" % self.name
            self.initialized = ("attrs", "write")

        def llvm_type(self):
            return "%%%s*" % (self.name)

class SetMT(MT):
    def __init__(self, elt_type):
        super(SetMT, self).__init__()
        assert isinstance(elt_type, MT)
        self.elt_type = elt_type
        self.name = SetMT.get_name(elt_type)

        self.iter_type = SetMT.SetIteratorMT(self)

    def _initialize(self, em, stage):
        if stage == "attrs":
            self.class_methods = {
                "add": Variable(UnboxedFunctionMT(em, None, [self, self.elt_type], None_), ("@%s_add" % (self.name,), [], None), 1, False),
                "__contains__": Variable(UnboxedFunctionMT(em, None, [self, self.elt_type], Bool), ("@%s_contains" % (self.name,), [], None), 1, False),
                "__decref__": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_decref" % (self.name,), [], None), 1, False),
                "__eq__": Variable(UnboxedFunctionMT(em, None, [self, self], Bool), ("@%s_eq" % (self.name,), [], None), 1, False),
                "__incref__": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_incref" % (self.name,), [], None), 1, False),
                "__iter__": Variable(UnboxedFunctionMT(em, None, [self], self.iter_type), ("@%s_iter" % (self.name,), [], None), 1, False),
                "__len__": Variable(UnboxedFunctionMT(em, None, [self], Int), ("@%s_len" % (self.name,), [], None), 1, False),
                "__nonzero__": Variable(UnboxedFunctionMT(em, None, [self], Bool), ("@%s_nonzero" % (self.name,), [], None), 1, False),
                "__repr__": Variable(UnboxedFunctionMT(em, None, [self], Str), ("@%s_repr" % (self.name,), [], None), 1, False),
            }
            self.class_methods["__str__"] = self.class_methods["__repr__"]
            self.typeobj_name = "@%s_typeobj" % self.name
        elif stage == "write":
            name = SetMT.get_name(self.elt_type)

            emitter = CodeEmitter(em)

            evaluated = eval_template("set", emitter, {
                'n':name,
                'elt_type':self.elt_type,
                'e':self.elt_type.llvm_type(),
                'iter_name':self.iter_type.name,
                })
            em.llvm_tail.write(convert_none_to_void_ll(evaluated))

            ctemplate = eval_ctemplate("set", em, {
                'et':self.elt_type,
                'n':name,
                'i':self.iter_type.name,
                })
            em.c_head.write(ctemplate)
        else:
            raise Exception(stage)

    def __repr__(self):
        return "<SetMT %r>" % (self.elt_type,)

    @staticmethod
    def get_name(elt_type):
        return "set_%s" % elt_type.llvm_type().replace('%', '').replace('*', '')

    def llvm_type(self):
        return "%%%s*" % (self.name,)

    def get_ctor_name(self):
        return "@%s_ctor" % (self.name,)

    __sets = {}

    @staticmethod
    def make_set(elt_type):
        assert isinstance(elt_type, MT)
        if elt_type not in SetMT.__sets:
            SetMT.__sets[elt_type] = SetMT(elt_type)
        return SetMT.__sets[elt_type]

    class SetIteratorMT(MT):
        def __init__(self, st):
            super(SetMT.SetIteratorMT, self).__init__()
            assert isinstance(st, SetMT)
            self._st = st
            assert st.name.startswith("set")
            self.name = "setiterator" + st.name[4:]

            self.class_methods = {
                "__decref__": Variable(UnboxedFunctionMT(None, None, [self], None_), ("@%s_decref" % (self.name,), [], None), 1, False),
                "hasnext": Variable(UnboxedFunctionMT(None, None, [self], Bool), ("@%s_hasnext" % (self.name,), [], None), 1, False),
                "__incref__": Variable(UnboxedFunctionMT(None, None, [self], None_), ("@%s_incref" % (self.name,), [], None), 1, False),
                "next": Variable(UnboxedFunctionMT(None, None, [self], self._st.elt_type), ("@%s_next" % (self.name,), [], None), 1, False),
            }

            self.initialized = ("attrs", "write")

        def llvm_type(self):
            return "%%%s*" % (self.name)

class DequeMT(MT):
    def __init__(self, elt_type):
        super(DequeMT, self).__init__()
        assert isinstance(elt_type, MT)
        self.elt_type = elt_type
        self.name = DequeMT.get_name(elt_type)

        self.iter_type = DequeMT.DequeIteratorMT(self)

    def _initialize(self, em, stage):
        if stage == "attrs":
            self.class_methods = {
                "append": Variable(UnboxedFunctionMT(em, None, [self, self.elt_type], None_), ("@%s_append" % (self.name,), [], None), 1, False),
                "appendleft": Variable(UnboxedFunctionMT(em, None, [self, self.elt_type], None_), ("@%s_appendleft" % (self.name,), [], None), 1, False),
                "__contains__": Variable(UnboxedFunctionMT(em, None, [self, self.elt_type], Bool), ("@%s_contains" % (self.name,), [], None), 1, False),
                "__decref__": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_decref" % (self.name,), [], None), 1, False),
                "__eq__": Variable(UnboxedFunctionMT(em, None, [self, self], Bool), ("@%s_eq" % (self.name,), [], None), 1, False),
                "__incref__": Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_incref" % (self.name,), [], None), 1, False),
                "__iter__": Variable(UnboxedFunctionMT(em, None, [self], self.iter_type), ("@%s_iter" % (self.name,), [], None), 1, False),
                "__len__": Variable(UnboxedFunctionMT(em, None, [self], Int), ("@%s_len" % (self.name,), [], None), 1, False),
                "__nonzero__": Variable(UnboxedFunctionMT(em, None, [self], Bool), ("@%s_nonzero" % (self.name,), [], None), 1, False),
                "pop": Variable(UnboxedFunctionMT(em, None, [self], self.elt_type), ("@%s_pop" % (self.name,), [], None), 1, False),
                "popleft": Variable(UnboxedFunctionMT(em, None, [self], self.elt_type), ("@%s_popleft" % (self.name,), [], None), 1, False),
                "__repr__": Variable(UnboxedFunctionMT(em, None, [self], Str), ("@%s_repr" % (self.name,), [], None), 1, False),
            }
            self.class_methods["__str__"] = self.class_methods["__repr__"]
            self.typeobj_name = "@%s_typeobj" % self.name

        elif stage == "write":
            name = DequeMT.get_name(self.elt_type)

            emitter = CodeEmitter(em)

            evaluated = eval_template("deque", emitter, {
                'n':self.name,
                'elt_type':self.elt_type,
                'e':self.elt_type.llvm_type(),
                'iter_name':self.iter_type.name,
                })
            em.llvm_tail.write(convert_none_to_void_ll(evaluated))

            ctemplate = eval_ctemplate("deque", em, {
                'et':self.elt_type,
                'n':name,
                'i':self.iter_type.name,
                })
            em.c_head.write(ctemplate)
        else:
            raise Exception(stage)

    @staticmethod
    def get_name(elt_type):
        return "deque_%s" % elt_type.llvm_type().replace('%', '').replace('*', '')

    def llvm_type(self):
        return "%%%s*" % (self.name,)

    def get_ctor_name(self):
        return "@%s_ctor" % (self.name,)

    __deques = {}

    @staticmethod
    def make_deque(elt_type):
        assert isinstance(elt_type, MT)
        if elt_type not in DequeMT.__deques:
            DequeMT.__deques[elt_type] = DequeMT(elt_type)
        return DequeMT.__deques[elt_type]

    class DequeIteratorMT(MT):
        def __init__(self, st):
            super(DequeMT.DequeIteratorMT, self).__init__()
            assert isinstance(st, DequeMT)
            self._st = st
            assert st.name.startswith("deque")
            self.name = "dequeiterator" + st.name[4:]

            self.class_methods = {
                "__decref__": Variable(UnboxedFunctionMT(None, None, [self], None_), ("@%s_decref" % (self.name,), [], None), 1, False),
                "hasnext": Variable(UnboxedFunctionMT(None, None, [self], Bool), ("@%s_hasnext" % (self.name,), [], None), 1, False),
                "__incref__": Variable(UnboxedFunctionMT(None, None, [self], None_), ("@%s_incref" % (self.name,), [], None), 1, False),
                "next": Variable(UnboxedFunctionMT(None, None, [self], self._st.elt_type), ("@%s_next" % (self.name,), [], None), 1, False),
            }
            self.initialized = ("attrs", "write")

        def llvm_type(self):
            return "%%%s*" % (self.name)

class Parametric1ArgCtorFuncMT(_SpecialFuncMT):
    def __init__(self, make_type, add_func_name):
        super(Parametric1ArgCtorFuncMT, self).__init__()
        self._make_type = make_type
        self._add_func_name = add_func_name
        self.__made = {}

    def _get_converter(self, em, iter_type):
        if iter_type not in self.__made:
            next_type = iter_type.get_attr_types()['next'][0]
            elt_type = next_type.get_instantiated().rtn_type

            rtn_type = self._make_type(elt_type)
            rtn_type.initialize(em, "write")

            func_name = "@" + em.mkname(prefix="%s_convert" % (rtn_type.name,))

            evaluated = eval_template("list_convert", em, {
                "iter_type":iter_type,
                "elt_type":elt_type,
                "rtn_type":rtn_type,
                "func_name":func_name,
                "add_func_name":self._add_func_name,
                })
            em.llvm_tail.write(evaluated)

            self.__made[iter_type] = Variable(UnboxedFunctionMT(em, None, [iter_type], rtn_type), (func_name, [], None), 1, False)
        return self.__made[iter_type]

    def call(self, em, v, args, expected_type=None):
        if len(args) == 1:
            arg, = args
            iter = arg.getattr(em, "__iter__").call(em, [])

            f = self._get_converter(em, iter.t)
            f.incvref(em)
            return f.call(em, [iter])
        elif not args:
            assert isinstance(expected_type, MT), repr(expected_type)
            name = "%" + em.mkname()
            em.pl("%s = call %s %s()" % (name, expected_type.llvm_type(), expected_type.get_ctor_name()))
            return Variable(expected_type, name, 1, True)
        else:
            raise Exception(len(args))

ListFunc = Parametric1ArgCtorFuncMT(ListMT.make_list, "append")
SetFunc = Parametric1ArgCtorFuncMT(SetMT.make_set, "add")
DequeFunc = Parametric1ArgCtorFuncMT(DequeMT.make_deque, "append")

class DictMT(MT):
    def __init__(self, key_type, value_type):
        super(DictMT, self).__init__()
        self.key_type = key_type
        self.value_type = value_type
        self.item_type = TupleMT.make_tuple([self.key_type, self.value_type])
        self.name = DictMT.get_name(key_type, value_type)

        self.key_iter_type = DictMT.DictIteratorMT(self, "key", self.key_type)
        self.value_iter_type = DictMT.DictIteratorMT(self, "value", self.value_type)
        self.item_iter_type = DictMT.DictIteratorMT(self, "item", self.item_type)

    def _initialize(self, em, stage):
        if stage == "attrs":
            self.class_methods = {
                "__contains__": Variable(UnboxedFunctionMT(em, None, [self, self.key_type], Bool), ("@%s_contains" % (self.name,), [], None), 1, False),
                "__decref__": Variable(UnboxedFunctionMT(None, None, [self], None_), ("@%s_decref" % (self.name,), [], None), 1, False),
                "__eq__": Variable(UnboxedFunctionMT(None, None, [self, self], Bool), ("@%s_eq" % (self.name,), [], None), 1, False),
                "get": Variable(UnboxedFunctionMT(None, None, [self, self.key_type, self.value_type], self.value_type), ("@%s_get" % self.name, [], None), 1, False),
                "__getitem__": Variable(UnboxedFunctionMT(em, None, [self, self.key_type], self.value_type), ("@%s_getitem" % (self.name,), [], None), 1, False),
                "__incref__": Variable(UnboxedFunctionMT(None, None, [self], None_), ("@%s_incref" % (self.name,), [], None), 1, False),
                "items": Variable(UnboxedFunctionMT(em, None, [self], ListMT.make_list(self.item_type)), ("@%s_items" % (self.name,), [], None), 1, False),
                "__iter__": Variable(UnboxedFunctionMT(em, None, [self], self.key_iter_type), ("@%s_iter" % (self.name,), [], None), 1, False),
                "iteritems": Variable(UnboxedFunctionMT(em, None, [self], self.item_iter_type), ("@%s_iteritems" % (self.name,), [], None), 1, False),
                "itervalues": Variable(UnboxedFunctionMT(em, None, [self], self.value_iter_type), ("@%s_itervalues" % (self.name,), [], None), 1, False),
                "__iter__": Variable(UnboxedFunctionMT(em, None, [self], self.key_iter_type), ("@%s_iter" % (self.name,), [], None), 1, False),
                "__len__": Variable(UnboxedFunctionMT(em, None, [self], Int), ("@%s_len" % (self.name,), [], None), 1, False),
                "__nonzero__": Variable(UnboxedFunctionMT(em, None, [self], Bool), ("@%s_nonzero" % (self.name,), [], None), 1, False),
                "__repr__": Variable(UnboxedFunctionMT(em, None, [self], Str), ("@%s_repr" % (self.name,), [], None), 1, False),
                "setdefault": Variable(UnboxedFunctionMT(em, None, [self, self.key_type, self.value_type], self.value_type), ("@%s_setdefault" % (self.name,), [], None), 1, False),
                "__setitem__": Variable(UnboxedFunctionMT(em, None, [self, self.key_type, self.value_type], None_), ("@%s_set" % (self.name,), [], None), 1, False),
                "values": Variable(UnboxedFunctionMT(em, None, [self], ListMT.make_list(self.value_type)), ("@%s_values" % (self.name,), [], None), 1, False),
            }
            self.class_methods["__str__"] = self.class_methods["__repr__"]
            self.class_methods["iterkeys"] = self.class_methods["__iter__"]
            self.typeobj_name = "@%s_typeobj" % self.name

        elif stage == "write":
            ListMT.make_list(self.key_type).initialize(em, "write")
            ListMT.make_list(self.value_type).initialize(em, "write")
            ListMT.make_list(self.item_type).initialize(em, "write")
            self.key_type.initialize(em, "write")
            self.value_type.initialize(em, "write")
            self.item_type.initialize(em, "write")

            template = eval_ctemplate("dict", em, {
                't':self,
                'n':self.name,
                })
            em.c_head.write(template)

            evaluated = eval_template("dict", em, {
                'n':self.name,
                'k':self.key_type.llvm_type(),
                'v':self.value_type.llvm_type(),
                'i':self.item_type.llvm_type(),
                'lv':ListMT.make_list(self.value_type).llvm_type(),
                'li':ListMT.make_list(self.item_type).llvm_type(),
                'key_iter_name':self.key_iter_type.name,
                'key_iter':self.key_iter_type.llvm_type(),
                'value_iter_name':self.value_iter_type.name,
                'value_iter':self.value_iter_type.llvm_type(),
                'item_iter_name':self.item_iter_type.name,
                'item_iter':self.item_iter_type.llvm_type(),
                })
            em.llvm_tail.write(convert_none_to_void_ll(evaluated))
        else:
            raise Exception(stage)

    def llvm_type(self):
        return "%%%s*" % (self.name,)

    def get_ctor_name(self):
        return "@%s_ctor" % (self.name,)

    @staticmethod
    def get_name(key_type, value_type):
        return "dict_%s_%s" % (key_type.llvm_type().replace('%', '').replace('*', ''), value_type.llvm_type().replace('%', '').replace('*', ''))

    __made_dicts = {}
    @staticmethod
    def make_dict(key_type, value_type):
        assert isinstance(key_type, MT)
        assert isinstance(value_type, MT)
        mem_key = (key_type, value_type)
        if mem_key not in DictMT.__made_dicts:
            d = DictMT(key_type, value_type)
            DictMT.__made_dicts[mem_key] = d
        return DictMT.__made_dicts[mem_key]

    class DictIteratorMT(MT):
        def __init__(self, d, type_name, rtn_type):
            super(DictMT.DictIteratorMT, self).__init__()
            assert isinstance(d, DictMT)
            self._d = d
            assert d.name.startswith("dict")
            self.name = "dict%siterator%s" % (type_name, d.name[4:])

            self.class_methods = {
                "__decref__": Variable(UnboxedFunctionMT(None, None, [self], None_), ("@%s_decref" % (self.name,), [], None), 1, False),
                "hasnext": Variable(UnboxedFunctionMT(None, None, [self], Bool), ("@%s_hasnext" % (self.name,), [], None), 1, False),
                "__incref__": Variable(UnboxedFunctionMT(None, None, [self], None_), ("@%s_incref" % (self.name,), [], None), 1, False),
                "__iter__": Variable(UnboxedFunctionMT(None, None, [self], self), ("@%s_iter" % (self.name,), [], None), 1, False),
                "next": Variable(UnboxedFunctionMT(None, None, [self], rtn_type), ("@%s_next" % (self.name,), [], None), 1, False),
            }
            self.typeobj_name = "@%s_typeobj" % self.name
            self.initialized = ("attrs", "write")

        def llvm_type(self):
            return "%%%s*" % (self.name)

class DictFuncMT(_SpecialFuncMT):
    __made = {}
    @staticmethod
    def get_converter(em, iter_type):
        if iter_type not in DictFuncMT.__made:
            next_type = iter_type.get_attr_types()['next'][0]
            elt_type = next_type.get_instantiated().rtn_type
            assert isinstance(elt_type, TupleMT), elt_type
            assert len(elt_type.elt_types) == 2

            key_type, value_type = elt_type.elt_types

            rtn_type = DictMT.make_dict(key_type, value_type)
            rtn_type.initialize(em, "write")

            func_name = "@" + em.mkname(prefix="%s_convert" % (rtn_type.name,))

            evaluated = eval_template("dict_convert", em, {
                "iter_type":iter_type,
                "elt_type":elt_type,
                "key_type":key_type,
                "value_type":value_type,
                "rtn_type":rtn_type,
                "func_name":func_name,
                })
            em.llvm_tail.write(evaluated)

            DictFuncMT.__made[iter_type] = Variable(UnboxedFunctionMT(em, None, [iter_type], rtn_type), (func_name, [], None), 1, False)
        return DictFuncMT.__made[iter_type]

    def call(self, em, v, args, expected_type=None):
        assert len(args) == 1

        arg, = args
        if isinstance(arg.t, DictMT):
            iter = arg.getattr(em, "iteritems").call(em, [])
        else:
            iter = arg.getattr(em, "__iter__").call(em, [])

        f = DictFuncMT.get_converter(em, iter.t)
        f.incvref(em)
        return f.call(em, [iter])
DictFunc = singleton(DictFuncMT)

class _StructWriter(object):
    def __init__(self, em, type_name, fields, constants, dealloc_maker=None, function_types=None):
        self.type_name = type_name
        self.fields = fields
        self.constants = constants

        self._function_types = function_types or {}
        self._function_placeholders = {}
        assert all(isinstance(v, UnboxedFunctionMT) for v in self._function_types.values())

        self.dealloc_maker = dealloc_maker or _StructWriter.make_struct_dealloc

        if not type_name:
            assert not fields
            return

    def write(self, em):
        if not self.type_name:
            assert not self.fields
            return

        field_positions = {}
        for i, (n, t) in enumerate(self.fields):
            t.initialize(em, "attrs")
            field_positions[n] = (i+1, t)
        dealloc = self.dealloc_maker(em, self.type_name, field_positions)

        em.llvm_tail.write(eval_template("struct", em, {
            'n':self.type_name,
            'type_str':", ".join(['i64'] + [type.llvm_type() for (name, type) in self.fields]),
            'DEBUG_CHECKS':' ' if DEBUG_CHECKS else ';',
            'NO_DEBUG_CHECKS':' ' if not DEBUG_CHECKS else ';',
            'dealloc':dealloc,
            'alloc_name':em.get_str_ptr(self.type_name),
            }))

    @staticmethod
    def make_struct_dealloc(em, type_name, field_positions):
        deallocs = []
        for n, (i, t) in sorted(field_positions.items()):
            ptr_name = "%" + em.mkname()
            name = "%" + em.mkname()
            d = t.decref_llvm(em, name)
            if d is None:
                continue
            deallocs.append("%s = getelementptr %%%s* %%self, i64 0, i32 %d\n    %s = load %s* %s\n    %s" % (ptr_name, type_name, i, name, t.llvm_type(), ptr_name, d))
        dealloc = '\n'.join(s for s in deallocs if s)
        return dealloc

    def get(self, em, v, name, skip_incref=False):
        if name in self.constants:
            if name in self._function_types and self.constants[name] is None:
                assert name not in self._function_placeholders
                placeholder = em.get_placeholder()
                self.constants[name] = Variable(self._function_types[name], (placeholder, [], None), 1, False)
                self._function_placeholders[name] = placeholder
                del self._function_types[name]

            assert self.constants[name], name

            self.constants[name].incvref(em)
            return self.constants[name]
            # return self.constants[name].dup({})

        assert isinstance(v, str), v

        offset = 1
        for i, (n, t) in enumerate(self.fields):
            if n == name:
                assert v
                assert em
                p_name = '%' + em.mkname()
                rtn_name = '%' + em.mkname()
                em.pl("%s = getelementptr inbounds %%%s* %s, i64 0, i32 %d" % (p_name, self.type_name, v, i + offset))
                em.pl("%s = load %s* %s" % (rtn_name, t.llvm_type(), p_name))
                em.pc("#error unimplemented 13")

                if not skip_incref:
                    inc = t.incref_llvm(em, rtn_name)
                    if inc:
                        em.pl(inc + " ; struct get")

                marked = not skip_incref
                return Variable(t, rtn_name, 1, marked)
        raise UserAttributeError("struct doesn't have field %r" % (name,))

    def set(self, em, v, name, val, skip_decref_prev=False, skip_incref=False):
        assert v is None or isinstance(v, str), v

        if name in self.constants:
            if self.constants[name] is not None:
                orig = self.constants[name]
                if isinstance(val.t, (UserModuleMT, ClassMT, ModuleMT)):
                    assert val.t is orig.t
                elif isinstance(val.t, UnboxedFunctionMT):
                    assert name in self._function_placeholders
                    assert name not in self._function_types, "should have been deleted by the get that created the placeholder"
                    em.register_replacement(self._function_placeholders[name], val.v[0])
                    del self._function_placeholders[name]
                else:
                    raise Exception(name, orig.t)
            self.constants[name] = val
            return

        assert is_emitter(em) and em, em
        assert v

        offset = 1
        for i, (n, t) in enumerate(self.fields):
            if n == name:
                p_name = '%' + em.mkname()
                em.pl("%s = getelementptr inbounds %%%s* %s, i64 0, i32 %d" % (p_name, self.type_name, v, i + offset))
                val = val.convert_to(em, t)
                assert val.t == t

                if not skip_decref_prev:
                    old_val = '%' + em.mkname()
                    d = t.decref_llvm(em, old_val)
                    if d:
                        em.pl("%s = load %s* %s" % (old_val, t.llvm_type(), p_name))
                        em.pl(d)

                em.pl("store %s %s, %s* %s" % (t.llvm_type(), val.v, t.llvm_type(), p_name))
                if not skip_incref:
                    em.pl(t.incref_llvm(em, val.v))
                val.decvref(em)
                em.pc("#error unimplemented 14")
                return
        raise UserAttributeError("struct doesn't have field %r" % (name,))

    def has(self, name):
        return self.has_constant(name) or any(name == n for (n, t) in self.fields)

    def has_constant(self, name):
        return name in self.constants

    def alloc(self, em):
        name = "%" + em.mkname()
        em.pl("%s = call %%%s* @%s_alloc()" % (name, self.type_name, self.type_name))
        em.pc("#error unimplemented 15")
        return name

class ClosureMT(MT):
    PARENT_FIELD_NAME = " __parent__"
    def __init__(self, em, name, parent_type, parent_obj, cells, functions, classes, modules):
        super(ClosureMT, self).__init__()
        assert (parent_type is None) or isinstance(parent_type, ClosureMT)
        assert isinstance(parent_obj, bool)

        if not parent_type:
            assert not parent_obj
        self.inlined = not cells
        if self.inlined:
            # Just to make sure the name is invalid and we don't try to use it:
            assert name == ''

        if parent_obj:
            # Ensure that chains of just inlined closures dont get objects
            assert (not parent_type.inlined) or (parent_type.inlined and parent_type.parent_obj)

        self.name = name
        self.parent_type = parent_type # ClosureMT of the parent (or None)
        self.parent_obj = parent_obj # Whether this closure has a reference to the parent object
        # self.cells = cells # list of [(name, type)]
        # self.functions = functions # mapping of name -> UnboxedFunctionMT
        # self.classes = classes # mapping of name -> ClassMT
        # self.modules = modules # mapping of name -> ModuleMT

        struct_fields = cells
        if cells and parent_obj:
            struct_fields.insert(0, (ClosureMT.PARENT_FIELD_NAME, parent_type.instantiated_type()))
        assert not set(functions).intersection(classes)
        assert not set(classes).intersection(modules)
        assert not set(modules).intersection(functions)
        constants = {}
        constants.update(functions)
        constants.update(classes)
        constants.update(modules)

        self._struct = _StructWriter(em, name, struct_fields, constants)
        self._struct.write(em)
        self.initialized = ("attrs", "write")

    def instantiated_type(self):
        if self.inlined:
            return self.parent_type.instantiated_type()
        return self

    def llvm_type(self):
        if self.inlined:
            assert self.parent_type, "shouldnt want the llvm type of this because it's not going to be instantiated"
            return self.parent_type.llvm_type()
        return "%%%s*" % (self.name,)

    def dup(self, v, dup_cache):
        assert v is None or isinstance(v, str)
        return v

    def alloc(self, em, parent=None):
        assert (parent is None) == (not self.parent_obj), (parent, self.parent_obj)
        if self.inlined:
            if parent:
                r = parent.split(em)
                r.t = self
                return r
            else:
                return Variable(self, None, 1, False)

        if parent:
            assert parent.t == self.parent_type

        name = self._struct.alloc(em)
        assert isinstance(name, str)
        if parent:
            self._struct.set(em, name, ClosureMT.PARENT_FIELD_NAME, parent, skip_decref_prev=True)
        return Variable(self, name, 1, True)

    def getattr(self, em, v, attr, clsonly):
        first_real = self
        while first_real.inlined:
            first_real = first_real.parent_type
            assert first_real

        if attr == "__incref__":
            return UnboxedInstanceMethod.make(em, v, Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_incref" % first_real.name, [], None), 1, False))
        if attr == "__decref__":
            return UnboxedInstanceMethod.make(em, v, Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_decref" % first_real.name, [], None), 1, False))

        raise Exception("couldn't find '%s' attribute on %s" % (attr, self))

    def has(self, name, include_parents=False):
        if self._struct.has(name):
            return True
        if not include_parents:
            return False

        if self.parent_type:
            if self.parent_obj:
                return self.parent_type.has(name)
            else:
                return self.parent_type.has_constant(name)
        return False

    def has_constant(self, name, include_parents=False):
        if self._struct.has_constant(name):
            return True
        if not include_parents:
            return False

        return self.parent_type and self.parent_type.has_constant(name)

    def get(self, em, v, name):
        assert isinstance(name, str)
        assert (v is None) or isinstance(v, str)

        if self._struct.has_constant(name):
            return self._struct.get(em, None, name)

        if v is None:
            return self.parent_type.get(None, None, name)

        if self._struct.has(name):
            return self._struct.get(em, v, name)

        assert self.parent_type

        if self.inlined:
            return self.parent_type.get(em, v, name)

        if self.parent_obj:
            parent = self._struct.get(em, v, ClosureMT.PARENT_FIELD_NAME)
            r = self.parent_type.get(em, parent.v, name)
            parent.decvref(em)
            return r
        else:
            return self.parent_type.get(None, None, name)

    def set(self, em, v, name, val):
        assert isinstance(val, Variable)

        self._struct.set(em, v, name, val)

    def _can_convert_to(self, t):
        return False

    @staticmethod
    def create(em, node, parent_type, parent_obj, closure_info, type_info):
        assert is_emitter(em)
        assert (parent_type is None) or (isinstance(parent_type, ClosureMT)), parent_type
        assert isinstance(closure_info, closure_analyzer.ClosureResults)
        assert isinstance(parent_obj, bool)

        if parent_obj:
            assert parent_type

        cells = []
        for name in closure_info.used_in_nested:
            try:
                cells.append((name, type_info.get_scope_type(em, node, name)))
            except:
                print "failed on", name
                raise

        # Probably don't need to always create the global closure?
        # if not cells and not isinstance(node, _ast.Module):
        if not cells:
            return ClosureMT(em, '', parent_type, parent_obj, cells,
                dict([(n, None) for n in closure_info.functions]),
                dict([(n, None) for n in closure_info.classes]),
                dict([(n, None) for n in closure_info.modules]))

        type_name = em.mkname(prefix="closure")

        return ClosureMT(
                em,
                type_name,
                parent_type,
                parent_obj,
                cells,
                dict([(n, None) for n in closure_info.functions]),
                dict([(n, None) for n in closure_info.classes]),
                dict([(n, None) for n in closure_info.modules]),
                )

class ClassMT(MT):
    def __init__(self, base, type_name, displayname, llvm_type=None):
        super(ClassMT, self).__init__()
        if type_name != "object":
            assert base
            assert isinstance(base, ClassMT), base
        self.base = base

        self._name = type_name
        self._displayname = displayname
        if llvm_type is None:
            llvm_type = "%%%s*" % type_name
        self._llvm_type = llvm_type
        self._ctor = None
        self._instance = InstanceMT(self)

        self._clsattr_types = {}
        self._clsattrs = {}
        self._instattr_types = []

    def _initialize(self, em, stage):
        if stage == "attrs":
            pass
        elif stage == "write":
            type_string = ", ".join(['i64'] + [type.llvm_type() for (name, type) in self._instattr_types])

            decref_all = ""
            for i in xrange(len(self._instattr_types)):
                attr_type = self._instattr_types[i][1]
                attr_type.initialize(em, "attrs")
                d = attr_type.decref_llvm(em, "%%attr%d" % (i,))
                if not d:
                    continue
                decref_all += "%%ptr%d = getelementptr inbounds %s %%self, i64 0, i32 %d\n" % (i, self._instance.llvm_type(), i + 1)
                decref_all += "%%attr%d = load %s* %%ptr%d\n" % (i, attr_type.llvm_type(), i)
                decref_all += d + '\n'
            decref_all = decref_all.replace('\n', '\n    ')

            if self._ctor:
                # TODO Hacky that it still writes out the __new__ function but doesn't use it
                new_args = ""
                init = ""
            elif not self.has_classattr("__init__"):
                new_args = ""
                init = ""
                self._ctor = Variable(UnboxedFunctionMT(None, None, [], self._instance), ("@%s_new" % self._name, [], None), 1, False)
            else:
                init_fn = self.getattr(em, Variable(self, (), 1, False), "__init__", False)
                init_fn.t.initialize(em, "write")

                init_fn.incvref(em)
                new_em = CodeEmitter(em)
                args = [Variable(self._instance, "%rtn", 1, False)]
                for i, a in enumerate(init_fn.t.arg_types[1:]):
                    args.append(Variable(a, "%%v%d" % i, 1, False))
                init_fn.call(new_em, args)
                init = new_em.get_llvm()
                new_t = UnboxedFunctionMT(None, None, init_fn.t.arg_types[1:], self._instance, ndefaults=init_fn.t.ndefaults)
                assert isinstance(init_fn.t, UnboxedFunctionMT)
                defaults = init_fn.v[1]
                self._ctor = Variable(new_t, ("@%s_new" % self._name, defaults, None), 1, False)
                new_args = ", ".join(["%s %%v%d" % (a.llvm_type(), i) for i, a in enumerate(init_fn.t.arg_types[1:])])

            strname_ptr = em.get_str_ptr(self._name)
            strname_str = "@" + em.mkname("str")
            em.llvm_tail.write("%s = global %%string {i64 1, i64 %d, i8* %s, [0 x i8] zeroinitializer}\n" % (strname_str, len(self._name), strname_ptr))
            typeobj = "{i64 1, %%string* %s, %%type* null}" % (strname_str,)

            em.llvm_tail.write(eval_template("instance", em, {
                'n':self._name,
                'type_str':type_string,
                'DEBUG_CHECKS':' ' if DEBUG_CHECKS else ';',
                'NO_DEBUG_CHECKS':' ' if not DEBUG_CHECKS else ';',
                'decref_all':decref_all,
                'new_args':new_args,
                'init':init,
                'alloc_name':em.get_str_ptr(self._name),
                'typeobj': typeobj,
                'displayname': self._displayname,
                }))

            em.c_head.write(eval_ctemplate("instance", em, {'n':self._name}))
        else:
            raise Exception(stage)

    def get_typeobj(self, em):
        return Variable(Type, "@%s_typeobj" % self._name, 1, False)

    def set_clsattr_type(self, name, t):
        assert not self.initialized
        assert name not in ("__nrefs__", "__incref__", "__decref__")

        self._clsattr_types[name] = t

    def setattr(self, em, v, attr, val):
        assert not v
        assert isinstance(val.t, UnboxedFunctionMT)
        self.set_clsattr_value(attr, val, em=em)

    def set_clsattr_value(self, name, v, _init=False, em=None, force=False):
        if not force:
            assert name not in ("__nrefs__", "__incref__", "__decref__")
        assert isinstance(v.t, (UnboxedFunctionMT, PolymorphicFunctionMT))
        assert isinstance(v.v, tuple), (v.v, "probably not a constant and we don't allocate actual storage for class attrs")

        assert _init or em

        if _init or (em and name in self._clsattr_types and name not in self._clsattrs):
            if _init:
                assert name not in self._clsattr_types
            assert name not in self._clsattrs
            self._clsattr_types[name] = v.t
            self._clsattrs[name] = v.dup({})
        else:
            assert name in self._clsattr_types
            assert name in self._clsattrs
            placeholder = self._clsattrs[name]
            assert v.t.can_convert_to(self._clsattr_types[name]), (v.t, self._clsattr_types[name])
            assert isinstance(v.t, UnboxedFunctionMT)

            placeholder_defaults = placeholder.v[1]
            new_defaults = v.v[1]
            assert len(new_defaults) == len(placeholder_defaults)
            for i in xrange(len(placeholder_defaults)):
                assert new_defaults[i].t == placeholder_defaults[i].t
                print placeholder_defaults[i].v, new_defaults[i].v
                em.register_replacement(placeholder_defaults[i].v, str(new_defaults[i].v))
            em.register_replacement(placeholder.v[0], v.v[0])

    def set_instattr_type(self, name, t):
        assert not self.initialized
        assert name not in ("__nrefs__", "__incref__", "__decref__")

        assert not any(name == _n for (_n, _t) in self._instattr_types)
        self._instattr_types.append((name, t))

    def has_classattr(self, attr):
        return attr in self._clsattr_types or (self.base and self.base.has_classattr(attr))

    def getattr(self, em, var, attr, clsonly):
        # TODO this should just use _StructWriter; there's some compilcation with builtin classes though
        assert not clsonly

        if attr not in self._clsattr_types:
            assert self.base.has_classattr(attr)
            return self.base.getattr(em, var, attr, clsonly)

        if attr in self._clsattr_types and attr not in self._clsattrs:
            t = self._clsattr_types[attr]
            assert isinstance(t, CallableMT), (name, t)
            new_t = UnboxedFunctionMT(None, None, t.arg_types, t.rtn_type, ndefaults=t.ndefaults)
            defaults = [Variable(t.arg_types[len(t.arg_types) - t.ndefaults + i], em.get_placeholder(), 1, False) for i in xrange(t.ndefaults)]
            self._clsattrs[attr] = Variable(new_t, (em.get_placeholder(), defaults, None), 1, False)

        assert attr in self._clsattrs
        v = self._clsattrs[attr].dup({})
        assert isinstance(v.v, tuple), (v.v, "probably not a constant and we don't allocate actual storage for class attrs")
        assert not v.marked, "should probably have incref'd in this case?"
        return v

    def free(self, em, v):
        assert v == ()
        for v in self._clsattrs.itervalues():
            print object.__getattribute__(v, "__dict__")
            v.decvref(em)

    def dup(self, v, dup_cache):
        assert v == ()
        return v

    def call(self, em, v, args, expected_type=None):
        assert v == ()

        self._ctor.incvref(em)
        return self._ctor.call(em, args)

    def get_instance(self):
        return self._instance

    __nclasses = 0
    @staticmethod
    def create(base, displayname):
        type_name = "cls%d" % ClassMT.__nclasses
        ClassMT.__nclasses += 1
        return ClassMT(base, type_name, displayname)

    def llvm_type(self):
        assert 0, "shouldnt do this"

    def get_instantiated(self):
        return self._ctor.t.get_instantiated()

    def _can_convert_to(self, t):
        return self._ctor.t.can_convert_to(t)

    def _convert_to(self, em, var, t):
        if t is Type:
            return self.get_typeobj(em)

        self._ctor.incvref(em)
        return self._ctor.convert_to(em, t)

class InstanceMT(MT):
    def __init__(self, cls):
        super(InstanceMT, self).__init__()
        assert isinstance(cls, ClassMT)
        self.cls = cls
        self._name = cls._name
        self._llvm_type = cls._llvm_type

    def _initialize(self, em, stage):
        # Careful: calling initailize with the same stage has the potential to
        # introduce cyclic dependencies, but the class should only call instance.initialize
        # with an earlier stage, so it should be ok:
        self.cls.initialize(em, stage)

    def llvm_type(self):
        return self._llvm_type

    def getattrptr(self, em, var, attr):
        assert isinstance(var, Variable)

        offset = 1
        for i, (name, t) in enumerate(self.cls._instattr_types):
            if name == attr:
                pl = '%' + em.mkname()
                em.pl("%s = getelementptr %s %s, i64 0, i32 %d" % (pl, self.llvm_type(), var.v, i + offset))
                em.pc("#error unimplemented 15")
                return Variable(PtrMT(t), pl, 1, False)

        raise UserAttributeError(attr)

    def hasattr(self, attr):
        return attr in self.cls._clsattr_types or attr in [name for (name, t) in self.cls._instattr_types]

    def getattr(self, em, var, attr, clsonly):
        self.cls._MT__check_initialized("attrs")
        assert isinstance(var, Variable)

        if not clsonly:
            if attr == "__class__":
                return self.cls.get_typeobj(em)

            offset = 1
            for i, (name, t) in enumerate(self.cls._instattr_types):
                if name == attr:
                    pl = '%' + em.mkname()
                    rtn = '%' + em.mkname()
                    em.pl("%s = getelementptr %s %s, i64 0, i32 %d" % (pl, self.llvm_type(), var.v, i + offset))
                    em.pl("%s = load %s* %s" % (rtn, t.llvm_type(), pl))
                    em.pc("#error unimplemented 16")
                    i = t.incref_llvm(em, rtn)
                    if i:
                        em.pl(i)
                    return Variable(t, rtn, 1, True)

        m = self._get_clsmethod(em, attr)
        return UnboxedInstanceMethod.make(em, var, m)

    def get_attr_types(self):
        if self.cls.base:
            r = self.cls.base._instance.get_attr_types()
        else:
            r = {}

        for name, t in self.cls._instattr_types:
            r[name] = (t, AttributeAccessType.FIELD)
        for name, t in self.cls._clsattr_types.iteritems():
            if name in r:
                continue
            r[name] = (UnboxedInstanceMethod(self, t), AttributeAccessType.CONST_METHOD)
        # TODO default functions like __repr__
        r["__incref__"] = (UnboxedInstanceMethod(self, UnboxedFunctionMT(None, None, [self], None_)), AttributeAccessType.CONST_METHOD)
        r["__decref__"] = (UnboxedInstanceMethod(self, UnboxedFunctionMT(None, None, [self], None_)), AttributeAccessType.CONST_METHOD)
        if "__repr__" not in r:
            r["__repr__"] = (UnboxedInstanceMethod(self, UnboxedFunctionMT(None, None, [self], Str)), AttributeAccessType.CONST_METHOD)
        r["__class__"] = (Type, AttributeAccessType.IMPLICIT_FIELD)
        return r

    def _get_clsmethod(self, em, attr):
        self.cls._MT__check_initialized("attrs")
        if not self.cls.has_classattr(attr):
            if attr == "__str__":
                return self._get_clsmethod(em, "__repr__")

            if attr == "__repr__":
                return Variable(UnboxedFunctionMT(em, None, [self], Str), ("@%s_repr" % self._name, [], None), 1, False)
            if attr == "__nonzero__":
                return Variable(UnboxedFunctionMT(em, None, [self], Bool), ("@%s_nonzero" % self._name, [], None), 1, False)
            if attr == "__eq__":
                return Variable(UnboxedFunctionMT(em, None, [self, self], Bool), ("@%s_eq" % self._name, [], None), 1, False)
            if attr == "__incref__":
                return Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_incref" % self._name, [], None), 1, False)
            if attr == "__decref__":
                return Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_decref" % self._name, [], None), 1, False)

            raise UserAttributeError("no such attribute '%s' on %s" % (attr, self))

        return self.cls.getattr(em, Variable(self.cls, (), 1, False), attr, False)

    def setattr(self, em, v, attr, val):
        assert isinstance(v, str)
        assert isinstance(val, Variable)

        offset = 1
        for i, (name, t) in enumerate(self.cls._instattr_types):
            if name == attr:
                val = val.convert_to(em, t)
                assert t == val.t, (t, val.t)
                inc = val.t.incref_llvm(em, val.v)
                if inc:
                    em.pl(inc)

                pl = '%' + em.mkname()
                old_val = '%' + em.mkname()
                em.pl("%s = getelementptr %s %s, i64 0, i32 %d" % (pl, self.llvm_type(), v, i + offset))
                d = t.decref_llvm(em, old_val)
                if d:
                    em.pl("%s = load %s* %s" % (old_val, t.llvm_type(), pl))
                    em.pl(d)
                em.pl("store %s %s, %s* %s" % (t.llvm_type(), val.v, t.llvm_type(), pl))
                em.pc("#error unimplemented 17")
                val.decvref(em)
                return
        raise Exception("doesn't have attribute '%s'" % (attr,))

    def convert_to(self, em, var, t):
        if t is self:
            return var

        assert isinstance(t, BoxedMT), (self, t)
        return t.convert_from(em, var)

    def _can_convert_to(self, t):
        # TODO this is wrong
        return False

    def __repr__(self):
        return "<InstanceMT %r (%s)>" % (self.llvm_type(), self.cls._displayname)

ObjectClass = ClassMT(None, "object", "object")
Object = ObjectClass._instance
IntClass = ClassMT(ObjectClass, "int", "int", llvm_type="i64")
Int = IntClass._instance
FloatClass = ClassMT(ObjectClass, "float", "float", llvm_type="double")
Float = FloatClass._instance
StrClass = ClassMT(ObjectClass, "str", "str", llvm_type="%string*")
Str = StrClass._instance
BoolClass = ClassMT(ObjectClass, "bool", "bool", "i1")
Bool = BoolClass._instance
TypeClass = ClassMT(ObjectClass, "type", "type")
Type = TypeClass._instance
FileClass = ClassMT(ObjectClass, "file", "file")
File = FileClass._instance

# TODO there is a lot of duplication between this and stuff like closures
class UserModuleMT(MT):
    LOADED_FIELD_NAME = " __loaded__"

    def __init__(self, em, module_name, module_fn, type_name, vars, constants, function_types):
        super(UserModuleMT, self).__init__()
        self.module_name = module_name
        self._type_name = type_name
        self.fn = module_fn

        self._struct = _StructWriter(em, type_name, vars, constants, function_types=function_types)
        self._struct.write(em)
        self.initialized = ("attrs", "write")

    def llvm_type(self):
        return "%%%s*" % (self._type_name)

    def has(self, name):
        return self._struct.has(name)

    def has_constant(self, name):
        return self._struct.has_constant(name)

    # Have this to mimic closure objects, since this can be a closure
    def set(self, em, v, name, val):
        return self.setattr(em, v, name, val)

    def getattr(self, em, v, name, clsonly=False, skip_incref=False):
        assert not clsonly
        return self._struct.get(em, v.v, name, skip_incref=skip_incref)

    def setattr(self, em, v, attr, val):
        return self._struct.set(em, v, attr, val)

    def load(self, em):
        em.pc("#error unimplemented 18")
        em.pl("call void @%s_init()" % self.module_name)

    def load_modules(self, em, cg, closure_info, ts_module, type_info):
        for n in closure_info.modules:
            assert self._struct.constants[n] is None
            # TODO this is pretty hacky
            submodule = ts_module.get_name(n)
            assert len(submodule.types()) == 1
            submodule, = submodule.types()
            m = cg.import_module(em, submodule.name)
            self._struct.constants[n] = m

    @staticmethod
    def make(em, module_name, module, module_fn, closure_info, ts_module, type_info):
        assert is_emitter(em)
        assert isinstance(module, _ast.Module)
        assert isinstance(closure_info, closure_analyzer.ClosureResults)

        vars = []
        vars.append((UserModuleMT.LOADED_FIELD_NAME, Bool))
        for name in closure_info.used_in_nested:
            try:
                vars.append((name, type_info.get_scope_type(em, module, name)))
            except:
                print "failed on", name
                raise

        constants = {}

        function_types = {}
        for n in closure_info.functions:
            u = ts_module.get_name(n)
            assert len(u.types()) == 1
            if u.types()[0].is_dead():
                print "Not adding %s since it's dead" % (n,)
                continue

            try:
                function_types[n] = type_info._convert_type(em, u)
            except Exception:
                print >>sys.stderr, "Failed when converting attribute %s of module %s [%s]" % (n, module_name, ts_module.get_name(n).display())
                raise
        for n, c in function_types.iteritems():
            assert n not in constants
            function_types[n] = UnboxedFunctionMT(em, None, c.arg_types, c.rtn_type)
            constants[n] = None

        for n in closure_info.classes:
            assert n not in constants
            cls = type_info._convert_type(em, ts_module.get_name(n))
            assert isinstance(cls, ClassMT)
            constants[n] = Variable(cls, (), 1, False)

        for n in closure_info.modules:
            assert n not in constants
            constants[n] = None
            # We will fill this in later, to allow for
            # cycles in the import graph

        type_name = em.mkname(prefix="mod_%s" % filter(lambda c: not c.isdigit(), module_name))
        t = UserModuleMT(
                em,
                module_name,
                module_fn,
                type_name,
                vars,
                constants,
                function_types,
                )
        module_obj_name = "@" + em.mkname(prefix="module")

        module_obj = Variable(t, module_obj_name, 1, False)
        em.llvm_tail.write(eval_template("module", em, {
            'module_obj':module_obj,
            'type_name':type_name,
            'module_name':module_name,
            't':t,
            }))
        return module_obj

class ModuleMT(MT):
    def __init__(self, attrs):
        super(ModuleMT, self).__init__()
        self._attrs = attrs
        self.initialized = ("attrs", "write")

    def getattr(self, em, var, attr, clsonly):
        assert not clsonly

        if attr not in self._attrs:
            raise UserAttributeError(attr)

        v = self._attrs[attr].dup({})
        # TODO to support setting things, this should assert marked, but then we need to put it somewhere
        assert not v.marked, "should probably have incref'd in this case?"
        return v

    def llvm_type(self):
        assert 0, "shouldnt do this"

    def get_instantiated(self):
        assert 0, "dont support this yet"
        # Don't support raising these yet
        return None

    def _can_convert_to(self, t):
        return False

class PtrMT(MT):
    """ An MT to represent the type of a stored pointer to an object.  They should only exist as a compiler implementation detail. """
    def __init__(self, referent_type):
        super(PtrMT, self).__init__()
        self.referent_type = referent_type
        self.initialized = ("attrs", "write")

    def llvm_type(self):
        return self.referent_type.llvm_type() + "*"
    def incref_llvm(self, em, name):
        return None
    def decref_llvm(self, em, name):
        return None

class FuncPtrMT(MT):
    def __init__(self, func_type):
        super(FuncPtrMT, self).__init__()
        self.func_type = func_type
        self.initialized = ("attrs", "write")

    def llvm_type(self):
        return self.func_type.llvm_type()

    def incref_llvm(self, em, name):
        return None
    def decref_llvm(self, em, name):
        return None
    def getattr(self, em, var, attr, clsonly=False):
        raise UserAttributeError(attr)

class _UnderlyingMT(MT):
    def __init__(self):
        super(_UnderlyingMT, self).__init__()
        self.initialized = ("attrs", "write")
    def llvm_type(self):
        return "%underlying*"
    def incref_llvm(self, em, v):
        assert False, "shouldn't be calling this"
    def decref_llvm(self, em, v):
        assert False, "shouldn't be calling this"
Underlying = singleton(_UnderlyingMT)

class BoxedMT(MT):
    class StorageStrategy(object):
        CONST_METHOD = "method" # store a reference to the method, and create the instancemethod on access
        PTR = "ptr" # store a pointer to the field in the object
        VALUE = "value" # store the value of the field in the boxed object

    UNDERLYING_FIELD_NAME = " __underlying"

    @staticmethod
    def make_struct_dealloc(em, type_name, field_positions):
        deallocs = []
        decref_name = None
        underlying_name = None
        for n, (i, t) in sorted(field_positions.items()):
            ptr_name = "%" + em.mkname()
            name = "%" + em.mkname()
            deallocs.append("%s = getelementptr %%%s* %%self, i64 0, i32 %d\n    %s = load %s* %s" % (ptr_name, type_name, i, name, t.llvm_type(), ptr_name))

            if n == BoxedMT.UNDERLYING_FIELD_NAME:
                underlying_name = name
                continue

            if n == "__decref__":
                decref_name = name

            d = t.decref_llvm(em, name)
            if d is None:
                continue
            deallocs.append(d)

        assert decref_name
        assert underlying_name
        deallocs.append("call void %s(%%underlying* %s)" % (decref_name, underlying_name))

        dealloc = '\n    '.join(s for s in deallocs if s)
        return dealloc

    __nboxes = 0
    def __init__(self, types):
        super(BoxedMT, self).__init__()
        self._name = "boxed%d" % (BoxedMT.__nboxes,)
        BoxedMT.__nboxes += 1
        self.types = types

    def _initialize(self, em, stage):
        if stage == "attrs":
            for t in self.types:
                t.initialize(em, "attrs")

            all_attrs = [t.get_attr_types() for t in self.types]
            all_attr_names = set()
            for i in xrange(len(self.types)):
                d = all_attrs[i]
                all_attr_names.update(d)
                assert "__class__" in d, (d, self.types[i])

                for n, (t, at) in d.items():
                    try:
                        d[n] = (t.get_instantiated(), at)
                    except CantInstantiateException:
                        del d[n]

            attrs = {}
            for n in all_attr_names:
                if any(n not in d for d in all_attrs):
                    continue
                attr_types = [d[n] for d in all_attrs]
                if any(at[1] != attr_types[0][1] for at in attr_types):
                    continue

                types = [at[0] for at in attr_types]
                if attr_types[0][1] == AttributeAccessType.FIELD and len(set(types)) > 1:
                    continue

                sup = make_common_supertype(types)
                if sup is not None:
                    # TODO this next initialize should somehow be taken care of before the
                    # enclosing _initialize is even started
                    # sup.initialize(em)
                    attrs[n] = sup, attr_types[0][1]

            assert "__incref__" in attrs
            assert "__decref__" in attrs
            assert "__class__" in attrs
            attrs.pop("__init__", None)

            converted_attrs = []
            for n, (t, at) in attrs.iteritems():
                ss = BoxedMT._storage_strategy(n, t, at)
                converted_attrs.append((n, t, ss))

            self.attrs = {}
            struct_fields = []
            struct_fields.append((BoxedMT.UNDERLYING_FIELD_NAME, Underlying))
            for n, t, ss in converted_attrs:
                st = self._storage_type(em, t, ss)
                # print n, t, st
                struct_fields.append((n, st))
                self.attrs[n] = (t, ss, st)

            self._struct = _StructWriter(em, self._name, struct_fields, {}, dealloc_maker=BoxedMT.make_struct_dealloc)

            self.__converters = {}
            em.c_head.write("struct %s;" % self._name)
        elif stage == "write":
            self._struct.write(em)
        else:
            raise Exception(stage)

    def llvm_type(self):
        return "%" + self._name + "*"

    def c_type(self):
        return "struct " + self._name + "*"

    def hasattr(self, attr):
        return self._struct.has(attr)

    def setattr(self, em, v, attr, val):
        assert self.initialized
        if attr not in self.attrs:
            raise UserAttributeError("boxed object does not contain settable %s" % attr)
        t, ss, st = self.attrs[attr]
        assert ss == BoxedMT.StorageStrategy.PTR, ss

        ptr = self._struct.get(em, v, attr)
        assert isinstance(ptr.t, PtrMT)
        assert ptr.t.referent_type is val.t

        prev = "%" + em.mkname()
        dec = val.t.decref_llvm(em, prev)
        if dec:
            em.pl("%s = load %s* %s" % (prev, val.t.llvm_type(), ptr.v))
            em.pl(dec)

        em.pl("store %s %s, %s* %s" % (val.t.llvm_type(), val.v, val.t.llvm_type(), ptr.v))

    def getattr(self, em, v, attr, clsonly):
        assert self.initialized
        # Handle these specially, since they hit the boxed object, not the underlying:
        if attr == "__incref__":
            return UnboxedInstanceMethod.make(em, v, Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_incref" % self._name, [], None), 1, False))
        if attr == "__decref__":
            return UnboxedInstanceMethod.make(em, v, Variable(UnboxedFunctionMT(em, None, [self], None_), ("@%s_decref" % self._name, [], None), 1, False))
        assert attr not in ("__incref__", "__decref__")

        stored = self._struct.get(em, v.v, attr)

        t, ss, st = self.attrs[attr]
        if ss == BoxedMT.StorageStrategy.CONST_METHOD:
            raise Exception("Pretty sure this isn't right, since we should incref the underlying as well")
            o = self._struct.get(em, v, BoxedMT.UNDERLYING_FIELD_NAME)
            assert isinstance(stored.t, FuncPtrMT)
            return UnboxedInstanceMethod.make(em, o, stored)
        elif ss == BoxedMT.StorageStrategy.VALUE:
            return stored
        elif ss == BoxedMT.StorageStrategy.PTR:
            assert isinstance(stored.t, PtrMT)
            rtn_type = st.referent_type
            r = '%' + em.mkname()
            em.pl("%s = load %s* %s" % (r, rtn_type.llvm_type(), stored.v))
            inc = rtn_type.incref_llvm(em, r)
            if inc:
                em.pl(inc + " ; getting boxed attr by ptr")
            em.pc("#error unimplemented 19")
            return Variable(rtn_type, r, 1, True)
        raise Exception(ss)

    def _storage_type(self, em, attr_type, storage_strategy):
        if storage_strategy == BoxedMT.StorageStrategy.CONST_METHOD:
            return FuncPtrMT(UnboxedFunctionMT(em, None, [Underlying] + attr_type.arg_types, attr_type.rtn_type))
        elif storage_strategy == BoxedMT.StorageStrategy.VALUE:
            return attr_type
        elif storage_strategy == BoxedMT.StorageStrategy.PTR:
            return PtrMT(attr_type)
        else:
            raise Exception(storage_strategy)

    def can_convert_from(self, t):
        if t is None_:
            return True

        attr_types = t.get_attr_types()
        for attr_name, (_t, ss, st) in self.attrs.iteritems():
            if attr_name not in attr_types or not attr_types[attr_name][0].can_convert_to(_t):
                return False
        return True

    def convert_from(self, em, var):
        self._MT__check_initialized("attrs")
        # TODO assert size of var object is 64 bits
        # TODO return None if the input was None

        if var.t not in self.__converters:
            converter_name = "@%s_from_%s" % (self._name, var.t.llvm_type().replace("*", "_").replace("%", ""))

            self.__converters[var.t] = Variable(UnboxedFunctionMT(None, None, [var.t], self), (converter_name, [], None), 1, False)

            evaluated = eval_template("boxer", em, {
                'bt': self,
                'ot': var.t,
                'converter_name':converter_name,
            })
            em.llvm_tail.write(evaluated)

        converter = self.__converters[var.t]
        converter.incvref(em)
        return converter.call(em, [var])

    @staticmethod
    def _storage_strategy(name, t, at):
        if name in ("__incref__", "__decref__"):
            return BoxedMT.StorageStrategy.CONST_METHOD
        if at in (AttributeAccessType.CONST_METHOD, AttributeAccessType.IMPLICIT_FIELD):
            return BoxedMT.StorageStrategy.VALUE
        if at == AttributeAccessType.FIELD:
            return BoxedMT.StorageStrategy.PTR
        raise Exception(at)

_made_supertypes = {}
def make_common_supertype(types):
    assert all(isinstance(t, MT) for t in types)
    types = tuple(sorted(set(types)))
    if len(types) == 1:
        return types[0]

    if types == tuple(sorted([Int, Float])):
        return Float

    if types in _made_supertypes:
        return _made_supertypes[types]

    if all(isinstance(t, ClassMT) for t in types):
        return Type

    if all(isinstance(t, CallableMT) for t in types):
        for t in types[1:]:
            if t.arg_types != types[0].arg_types:
                return None
        ret_type = make_common_supertype([t.rtn_type for t in types])
        if ret_type is None:
            return None
        return CallableMT.make_callable(types[0].arg_types, 0, ret_type)
    if any(isinstance(t, CallableMT) for t in types):
        # Callables aren't mixable with non-callables, at least for now.
        # Probably can/should return the common_supertype of all the __call__ attributes?
        return None

    rtn = BoxedMT(types)
    _made_supertypes[types] = rtn
    return rtn

def common_subtype(em, types):
    raise NotImplementedError()

class _FakeMT(MT):
    def __init__(self, attrs):
        super(_FakeMT, self).__init__()
        self._attrs = attrs

    def _initialize(self, em, stage):
        pass

    def get_attr_types(self):
        return self._attrs

# Some type classes for stdlib stuff:
STDLIB_TYPES = []
def _make_iterable(elt_type):
    iterator = BoxedMT([_FakeMT({
        "__class__": (Type, AttributeAccessType.IMPLICIT_FIELD),
        "__incref__": (CallableMT.make_callable([], 0, None_), AttributeAccessType.CONST_METHOD),
        "__decref__": (CallableMT.make_callable([], 0, None_), AttributeAccessType.CONST_METHOD),
        "hasnext": (CallableMT.make_callable([], 0, Bool), AttributeAccessType.CONST_METHOD),
        "next": (CallableMT.make_callable([], 0, elt_type), AttributeAccessType.CONST_METHOD),
        })])
    iterable = BoxedMT([_FakeMT({
        "__class__": (Type, AttributeAccessType.IMPLICIT_FIELD),
        "__incref__": (CallableMT.make_callable([], 0, None_), AttributeAccessType.CONST_METHOD),
        "__decref__": (CallableMT.make_callable([], 0, None_), AttributeAccessType.CONST_METHOD),
        "__iter__": (CallableMT.make_callable([], 0, iterator), AttributeAccessType.CONST_METHOD),
        })])
    STDLIB_TYPES.append(iterator)
    STDLIB_TYPES.append(iterable)
    return iterator, iterable

_IntIterator, _IntIterable = _make_iterable(Int)
_FloatIterator, _FloatIterable = _make_iterable(Float)

_Boolable = BoxedMT([_FakeMT({
    "__class__": (Type, AttributeAccessType.IMPLICIT_FIELD),
    "__incref__": (CallableMT.make_callable([], 0, None_), AttributeAccessType.CONST_METHOD),
    "__decref__": (CallableMT.make_callable([], 0, None_), AttributeAccessType.CONST_METHOD),
    "__nonzero__": (CallableMT.make_callable([], 0, Bool), AttributeAccessType.CONST_METHOD),
    })])
STDLIB_TYPES.append(_Boolable)
_BoolableIterator, _BoolableIterable = _make_iterable(_Boolable)


BUILTINS = {
        "True":Variable(Bool, 1, 1, False),
        "False":Variable(Bool, 0, 1, False),
        "len":Variable(Len, (), 1, False),
        "str":Variable(StrClass, (), 1, False),
        "repr":Variable(ReprFunc, (), 1, False),
        "type":Variable(TypeClass, (), 1, False),
        "map":Variable(MapFunc, (), 1, False),
        "reduce":Variable(ReduceFunc, (), 1, False),
        "nrefs":Variable(Nref, (), 1, False),
        "bool":Variable(BoolClass, (), 1, False),
        "list":Variable(ListFunc, (), 1, False),
        "dict":Variable(DictFunc, (), 1, False),
        "set":Variable(SetFunc, (), 1, False),
        "isinstance":Variable(Isinstance, (), 1, False),
        "__cast__":Variable(Cast, (), 1, False),
        "enumerate":Variable(Enumerate, (), 1, False),
        "chr":Variable(UnboxedFunctionMT(None, None, [Int], Str), ("@chr", [], None), 1, False),
        "ord":Variable(UnboxedFunctionMT(None, None, [Str], Int), ("@ord", [], None), 1, False),
        # "open":Variable(UnboxedFunctionMT(None, None, [Str], File), ("@file_open", [], None), 1, True),
        "open":Variable(UnboxedFunctionMT(None, None, [Str, Str], File, ndefaults=1), ("@file_open2", [Variable(Str, "@.str_r", 1, True)], None), 1, False),
        "int":Variable(IntClass, (), 1, False),
        "min":PolymorphicFunctionMT.make([
            Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_min", [], None), 1, False),
            Variable(UnboxedFunctionMT(None, None, [Float, Float], Float), ("@float_min", [], None), 1, False),
            Variable(MinFunc, (), 1, False),
            ]),
        "max":PolymorphicFunctionMT.make([
            Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_max", [], None), 1, False),
            Variable(UnboxedFunctionMT(None, None, [Float, Float], Float), ("@float_max", [], None), 1, False),
            Variable(MaxFunc, (), 1, False),
            ]),
        "float":Variable(FloatClass, (), 1, False),
        "file":Variable(FileClass, (), 1, False),
        "abs":PolymorphicFunctionMT.make([
            Variable(UnboxedFunctionMT(None, None, [Int], Int), ("@int_abs", [], None), 1, False),
            Variable(UnboxedFunctionMT(None, None, [Float], Float), ("@float_abs", [], None), 1, False)]),

        "None":Variable(None_, "null", 1, False),
        "object":Variable(ObjectClass, (), 1, False),
        "sum":PolymorphicFunctionMT.make([
            Variable(UnboxedFunctionMT(None, None, [_IntIterable], Int), ("@sum_int", [], None), 1, False),
            Variable(UnboxedFunctionMT(None, None, [_FloatIterable], Float), ("@sum_float", [], None), 1, False),
            ]),
        "any":Variable(UnboxedFunctionMT(None, None, [_BoolableIterable], Bool), ("@any", [], None), 1, False),
        }

BUILTIN_MODULES = {
        "time":Variable(ModuleMT({
            'time':Variable(UnboxedFunctionMT(None, None, [], Float), ("@time_time", [], None), 1, False),
            'clock':Variable(UnboxedFunctionMT(None, None, [], Float), ("@time_clock", [], None), 1, False),
            'sleep':Variable(UnboxedFunctionMT(None, None, [Float], None_), ("@time_sleep", [], None), 1, False),
            }), 1, 1, False),
        "sys":Variable(ModuleMT({
            'stdin':Variable(File, "@sys_stdin", 1, False),
            'stdout':Variable(File, "@sys_stdout", 1, False),
            'stderr':Variable(File, "@sys_stderr", 1, False),
            }), 1, 1, False),
        "math":Variable(ModuleMT({
            'sqrt':Variable(UnboxedFunctionMT(None, None, [Float], Float), ("@sqrt", [], None), 1, False),
            'tan':Variable(UnboxedFunctionMT(None, None, [Float], Float), ("@tan", [], None), 1, False),
            'sin':Variable(UnboxedFunctionMT(None, None, [Float], Float), ("@sin", [], None), 1, False),
            'cos':Variable(UnboxedFunctionMT(None, None, [Float], Float), ("@cos", [], None), 1, False),
            'ceil':Variable(UnboxedFunctionMT(None, None, [Float], Float), ("@ceil", [], None), 1, False),
            'pi':Variable(Float, format_float(3.141592653589793), 1, False),
            }), 1, 1, False),
        "collections":Variable(ModuleMT({
            'deque':Variable(DequeFunc, (), 1, False),
            }), 1, 1, False),
        # Interopability library:
        "hax":Variable(ModuleMT({
            "ftoi":Variable(UnboxedFunctionMT(None, None, [Float], Int), ("@hax_ftoi", [], None), 1, False),
            "itof":Variable(UnboxedFunctionMT(None, None, [Int], Float), ("@hax_itof", [], None), 1, False),
            "min":Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_min", [], None), 1, False),
            "max":Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_max", [], None), 1, False),
            "fmin":Variable(UnboxedFunctionMT(None, None, [Float, Float], Float), ("@float_min", [], None), 1, False),
            "abs":Variable(UnboxedFunctionMT(None, None, [Float], Float), ("@float_abs", [], None), 1, False),
            "initvideo":Variable(UnboxedFunctionMT(None, None, [Int, Int], None_), ("@hax_initvideo", [], None), 1, False),
            "plot":Variable(UnboxedFunctionMT(None, None, [Int, Int, Int, Int, Int], None_), ("@hax_plot", [], None), 1, False),
            }), 1, 1, False),
        }

SliceMT.setup_class_methods()
NoneMT.setup_class_methods()

def setup_int():
    IntClass._ctor = Variable(UnboxedFunctionMT(None, None, [Str, Int], Int, ndefaults=1), ("@int_", [Variable(Int, 10, 1, False)], None), 1, False)

    def _int_can_convert_to(t):
        return t is Float

    def _int_convert_to(em, var, t):
        if t is Int:
            return var
        if t is Float:
            name = '%' + em.mkname()
            em.pl('%s = sitofp i64 %s to double' % (name, var.v))
            em.pc("#error unimplemented")
            var.decvref(em)
            return Variable(Float, name, 1, True)
        if isinstance(t, BoxedMT):
            return t.convert_from(em, var)
        raise UserTypeError(t)
    Int._can_convert_to = _int_can_convert_to
    Int.convert_to = _int_convert_to

    int_class_methods = {
        "__add__": Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_add", [], None), 1, False),
        "__and__": Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_and", [], None), 1, False),
        "__or__": Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_or", [], None), 1, False),
        "__div__": Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_div", [], None), 1, False),
        "__lshift__": Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_lshift", [], None), 1, False),
        "__mod__": Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_mod", [], None), 1, False),
        "__mul__": Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_mul", [], None), 1, False),
        "__neg__": Variable(UnboxedFunctionMT(None, None, [Int], Int), ("@int_neg", [], None), 1, False),
        "__nonzero__": Variable(UnboxedFunctionMT(None, None, [Int], Bool), ("@int_nonzero", [], None), 1, False),
        "__pow__": Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_pow", [], None), 1, False),
        "__repr__": Variable(UnboxedFunctionMT(None, None, [Int], Str), ("@int_repr", [], None), 1, False),
        "__rshift__": Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_rshift", [], None), 1, False),
        "__sub__": Variable(UnboxedFunctionMT(None, None, [Int, Int], Int), ("@int_sub", [], None), 1, False),
        # "__incref__": Variable(UnboxedFunctionMT(None, None, [Int], None_), ("@int_incref", [], None), 1, False),
        # "__decref__": Variable(UnboxedFunctionMT(None, None, [Int], None_), ("@int_decref", [], None), 1, False),
            }
    int_class_methods["__str__"] = int_class_methods["__repr__"]
    for attr in COMPARE_MAP.values():
        int_class_methods[attr] = Variable(UnboxedFunctionMT(None, None, [Int, Int], Bool), ("@int_" + attr[2:-2], [], None), 1, False)
    for n, v in int_class_methods.iteritems():
        IntClass.set_clsattr_value(n, v, _init=True)
    IntClass.initialized = ("attrs", "write")
    Int.initialized = ("attrs", "write")
setup_int()

def setup_float():
    FloatClass._ctor = Variable(UnboxedFunctionMT(None, None, [Int], Float), ("@float_", [], None), 1, False)

    float_class_methods = {
        "__add__": Variable(UnboxedFunctionMT(None, None, [Float, Float], Float), ("@float_add", [], None), 1, False),
        "__div__": Variable(UnboxedFunctionMT(None, None, [Float, Float], Float), ("@float_div", [], None), 1, False),
        "__mod__": Variable(UnboxedFunctionMT(None, None, [Float, Float], Float), ("@float_mod", [], None), 1, False),
        "__mul__": Variable(UnboxedFunctionMT(None, None, [Float, Float], Float), ("@float_mul", [], None), 1, False),
        "__neg__": Variable(UnboxedFunctionMT(None, None, [Float], Float), ("@float_neg", [], None), 1, False),
        "__nonzero__": Variable(UnboxedFunctionMT(None, None, [Float], Bool), ("@float_nonzero", [], None), 1, False),
        "__pow__": Variable(UnboxedFunctionMT(None, None, [Float, Float], Float), ("@float_pow", [], None), 1, False),
        "__rdiv__": Variable(UnboxedFunctionMT(None, None, [Float, Float], Float), ("@float_rdiv", [], None), 1, False),
        "__repr__": Variable(UnboxedFunctionMT(None, None, [Float], Str), ("@float_repr", [], None), 1, False),
        "__rsub__": Variable(UnboxedFunctionMT(None, None, [Float, Float], Float), ("@float_rsub", [], None), 1, False),
        "__str__": Variable(UnboxedFunctionMT(None, None, [Float], Str), ("@float_str", [], None), 1, False),
        "__sub__": Variable(UnboxedFunctionMT(None, None, [Float, Float], Float), ("@float_sub", [], None), 1, False),
        # "__incref__": Variable(UnboxedFunctionMT(None, None, [Float], None_), ("@float_incref", [], None), 1, False),
        # "__decref__": Variable(UnboxedFunctionMT(None, None, [Float], None_), ("@float_decref", [], None), 1, False),
    }
    float_class_methods["__radd__"] = float_class_methods["__add__"]
    float_class_methods["__rmul__"] = float_class_methods["__mul__"]
    for attr in COMPARE_MAP.values():
        float_class_methods[attr] = Variable(UnboxedFunctionMT(None, None, [Float, Float], Bool), ("@float_" + attr[2:-2], [], None), 1, False)

    for n, v in float_class_methods.iteritems():
        FloatClass.set_clsattr_value(n, v, _init=True)
    FloatClass.initialized = ("attrs", "write")
    Float.initialized = ("attrs", "write")
setup_float()

def setup_string():
    StrIteratorClass = ClassMT(ObjectClass, "striterator", "striterator")
    StrIterator = StrIteratorClass._instance

    StrClass._ctor = Variable(StrFunc, (), 1, False)
    em = None
    string_class_methods = {
        "__add__": Variable(UnboxedFunctionMT(em, None, [Str, Str], Str), ("@str_add", [], None), 1, False),
        "__eq__": Variable(UnboxedFunctionMT(em, None, [Str, Str], Bool), ("@str_eq", [], None), 1, False),
        "__getitem__": PolymorphicFunctionMT.make([
                            Variable(UnboxedFunctionMT(em, None, [Str, Int], Str), ("@str_getitem", [], None), 1, False),
                            Variable(UnboxedFunctionMT(em, None, [Str, Slice], Str), ("@str_getitem_slice", [], None), 1, False)]),
        "join": Variable(UnboxedFunctionMT(em, None, [Str, ListMT.make_list(Str)], Str), ("@str_join", [], None), 1, False),
        "__len__": Variable(UnboxedFunctionMT(em, None, [Str], Int), ("@str_len", [], None), 1, False),
        "__le__": Variable(UnboxedFunctionMT(em, None, [Str, Str], Bool), ("@str_le", [], None), 1, False),
        "__lt__": Variable(UnboxedFunctionMT(em, None, [Str, Str], Bool), ("@str_lt", [], None), 1, False),
        "__mul__": Variable(UnboxedFunctionMT(em, None, [Str, Int], Str), ("@str_mul", [], None), 1, False),
        "__ne__": Variable(UnboxedFunctionMT(em, None, [Str, Str], Bool), ("@str_ne", [], None), 1, False),
        "__nonzero__": Variable(UnboxedFunctionMT(em, None, [Str], Bool), ("@str_nonzero", [], None), 1, False),
        "__repr__": Variable(UnboxedFunctionMT(em, None, [Str], Str), ("@str_repr", [], None), 1, False),
        "split": Variable(UnboxedFunctionMT(em, None, [Str, Str], ListMT.make_list(Str), ndefaults=1), ("@str_split", [Variable(Str, "null", 1, False)], None), 1, False),
        "__str__": Variable(UnboxedFunctionMT(em, None, [Str], Str), ("@str_str", [], None), 1, False),
        # "__incref__": Variable(UnboxedFunctionMT(em, None, [Str], None_), ("@str_incref", [], None), 1, False),
        # "__decref__": Variable(UnboxedFunctionMT(em, None, [Str], None_), ("@str_decref", [], None), 1, False),
        "strip": Variable(UnboxedFunctionMT(em, None, [Str], Str), ("@str_strip", [], None), 1, False),
        "lstrip": Variable(UnboxedFunctionMT(em, None, [Str], Str), ("@str_lstrip", [], None), 1, False),
        "rstrip": Variable(UnboxedFunctionMT(em, None, [Str], Str), ("@str_rstrip", [], None), 1, False),
        "__iter__": Variable(UnboxedFunctionMT(em, None, [Str], StrIterator), ("@str_iter", [], None), 1, False),
    }

    for n, v in string_class_methods.iteritems():
        StrClass.set_clsattr_value(n, v, _init=True)
    StrClass.initialized = ("attrs", "write")
    Str.initialized = ("attrs", "write")

    StrIteratorClass.set_clsattr_value("hasnext", Variable(UnboxedFunctionMT(em, None, [StrIterator], Bool), ("@striterator_hasnext", [], None), 1, False), _init=True)
    StrIteratorClass.set_clsattr_value("next", Variable(UnboxedFunctionMT(em, None, [StrIterator], Str), ("@striterator_next", [], None), 1, False), _init=True)
    StrIteratorClass.set_instattr_type(" str", Str)
    StrIteratorClass.set_instattr_type(" pos", Int)
    STDLIB_TYPES.append(StrIteratorClass)
setup_string()

def setup_bool():
    BoolClass._ctor = Variable(BoolFunc, (), 1, False)

    em = None
    bool_class_methods = {
        "__nonzero__": Variable(UnboxedFunctionMT(em, None, [Bool], Bool), ("@bool_nonzero", [], None), 1, False),
        "__repr__": Variable(UnboxedFunctionMT(em, None, [Bool], Str), ("@bool_repr", [], None), 1, False),
        "__eq__": Variable(UnboxedFunctionMT(em, None, [Bool, Bool], Bool), ("@bool_eq", [], None), 1, False),
    }
    bool_class_methods["__str__"] = bool_class_methods["__repr__"]

    def _bool_can_convert_to(self, t):
        return t in (Int,)

    for n, v in bool_class_methods.iteritems():
        BoolClass.set_clsattr_value(n, v, _init=True)
    BoolClass.initialized = ("attrs", "write")
    Bool.initialized = ("attrs", "write")
setup_bool()

def setup_type():
    TypeClass._ctor = Variable(TypeFunc, (), 1, False)

    type_class_methods = {
        "__repr__": Variable(UnboxedFunctionMT(None, None, [Type], Str), ("@type_repr_", [], None), 1, False),
    }
    type_class_methods["__str__"] = type_class_methods["__repr__"]
    for n, v in type_class_methods.iteritems():
        TypeClass.set_clsattr_value(n, v, _init=True)
    TypeClass.set_clsattr_value("__incref__", Variable(UnboxedFunctionMT(None, None, [Type], None_), ("@type_incref_", [], None), 1, False), _init=True, force=True)
    TypeClass.set_clsattr_value("__decref__", Variable(UnboxedFunctionMT(None, None, [Type], None_), ("@type_decref_", [], None), 1, False), _init=True, force=True)

    TypeClass.set_instattr_type("__name__", Str)
    TypeClass.set_instattr_type("__base__", Type)
    # TypeClass.initialized = ("attrs", "write")
    # Type.initialized = ("attrs", "write")
setup_type()

def setup_file():
    FileClass.set_clsattr_value("__init__", Variable(UnboxedFunctionMT(None, None, [File, Str], None_), ("@file_init", [], None), 1, False), _init=True)
    FileClass.set_clsattr_value("read", Variable(UnboxedFunctionMT(None, None, [File, Int], Str), ("@file_read", [], None), 1, False), _init=True)
    FileClass.set_clsattr_value("write", Variable(UnboxedFunctionMT(None, None, [File, Str], None_), ("@file_write", [], None), 1, False), _init=True)
    FileClass.set_clsattr_value("readline", Variable(UnboxedFunctionMT(None, None, [File], Str), ("@file_readline", [], None), 1, False), _init=True)
    FileClass.set_clsattr_value("close", Variable(UnboxedFunctionMT(None, None, [File], None_), ("@file_close", [], None), 1, False), _init=True)
    FileClass.set_clsattr_value("flush", Variable(UnboxedFunctionMT(None, None, [File], None_), ("@file_flush", [], None), 1, False), _init=True)
    FileClass.set_clsattr_value("__enter__", Variable(UnboxedFunctionMT(None, None, [File], File), ("@file_enter", [], None), 1, False), _init=True)
    FileClass.set_clsattr_value("__exit__", Variable(UnboxedFunctionMT(None, None, [File, None_, None_, None_], None_), ("@file_exit", [], None), 1, False), _init=True)
    FileClass.set_instattr_type("closed", Bool)
    FileClass.set_instattr_type("fd", Int)
    FileClass.initialized = ("attrs", "write")
    File.initialized = ("attrs", "write")
setup_file()
