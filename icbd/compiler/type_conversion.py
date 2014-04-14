import os
import sys

from icbd.type_analyzer import type_system, type_checker, builtins
from . import compiler_types
from .code_emitter import CodeEmitter

class InferredTypeOutput(object):
    def __init__(self, fn, pythonpath=[]):
        self._made_classes = {}

        fn = os.path.abspath(fn)
        e = type_checker.Engine(allow_import_errors=False)
        self.e = e
        e.python_path.extend(pythonpath)
        e._load(fn, "__main__")

        good = e.analyze()
        assert good
        for node, errs in e.errors.iteritems():
            scope = e.scopes[node[0]]
            while not isinstance(scope, type_checker.ModuleScope):
                scope = scope._parent
            filename = scope._filename

            for pos, msg in errs.iteritems():
                good = False
                print >>sys.stderr, "%s:%d:%d ERROR %s" % (filename, pos[0], pos[1], msg)
        if not good:
            sys.exit(1)
        # print "Done with type analysis"

        # out_fn = "/tmp/out.html"
        # out_func = lambda fn:os.path.join("/tmp", os.path.basename(fn).replace(".py", ".html"))
        # html = e.format_html(fn, out_func)
        # open(out_fn, 'w').write(html)

        self._module_map = {}

        """
        out_func = lambda fn:os.path.join("/tmp", os.path.basename(fn).replace(".py", ".html"))
        html = e.format_html(fn, out_func)
        open("/tmp/out.html", 'w').write(html)
        import hashlib
        print "%s -> %s (%s)" % (fn, '/tmp/out.html', hashlib.sha1(html).hexdigest())
        """

    def get_module(self, filename):
        return self.e._loaded_modules[os.path.abspath(filename)]

    def map_module(self, ts_module, compiler_module):
        assert isinstance(compiler_module, compiler_types.UserModuleMT)
        assert isinstance(ts_module, type_system.Module)
        self._module_map[ts_module] = compiler_module


    def get_expr_type(self, em, node):
        u = self.e.node_types[node]
        try:
            r = self._convert_type(em, u.prettify())
        except Exception:
            print "failed converting", u.prettify().display()
            raise
        return r

    def is_dead_function(self, node):
        u = self.e.node_types[node]
        assert len(u.types()) == 1
        t, = u.types()
        return t.is_dead()

    def get_scope_type(self, em, node, name):
        return self._convert_type(em, self.e.scopes[node].get_name(name, None))

    def get_block_starting_type(self, em, node, node_id, name):
        u = self.e.input_states[(node, node_id)].locals_[name]
        try:
            return self._convert_type(em, u)
        except:
            print "Failure getting starting type of %s" % (name,)
            raise

    def _convert_type(self, em, u):
        to_initialize = []
        r = self._make_type(u, to_initialize)

        for t in to_initialize:
            t.initialize(em, "write")

        return r

    def _make_class(self, t, to_initialize):
        if isinstance(t, type_system.ClassType):
            if t == builtins.FileClass:
                return compiler_types.FileClass
            if t == builtins.ObjectClass:
                return compiler_types.ObjectClass

        assert isinstance(t, type_system.UserClassType), (t, getattr(t, "name", repr(t)))
        if t not in self._made_classes:
            assert len(t._bases) == 1
            base = self._make_class(t._bases[0], to_initialize)

            # Important to create the ClassMT object first, since the attributes of it may reference the class itself;
            # if we tried to convert all the attributes first, we would be triggered to convert the class again (and again)
            self._made_classes[t] = cls = compiler_types.ClassMT.create(base, t.name)

            for attr_name, attr_type in t._attributes.items():
                if len(attr_type.types()) == 1 and isinstance(attr_type.types()[0], type_system.UserFunction) and attr_type.types()[0].is_dead():
                    print "Not adding class method %s since it's dead" % (attr_name,)
                    continue

                try:
                    cls.set_clsattr_type(attr_name, self._make_type(attr_type, to_initialize))
                except:
                    print >>sys.stderr, "Failed converting class attribute %r of %r" % (attr_name, t.name)
                    raise

            for name, u in t.instance()._attrs.iteritems():
                if name == "__dict__":
                    continue
                try:
                    cls.set_instattr_type(name, self._make_type(u, to_initialize))
                except:
                    print "failed to convert", name, u.prettify().display()
                    raise
            to_initialize.append(cls)
        return self._made_classes[t]

    def _make_type(self, u, to_initialize):
        r = self.__make_type(u, to_initialize)
        assert r, u.display()
        to_initialize.append(r)
        return r

    def __make_type(self, u, to_initialize):
        if isinstance(u, type_system.Type):
            u = type_system.Union(u)
        assert isinstance(u, type_system.Union), u
        u = u.prettify()

        if len(u.types()) > 1:
            types = [self._make_type(_u, to_initialize) for _u in u.types()]

            return compiler_types.make_common_supertype(types)

        assert len(u.types()) == 1, u.display()
        [t] = u.types()

        if isinstance(t, type_system.IntType):
            return compiler_types.Int
        if isinstance(t, type_system.BoolType):
            return compiler_types.Bool
        if isinstance(t, type_system.StrType):
            return compiler_types.Str
        if isinstance(t, type_system.NoneType):
            return compiler_types.None_
        if isinstance(t, type_system.FloatType):
            return compiler_types.Float

        if isinstance(t, type_system.InstanceType):
            if t.cls is type_system.ListClass:
                # Hax to make it work for now
                if not t.unions[0].types():
                    return compiler_types.ListMT.make_list(compiler_types.Int)
                elt_type = self._make_type(t.unions[0], to_initialize).get_instantiated()
                to_initialize.append(elt_type)
                return compiler_types.ListMT.make_list(elt_type)
            if t.cls is type_system.DictClass:
                key_type = self._make_type(t.unions[0], to_initialize).get_instantiated()
                value_type = self._make_type(t.unions[1], to_initialize).get_instantiated()
                to_initialize.append(key_type)
                to_initialize.append(value_type)
                return compiler_types.DictMT.make_dict(key_type, value_type)
            if t.cls is type_system.TupleClass:
                elt_types = [self._make_type(_u, to_initialize) for _u in t.unions]
                return compiler_types.TupleMT.make_tuple(elt_types)
            if t.cls is builtins.SetClass:
                assert len(t.unions) == 1
                elt_type = self._make_type(t.unions[0], to_initialize)
                return compiler_types.SetMT.make_set(elt_type)
            if t.cls is builtins.DequeClass:
                assert len(t.unions) == 1
                elt_type = self._make_type(t.unions[0], to_initialize)
                return compiler_types.DequeMT.make_deque(elt_type)
            if t is builtins.TypeClass:
                return compiler_types.TypeFunc
            if t.cls == type_system.GeneratorClass:
                return compiler_types.ListMT.make_list(self._make_type(t.unions[0], to_initialize))
            if t.cls == builtins.TypeClass:
                return compiler_types.Type

        if isinstance(t, type_system.UserFunction):
            assert not t.vararg
            assert not t.kwarg
            assert not t.is_generator
            assert len(t.unions) == len(t.arg_names) + 1
            assert t.rtn_idx == len(t.arg_names)
            r = self._make_type(t.unions[t.rtn_idx], to_initialize)
            args = [self._make_type(a, to_initialize).get_instantiated() for a in t.unions[:-1]]

            # return UnboxedFunctionMT(None, args, r)
            return compiler_types.CallableMT.make_callable(args, t.ndefault, r)

        if isinstance(t, type_system.InstanceMethod):
            if t._bind is None:
                # Not really sure how to handle this
                assert 0, "Double check this once we start running into it"
                f = self._make_type(t._f, to_initialize)
                assert isinstance(f, compiler_types.CallableMT)
                return compiler_types.CallableMT.make_callable(f.arg_types, f.rtn_type)
            else:
                if isinstance(t._f, type_system.UserFunction):
                    # this is cleaner:
                    # sub = self._make_type(t._f, to_initialize)
                    # return CallableMT.make_callable(sub.arg_types[1:], sub.rtn_type)
                    # but this allows polymorphism in the object
                    return compiler_types.CallableMT.make_callable([self._make_type(u, to_initialize) for u in t._f.unions[1:-1]], 0, self._make_type(t._f.unions[t._f.rtn_idx], to_initialize))
                elif isinstance(t._f, type_system.FixedFunction):
                    args, rtn = t._f.im_bind(t._bind)
                    rtn = self._make_type(rtn, to_initialize)
                    args = [self._make_type(a, to_initialize) for a in args]
                    return compiler_types.CallableMT.make_callable(args, 0, rtn)
                raise Exception(t._f)

        if isinstance(t, type_system.FixedFunction):
            # assert not t._defaults
            r = self._make_type(t._rtn, to_initialize)
            args = [self._make_type(a, to_initialize) for a in t._args]
            return compiler_types.CallableMT.make_callable(args, len(t._defaults), r)

        if isinstance(t, type_system.UserClassType):
            return self._make_class(t, to_initialize)

        if isinstance(t, type_system.InstanceType):
            cls = self._make_class(t.cls, to_initialize)
            return cls.get_instance()

        if isinstance(t, type_system.PolymorphicFunction):
            funcs = [self._make_type(f, to_initialize) for f in t._fs]
            return compiler_types.PolymorphicFunctionMT(funcs)

        if isinstance(t, type_system.SliceType):
            return compiler_types.Slice

        if isinstance(t, type_system.Module):
            return self._module_map[t]

        raise Exception(t)

