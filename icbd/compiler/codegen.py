import _ast
import collections
from cStringIO import StringIO
import re
import sys
import os

from icbd.util import ast_utils, cfa
from icbd.type_analyzer import builtins, type_checker, type_system
from . import closure_analyzer, usage_checker, phi_analyzer
from .type_conversion import InferredTypeOutput

from .code_emitter import CodeEmitter

from .compiler_types import (
        BINOP_MAP,
        COMPARE_MAP,
        COMPARE_REFLECTIONS,
        UserAttributeError,
        UserTypeError,
        AttributeAccessType,
        CantInstantiateException,
        format_float,
        eval_template,
        eval_ctemplate,
        Variable,
        UnboxedFunctionMT,
        UnboxedTupleMT,
        TupleMT,
        ClassMT,
        Type,
        TypeClass,
        FileClass,
        ObjectClass,
        File,
        ListMT,
        SetMT,
        DequeMT,
        Bool,
        Float,
        Str,
        Int,
        None_,
        TypeFunc,
        ClosureMT,
        StrConstant,
        _SpecialFuncMT,
        PolymorphicFunctionMT,
        UnboxedInstanceMethod,
        CallableMT,
        ModuleMT,
        UserModuleMT,
        DictMT,
        SliceMT,
        Slice,
        BUILTINS,
        BUILTIN_MODULES,

        STDLIB_TYPES,
    )

class CompileWalker(object):
    def __init__(self, parent_module, node_id, func_type, cg, em, sym_table, type_info, live_at_end, vars_to_raise, closure_results, my_closure_results, globals_, is_module):
        assert isinstance(my_closure_results, closure_analyzer.ClosureResults), my_closure_results

        self._parent_module = parent_module
        self._nid = node_id
        self._func_type = func_type
        self.cg = cg
        self.em = em
        self._st = sym_table
        self._type_info = type_info
        self._live_at_end = live_at_end
        self._vars_to_raise = vars_to_raise
        self._closure_results = closure_results
        self._cr = my_closure_results
        self._globals = globals_
        self._is_module = is_module

    def _find_and_apply_binop(self, _v1, _v2, *ops):
        _v1.incvref(self.em)
        _v2.incvref(self.em)

        # number of vrefs: (v1) 2, (v2) 2

        for op_name, is_reversed in ops:
            # 2, 2
            if is_reversed:
                v1, v2 = _v2, _v1
            else:
                v1, v2 = _v1, _v2

            # 2, 2
            try:
                f = v1.getattr(self.em, op_name, clsonly=True)
                # 1, 2
            except UserAttributeError:
                # 1, 2
                v1.incvref(self.em)
                continue

            # 1, 2
            if f.t.can_call([v2.t]):
                r = f.call(self.em, [v2])
                # 1, 1
            else:
                # 1, 2
                f.decvref(self.em)
                v1.incvref(self.em)
                # 2, 2
                continue

            # 1, 1
            v1.decvref(self.em)
            v2.decvref(self.em)
            # 0, 0
            return r

        # 2, 2
        # v1.decvref(self.em)
        # v1.decvref(self.em)
        # v2.decvref(self.em)
        # v2.decvref(self.em)
        raise Exception("Couldn't apply any of %s on %s, %s" % (ops, _v1.t, _v2.t))

    def _get(self, node):
        self.em.pl("; %s:" % getattr(node, "lineno", "??") + " " + ast_utils.format_node(node))
        self.em.indent(2)
        r = self._evaluate(node)
        self.em.pl("; end" + " " + ast_utils.format_node(node))
        self.em.indent(-2)

        # Skip generated nodes since they're not in the type inference (TODO are there cases that that could break?)
        # and skip several classes of things that can't always be converted
        if not hasattr(node, "not_real") and not isinstance(r.t, (UnboxedFunctionMT, _SpecialFuncMT, PolymorphicFunctionMT, UnboxedInstanceMethod, CallableMT, ModuleMT, ListMT.ListIteratorMT, DictMT.DictIteratorMT, ClassMT)):
            expected_type = self._type_info.get_expr_type(self.em, node)
            if not (expected_type is r.t or expected_type is r.t.get_instantiated()):
                assert r.t.can_convert_to(expected_type), (expected_type, r.t)
                r = r.convert_to(self.em, expected_type)

        return r

    def _evaluate(self, node):
        assert isinstance(node, _ast.AST), node

        if isinstance(node, _ast.Str):
            return Variable(StrConstant, (node.s,), 1, False)
        elif isinstance(node, _ast.Num):
            if isinstance(node.n, (int, long)):
                assert -2 ** 62 < node.n < 2 ** 62
                return Variable(Int, node.n, 1, True)
            assert isinstance(node.n, float)
            return Variable(Float, format_float(node.n), 1, True)
        elif isinstance(node, _ast.Name):
            n = node.id
            assert (n in self._cr.from_local) + (n in self._cr.from_closure) + (n in self._cr.from_global) + (n in self._cr.from_builtins) == 1, (n, self._cr.__dict__)

            should_be_in_st = (n in self._cr.from_local) or (not self._is_module and n in self._cr.used_in_nested)
            assert (n in self._st) == should_be_in_st, (n, n in self._st, should_be_in_st, self._cr.__dict__)

            if n in self._cr.from_global or n in self._cr.globals_:
                m = self.cg.modules[self._parent_module]
                m.incvref(None)
                return m.getattr(self.em, node.id)
            elif n in self._cr.from_local:
                v = self._st[node.id]
                v.incvref(self.em)
                return v
            elif n in self._cr.from_closure:
                assert node.id not in self._st, "%s is in both the closure and the local scope??" % (node.id,)
                assert node.id not in self._globals, "%s is in both the closure and globals??" % (node.id,)
                closure = self._st["__parent_closure__"]
                # TODO might still need to hit the global closure in this case
                v = closure.t.get(self.em, closure.v, node.id)
                return v
            elif n in self._cr.from_builtins:
                if n == "__name__":
                    m = self.cg.modules[self._parent_module]
                    return Variable(StrConstant, (m.t.module_name,), 1, False)
                v = BUILTINS[node.id].dup({})
                v.incvref(self.em)
                return v
            else:
                raise Exception("wtf, couldn't find %s" % node.id)

        elif isinstance(node, _ast.BinOp):
            v1 = self._get(node.left)
            v2 = self._get(node.right)

            op_name = BINOP_MAP[type(node.op)]
            rop_name = "__r" + op_name[2:]

            return self._find_and_apply_binop(v1, v2, (op_name, False), (rop_name, True))
        elif isinstance(node, _ast.Compare):
            if len(node.comparators) > 1:
                sub_compare = _ast.Compare(node.comparators[0], node.ops[1:], node.comparators[1:], not_real=True)
                twoarg_compare = _ast.Compare(node.left, node.ops[:1], node.comparators[:1], not_real=True)
                new_node = _ast.BoolOp(_ast.And(), [twoarg_compare, sub_compare], not_real=True, lineno=node.lineno, col_offset=node.col_offset)
                return self._evaluate(new_node)
            assert len(node.comparators) == 1
            # TODO use getattr
            v1 = self._get(node.left)
            v2 = self._get(node.comparators[0])

            if isinstance(node.ops[0], (_ast.Is, _ast.IsNot)):
                if v1.t.can_convert_to(v2.t):
                    v1 = v1.convert_to(self.em, v2.t)
                if v2.t.can_convert_to(v1.t):
                    v2 = v2.convert_to(self.em, v1.t)
                assert v1.t is v2.t, (v1.t, v2.t)

                r = '%' + self.em.mkname()
                self.em.pl("%s = icmp eq %s %s, %s" % (r, v1.t.llvm_type(), v1.v, v2.v))
                if isinstance(node.ops[0], _ast.IsNot):
                    r2 = '%' + self.em.mkname()
                    self.em.pl("%s = xor i1 %s, 1" % (r2, r))
                    r = r2
                v1.decvref(self.em)
                v2.decvref(self.em)
                return Variable(Bool, r, 1, False)

            op_type = type(node.ops[0])
            op_name = COMPARE_MAP[op_type]

            if op_type is _ast.In or op_type is _ast.NotIn:
                v1, v2 = v2, v1
            ops = [(op_name, False)]

            if op_type in COMPARE_REFLECTIONS:
                reverse_name = COMPARE_MAP[COMPARE_REFLECTIONS[op_type]]
                ops.append((reverse_name, True))
            return self._find_and_apply_binop(v1, v2, *ops)
        elif isinstance(node, _ast.Call):
            f = self._get(node.func)
            assert not node.keywords
            assert not node.starargs
            assert not node.kwargs
            args = [self._get(e) for e in node.args]

            expected_type = None
            if isinstance(node.func, _ast.Name) and node.func.id in ("deque", "list", "set", "dict"):
                expected_type = self._type_info.get_expr_type(self.em, node)
            r = f.call(self.em, args, expected_type=expected_type)
            return r
        elif isinstance(node, _ast.Attribute):
            v = self._get(node.value)

            # print v.t, self._type_info.get_expr_type(self.em, node.value)
            r = v.getattr(self.em, node.attr)
            return r
        elif isinstance(node, _ast.Subscript):
            v = self._get(node.value)
            s = self._get(node.slice)
            # v has one ref, and will have two taken off (getattr and then call)
            # v.incvref(self.em)
            f = v.getattr(self.em, "__getitem__", clsonly=True)
            r = f.call(self.em, [s])
            return r
        elif isinstance(node, _ast.Index):
            return self._get(node.value)
        elif isinstance(node, _ast.List):
            t = self._type_info.get_expr_type(self.em, node)
            assert isinstance(t, ListMT), t
            name = "%" + self.em.mkname()
            self.em.pl("%s = call %s %s()" % (name, t.llvm_type(), t.get_ctor_name()))
            r = Variable(t, name, 1, True)

            r.incvref(self.em) # for the getattr
            f = r.getattr(self.em, "append")
            for e in node.elts:
                arg = self._get(e)
                f.incvref(self.em) # for the next call
                f.call(self.em, [arg])
            f.decvref(self.em) # because we incvref'd it
            return r
        elif isinstance(node, _ast.Dict):
            t = self._type_info.get_expr_type(self.em, node)
            assert isinstance(t, DictMT), t
            name = '%' + self.em.mkname()
            self.em.pl("%s = call %s %s()" % (name, t.llvm_type(), t.get_ctor_name()))
            r = Variable(t, name, 1, True)

            r.incvref(self.em)
            f = r.getattr(self.em, "__setitem__", clsonly=True) # I guess it shouldn't matter if clsonly is set or not
            for i in xrange(len(node.keys)):
                k = self._get(node.keys[i])
                v = self._get(node.values[i])
                f.incvref(self.em) # for the next call
                f.call(self.em, [k, v])
            f.decvref(self.em) # because we incvref'd it
            return r
        elif isinstance(node, _ast.Tuple):
            elts = [self._get(e) for e in node.elts]
            t = UnboxedTupleMT([e.t for e in elts])
            return Variable(t, tuple(elts), 1, False)
            # t = TupleMT.get_tuple(self.em, [e.t.get_instantiated() for e in elts])
            # t_check = self._type_info.get_expr_type(self.em, node)
            # assert t is t_check
            # return t.alloc(elts)
        elif isinstance(node, _ast.Slice):
            lower = node.lower and self._get(node.lower)
            upper = node.upper and self._get(node.upper)
            step = node.step and self._get(node.step)
            return SliceMT.create(self.em, lower, upper, step)
        elif isinstance(node, _ast.UnaryOp):
            v = self._get(node.operand)
            if isinstance(node.op, _ast.Not):
                f = v.getattr(self.em, "__nonzero__", clsonly=True)
                r = f.call(self.em, [])
                assert r.t is Bool, "not sure what the behavior is in this case"
                n = "%" + self.em.mkname()
                self.em.pl("%s = xor i1 %s, 1" % (n, r.v))
                return Variable(Bool, n, 1, True)
            elif isinstance(node.op, _ast.USub):
                f = v.getattr(self.em, "__neg__", clsonly=True)
                r = f.call(self.em, [])
                return r
            else:
                raise Exception(node.op)
        elif isinstance(node, _ast.Lambda):
            return self._handle_function(node)
        elif isinstance(node, _ast.BoolOp):
            assert len(node.values) >= 2
            if isinstance(node.op, _ast.Or):
                lhs = self._get(node.values[0])

                if hasattr(node, 'not_real'):
                    rtn_type = lhs.t.get_instantiated()
                else:
                    rtn_type = self._type_info.get_expr_type(self.em, node)

                _lhs = lhs.convert_to(self.em, rtn_type)
                lhs = _lhs.split(self.em)
                _lhs.decvref(self.em)

                lhs.incvref(self.em) # for the getattr
                lhs_nonzero = lhs.getattr(self.em, "__nonzero__", clsonly=True)
                lhs_bool = lhs_nonzero.call(self.em, [])
                assert lhs_bool.t is Bool, lhs.t

                next = self.em.mkname(prefix="label")

                inputs = [(self.cg.blockname, lhs.v)]
                for elt in node.values[1:]:
                    iffalse = self.em.mkname(prefix="label")
                    self.em.pl("br i1 %s, label %%%s, label %%%s" % (lhs_bool.v, next, iffalse))

                    self.em.indent(-4)
                    self.em.pl("%s:" % iffalse)
                    self.em.indent(4)
                    self.cg.blockname = iffalse

                    d = lhs.t.decref_llvm(self.em, lhs.v)
                    if d:
                        self.em.pl(d + "; fell from conditional")

                    lhs = self._get(elt)
                    _lhs = lhs.convert_to(self.em, rtn_type)
                    lhs = _lhs.split(self.em)
                    _lhs.decvref(self.em)
                    if elt is not node.values[-1]:
                        lhs.incvref(self.em)
                        lhs_nonzero = lhs.getattr(self.em, "__nonzero__", clsonly=True)
                        lhs_bool = lhs_nonzero.call(self.em, [])
                        assert lhs_bool.t is Bool, lhs.t
                    else:
                        del lhs_bool, lhs_nonzero

                    inputs.append((self.cg.blockname, lhs.v))

                self.em.pl("br label %%%s" % next)
                rtn = '%' + self.em.mkname()
                self.em.indent(-4)
                self.em.pl("%s:" % next)
                self.em.indent(4)
                self.em.pl("%s = phi %s %s" % (rtn, rtn_type.llvm_type(), ", ".join(["[%s, %%%s]" % (vn, bn) for bn, vn in inputs])))
                self.cg.blockname = next
                return Variable(rtn_type, rtn, 1, True)
            elif isinstance(node.op, _ast.And):
                lhs = self._get(node.values[0])

                if hasattr(node, 'not_real'):
                    rtn_type = lhs.t.get_instantiated()
                else:
                    rtn_type = self._type_info.get_expr_type(self.em, node)

                _lhs = lhs.convert_to(self.em, rtn_type)
                lhs = _lhs.split(self.em)
                _lhs.decvref(self.em)

                lhs.incvref(self.em) # for the getattr
                lhs_nonzero = lhs.getattr(self.em, "__nonzero__", clsonly=True)
                lhs_bool = lhs_nonzero.call(self.em, [])
                assert lhs_bool.t is Bool, lhs.t

                next = self.em.mkname(prefix="label")

                # TODO this is wrong
                rtn_type = lhs.t.get_instantiated()

                inputs = [(self.cg.blockname, lhs.v)]
                for elt in node.values[1:]:
                    iftrue = self.em.mkname(prefix="label")
                    self.em.pl("br i1 %s, label %%%s, label %%%s" % (lhs_bool.v, iftrue, next))

                    self.em.indent(-4)
                    self.em.pl("%s:" % iftrue)
                    self.em.indent(4)
                    self.cg.blockname = iftrue

                    d = lhs.t.decref_llvm(self.em, lhs.v)
                    if d:
                        self.em.pl(d + "; fell from conditional")

                    lhs = self._get(elt)
                    _lhs = lhs.convert_to(self.em, rtn_type)
                    lhs = _lhs.split(self.em)
                    _lhs.decvref(self.em)
                    if elt is not node.values[-1]:
                        lhs.incvref(self.em)
                        lhs_nonzero = lhs.getattr(self.em, "__nonzero__", clsonly=True)
                        lhs_bool = lhs_nonzero.call(self.em, [])
                        assert lhs_bool.t is Bool, lhs.t
                    else:
                        del lhs_bool, lhs_nonzero


                    inputs.append((self.cg.blockname, lhs.v))

                self.em.pl("br label %%%s" % next)
                rtn = '%' + self.em.mkname()
                self.em.indent(-4)
                self.em.pl("%s:" % next)
                self.em.indent(4)
                self.em.pl("%s = phi %s %s" % (rtn, rtn_type.llvm_type(), ", ".join(["[%s, %%%s]" % (vn, bn) for bn, vn in inputs])))
                self.cg.blockname = next
                return Variable(rtn_type, rtn, 1, True)
            else:
                raise Exception(node.op)
        elif isinstance(node, (_ast.ListComp, _ast.GeneratorExp)):
            list_type = self._type_info.get_expr_type(self.em, node)
            assert isinstance(list_type, ListMT)

            assert len(node.generators) == 1
            [g] = node.generators
            assert not g.ifs

            set_names = [n.id for n in ast_utils.find_names(g.target) if isinstance(n.ctx, _ast.Store)]
            inner_set_names = [n.id for n in ast_utils.find_names(node.elt) if isinstance(n.ctx, _ast.Store)]
            set_names += inner_set_names

            if isinstance(g.iter, _ast.Call) and isinstance(g.iter.func, _ast.Name) and g.iter.func.id in ("range", "xrange"):
                assert len(g.iter.args) == 1
                assert not g.iter.starargs
                assert not g.iter.kwargs
                assert not g.iter.keywords
                end = self._get(g.iter.args[0])
                assert end.t is Int
                is_xrange = True
            else:
                gen = self._get(g.iter)
                iter_func = gen.getattr(self.em, "__iter__", clsonly=True)
                iter = iter_func.call(self.em, [])
                is_xrange = False

            rtn = '%' + self.em.mkname()
            iter_name = '%' + self.em.mkname()
            next_iter = '%' + self.em.mkname()

            start_label = self.cg.blockname
            check_label = self.em.mkname(prefix="label")
            loop_label = self.em.mkname(prefix="label")
            done_label = self.em.mkname(prefix="label")
            loop_label_placeholder = self.em.get_placeholder()

            self.em.pl("%s = call %s %s()" % (rtn, list_type.llvm_type(), list_type.get_ctor_name()))
            clear_names = []
            changed_names = {}
            for n in set_names:
                if n in self._globals:
                    continue
                if self._is_module and self.cg.modules[self._parent_module].t.has(n):
                    continue
                if n not in self._st:
                    clear_names.append(n)
                    continue

                v = self._st[n]
                v2 = v.convert_to(self.em, v.t.get_instantiated())
                assert v2.nrefs == 1
                if not v2.marked:
                    self.em.pl(v2.t.incref_llvm(self.em, v2.v) + " ; marking")
                old_name = v2.v
                new_name = "%" + self.em.mkname()
                changed_names[n] = (old_name, new_name)
                v2.v = new_name
                self._st[n] = v2
            self.em.pl("br label %%%s" % check_label)

            self.em.indent(-4)
            self.em.pl("%s:" % check_label)
            self.cg.blockname = check_label
            phi_placeholder = self.em.get_placeholder()
            self.em.pl(phi_placeholder)
            self.em.indent(4)

            if is_xrange:
                done_name = '%' + self.em.mkname()
                self.em.pl("%s = phi i64 [0, %%%s], [%s, %%%s]" % (iter_name, start_label, next_iter, loop_label_placeholder))
                self.em.pl("%s = icmp sge i64 %s, %s" % (done_name, iter_name, end.v))
                self.em.pl("br i1 %s, label %%%s, label %%%s" % (done_name, done_label, loop_label))
            else:
                iter.incvref(self.em)
                has_next_func = iter.getattr(self.em, "hasnext", clsonly=True)
                has_next = has_next_func.call(self.em, [])
                assert isinstance(has_next, Variable)
                assert has_next.t is Bool
                self.em.pl("br i1 %s, label %%%s, label %%%s" % (has_next.v, loop_label, done_label))

            self.em.indent(-4)
            self.em.pl("%s:" % loop_label)
            self.cg.blockname = loop_label
            self.em.indent(4)

            # TODO do I need to use the cache here?  is this right?
            saved_syms = dict([(sym, v.dup({})) for sym, v in self._st.iteritems()])
            if is_xrange:
                self._set(g.target, Variable(Int, iter_name, 1, True))
            else:
                iter.incvref(self.em)
                next_func = iter.getattr(self.em, "next", clsonly=True)
                next = next_func.call(self.em, [])
                self._set(g.target, next)
            elt = self._get(node.elt)
            for k in clear_names:
                if k not in self._st:
                    assert k in inner_set_names
                    continue
                v = self._st.pop(k)
                v.decvref(self.em, "clearing")

            self.em.register_replacement(loop_label_placeholder, self.cg.blockname)
            elt = elt.convert_to(self.em, list_type.elt_type)
            assert elt.t is list_type.elt_type, (elt.t, list_type.elt_type)
            rtn_l = Variable(list_type, rtn, 1, False)
            func = rtn_l.getattr(self.em, "append")
            func.call(self.em, [elt])
            if is_xrange:
                self.em.pl("%s = add i64 %s, 1" % (next_iter, iter_name))

            assert set(self._st) == set(saved_syms), "This should have been enforced above"
            phi_code = ''
            for k, v in self._st.items():
                v2 = saved_syms[k]
                if not v.equiv(v2):
                    if v.t.can_convert_to(v2.t):
                        v = v.convert_to(self.em, v2.t)
                    v = v.split(self.em)

                    assert v.nrefs == 1
                    assert v.marked

                    assert v.t == v2.t, (v.t, v2.t)

                    old_name, new_name = changed_names.pop(k)
                    assert v2.v == new_name
                    phi_code += '    %s = phi %s [%s, %%%s], [%s, %%%s]' % (new_name, v.t.llvm_type(), old_name, start_label, v.v, self.cg.blockname)
                    self._set(k, Variable(v.t, new_name, 1, True))
            # They should have all been updated:
            assert not changed_names
            self.em.register_replacement(phi_placeholder, phi_code)
            self.em.pl("br label %%%s" % (check_label,))

            self.em.indent(-4)
            self.em.pl("%s:" % done_label)
            self.cg.blockname = done_label
            self.em.indent(4)
            if not is_xrange:
                iter.decvref(self.em, "end of listcomp")

            return Variable(list_type, rtn, 1, True)
        elif isinstance(node, _ast.IfExp):
            test = self._get(node.test)
            test2 = test.getattr(self.em, "__nonzero__", clsonly=True).call(self.em, [])
            assert test2.t is Bool

            true_label = self.em.mkname(prefix="label")
            false_label = self.em.mkname(prefix="label")
            end_label = self.em.mkname(prefix="label")
            self.em.pl("br i1 %s, label %%%s, label %%%s" % (test2.v, true_label, false_label))

            resulting_type = self._type_info.get_expr_type(self.em, node)

            self.em.indent(-4)
            self.em.pl("%s:" % true_label)
            self.cg.blockname = true_label
            self.em.indent(4)
            v1 = self._get(node.body).convert_to(self.em, resulting_type)
            if v1.nrefs != 1 or not v1.marked:
                _v1 = v1.split(self.em)
                v1.decvref(self.em)
                v1 = _v1
            true_end = self.cg.blockname
            self.em.pl("br label %%%s" % (end_label,))

            self.em.indent(-4)
            self.em.pl("%s:" % false_label)
            self.cg.blockname = false_label
            self.em.indent(4)
            v2 = self._get(node.orelse).convert_to(self.em, resulting_type)
            if v2.nrefs != 1 or not v2.marked:
                _v2 = v2.split(self.em)
                v2.decvref(self.em)
                v2 = _v2
            false_end = self.cg.blockname
            self.em.pl("br label %%%s" % (end_label,))

            assert v1.t is resulting_type
            assert v2.t is resulting_type
            # Need to obey the phi discipline:
            assert v1.nrefs == v2.nrefs
            assert v1.marked == v2.marked
            t = v1.t

            self.em.indent(-4)
            self.em.pl("%s:" % end_label)
            self.cg.blockname = end_label
            self.em.indent(4)

            r = '%' + self.em.mkname()
            self.em.pl("%s = phi %s [%s, %%%s], [%s, %%%s]" % (r, t.llvm_type(), v1.v, true_end, v2.v, false_end))
            return Variable(t, r, 1, v1.marked)
        elif isinstance(node, cfa.HasNext):
            it = self._get(node.iter)
            f = it.getattr(self.em, "hasnext", clsonly=True)
            return f.call(self.em, [])
        else:
            raise Exception(node)
        raise Exception("didn't return for %s" % node)

    def _set(self, t, val):
        # v is a Variable with one vref that this _set should consume
        # (can't actually check it because it might have added other refs
        # ex by adding it to the symbol table)

        if isinstance(t, _ast.Name):
            self._set(t.id, val)
        elif isinstance(t, _ast.Subscript):
            v = self._get(t.value)
            s = self._get(t.slice)
            f = v.getattr(self.em, "__setitem__", clsonly=True)
            f.call(self.em, [s, val])
        elif isinstance(t, _ast.Attribute):
            v = self._get(t.value)
            v.setattr(self.em, t.attr, val)
        elif isinstance(t, str):
            self._set_name(t, val)
        elif isinstance(t, (_ast.Tuple, _ast.List)):
            if isinstance(val.t, UnboxedTupleMT):
                assert len(t.elts) == len(val.v)
                for i in xrange(len(val.v)):
                    e = val.v[i]
                    e.incvref(self.em)
                    self._set(t.elts[i], e)
                val.decvref(self.em)
            elif isinstance(val.t, (TupleMT, ListMT)):
                if isinstance(val.t, TupleMT):
                    assert len(t.elts) == len(val.t.elt_types)
                else:
                    val.incvref(self.em)
                    r = val.getattr(self.em, "__len__", clsonly=True).call(self.em, [])
                    self.em.pl("call void @check_unpacking_length(i64 %d, i64 %s)" % (len(t.elts), r.v))

                for i in xrange(len(t.elts)):
                    val.incvref(self.em)
                    r = val.getattr(self.em, "__getitem__", clsonly=True).call(self.em, [Variable(Int, i, 1, True)])
                    self._set(t.elts[i], r)
                val.decvref(self.em)
            else:
                raise Exception(val.t)
        else:
            raise Exception(t)

    def _set_name(self, name, v):
        assert isinstance(name, str)
        assert isinstance(v, Variable)

        in_closure = (name in self._cr.used_in_nested) or (name in self._cr.functions) or (name in self._cr.classes) or (name in self._cr.modules)

        assert (name in self._cr.globals_) + (name in self._cr.local_only) + in_closure == 1, (name, self._cr.globals_, self._cr.local_only, in_closure)

        if name in self._globals:
            m = self.cg.modules[self._parent_module]
            m.incvref(self.em)
            m.setattr(self.em, name, v)
            return

        # Scopes read their closure by putting the items in the local sym table,
        # except for the global closure since all its items are mutable, except
        # for the static ones
        if in_closure:
            if self._is_module:
                scope = self.cg.modules[self._parent_module]

                # The closure_analyzer will determine which variables are safe to assume
                # as being immutable by other scopes; currently just "__foriter_" variables
                put_in_st = name in self._cr.local_only
            else:
                scope = self._st["__closure__"]
                # closure variables can't be modified by inner scopes
                put_in_st = True
            assert scope

            v.incvref(self.em)
            scope.t.set(self.em, scope.v, name, v)
            # We could put it into the symbol table if it's a constant,
            # but that optimization wouldn't do anything since getting
            # a constant from the scope is a no-op
        else:
            put_in_st = True

        if put_in_st:
            if name in self._st:
                self._st[name].decvref(self.em)
            self._st[name] = v
        else:
            v.decvref(self.em)

    def _close_block(self):
        done = []
        for n, v in self._st.iteritems():
            if n not in self._live_at_end:
                # self.em.pl("; %s not live" % (n))
                v.decvref(self.em)
                done.append(n)
            else:
                # self.em.pl("; %s live" % (n))
                if n in self._vars_to_raise:
                    # Have to assume that all variables are owned at the end of a block; could get around this with a more complicated analysis phase (or maybe just remove them in a post-processing phase)
                    # similarly for raising
                    v2 = v.convert_to(self.em, self._vars_to_raise[n])
                    if v2.nrefs > 1 or not v2.marked:
                        v3 = v2.split(self.em)
                        v2.decvref(self.em)
                        v2 = v3
                    self._st[n] = v2

        for n in done:
            self._st.pop(n)

    def pre_global(self, node):
        return ()

    def pre_pass(self, node):
        return ()

    def pre_expr(self, node):
        v = self._get(node.value)
        v.decvref(self.em)
        return ()

    def pre_branch(self, node):
        v = self._get(node.test)
        v2 = v.getattr(self.em, "__nonzero__", clsonly=True).call(self.em, [])

        assert node.true_block
        assert node.false_block
        self._close_block()

        if str(v2.v) == "0" or node.true_block == node.false_block:
            assert 0, "untested"
            self.em.pl("br label %%block%d" % (node.false_block,))
        elif str(v2.v) == "1":
            assert 0, "untested"
            self.em.pl("br label %%block%d" % (node.true_block,))
        else:
            self.em.pl("br i1 %s, label %%block%d, label %%block%d" % (v2.v, node.true_block, node.false_block))

        return ()

    def pre_jump(self, node):
        self._close_block()
        self.em.pl("br label %%block%d" % (node.block_id,))

        return ()

    def pre_import(self, node):
        for n in node.names:
            assert not n.asname
            assert '.' not in n.name
            m = self.cg.import_module(self.em, n.name)
            self._set(n.name, m)
        return ()

    def pre_importfrom(self, node):
        m = self.cg.import_module(self.em, node.module)
        for n in node.names:
            m.incvref(self.em)
            v = m.getattr(self.em, n.name)
            local_name = n.asname or n.name
            assert '.' not in n.name
            assert '.' not in local_name
            self._set(local_name, v)
        return ()

    def pre_augassign(self, node):
        t = self._get(node.target)
        v = self._get(node.value)

        op_name = BINOP_MAP[type(node.op)]
        iop_name = "__i" + op_name[2:]
        rop_name = "__r" + op_name[2:]
        r = self._find_and_apply_binop(t, v, (iop_name, False), (op_name, False), (rop_name, True))
        self._set(node.target, r)
        return ()

    def pre_assign(self, node):
        val = self._get(node.value)
        for t in node.targets:
            # Each _set will consume one vref
            val.incvref(self.em)
            self._set(t, val)
        # consume the vref from _get
        val.decvref(self.em)
        return ()

    def pre_print(self, node):
        for i, elt in enumerate(node.values):
            v = self._get(elt)
            assert isinstance(v, Variable), elt
            v = v.getattr(self.em, "__str__", clsonly=True).call(self.em, [])
            assert v.t is Str

            self.em.pl("call void @file_write(%%file* @sys_stdout, %%string* %s)" % (v.v,))
            if i < len(node.values) - 1 or not node.nl:
                self.em.pl("call void @print_space_if_necessary(%%string* %s)" % (v.v,))
            v.decvref(self.em)

        if node.nl:
            self.em.pl("call void @file_write(%%file* @sys_stdout, %%string* @str_newline)" % ())

        return ()

    def _handle_function(self, node):
        assert isinstance(node, (_ast.FunctionDef, _ast.Lambda))
        assert not node.args.vararg
        assert not node.args.kwarg

        if self._type_info.is_dead_function(node):
            print "Not compiling %s since it's dead" % (node.name,)
            return None

        try:
            f_type = self._type_info.get_expr_type(self.em, node)
        except Exception:
            print "Couldn't get the type of", node.name
            raise
        assert isinstance(f_type, CallableMT)

        defaults = []
        for i, d in enumerate(node.args.defaults):
            arg_idx = len(f_type.arg_types) - len(node.args.defaults) + i
            d = self._get(d)
            # d = d.convert_to(self.em, f_type.arg_types[arg_idx])
            defaults.append(d)
        # our ref to the defaults will get consumed when creating the unboxedfunctionmt variable

        name = "@" + self.em.mkname(prefix="_%s_" % (getattr(node, "name", "lambda"),))
        # Pass the closure created in this function if there was one,
        # otherwise directly pass the parent closure.
        closure = self._st.get("__closure__") or self._st.get("__parent_closure__")
        closure_type = closure.t if closure else None
        takes_closure = self._closure_results[self._parent_module][node].takes_closure

        unboxed = UnboxedFunctionMT(name, closure_type if takes_closure else None, f_type.arg_types, f_type.rtn_type, ndefaults=len(defaults))
        unboxed.initialize(self.em, "write")
        self.cg.queue_function(node, self._parent_module, unboxed, name, closure_type)
        return Variable(unboxed, (name, defaults, closure if takes_closure else None), 1, False)

    def pre_functiondef(self, node):
        var = self._handle_function(node)
        if var is not None:
            self._set(node.name, var)
        return ()

    def pre_classdef(self, node):
        assert len(node.bases) == 1

        base = self._get(node.bases[0])
        assert isinstance(base.t, ClassMT), base.t

        cls_type = self._type_info.get_expr_type(self.em, node)
        assert isinstance(cls_type, ClassMT)
        assert cls_type.base == base.t
        for fd in node.body:
            if isinstance(fd, _ast.Pass):
                continue

            assert isinstance(fd, _ast.FunctionDef), "Dont support %s yet" % (fd,)
            func = self._handle_function(fd)
            if func is not None:
                cls_type.set_clsattr_value(fd.name, func, em=self.em)
        for name, val in cls_type._clsattr_types.iteritems():
            assert val is not None, "should have %s for %s, but don't?" % (name, node.name)
        self._set(node.name, Variable(cls_type, (), 1, False))
        return ()

    def pre_return(self, node):
        rtn_type = self._func_type.rtn_type

        v = Variable(None_, "null", 1, False) if node.value is None else self._get(node.value)
        v = v.convert_to(self.em, rtn_type)
        if v.marked:
            r = v
        else:
            r = v.split(self.em)
            v.decvref(self.em)

        self._close_block()

        if rtn_type is None_:
            self.em.pl("ret void")
        else:
            # This is the ref contract:
            assert r.nrefs == 1
            assert r.marked
            self.em.pl("ret %s %s" % (r.t.llvm_type(), r.v))
        return ()

    def pre_assert(self, node):
        v = self._get(node.test)
        v2 = v.getattr(self.em, "__nonzero__", clsonly=True).call(self.em, [])
        assert v2.t is Bool
        self.em.pl("call void @assert_(i1 %s)" % v2.v)
        return ()

class CodeGenerator(object):
    def __init__(self, typepath, pythonpath):
        self._compile_queue = None
        self._typepath = typepath
        self._pythonpath = pythonpath
        self.modules = None # maps ast node -> usermodulemt object
        self._loaded_modules = None # maps fn -> usermodulemt object
        self._module_filenames = None # maps ast module -> fn
        self._closure_results = None
        self.type_info = None

    def queue_function(self, node, parent_module, f_type, name, parent_closure_type):
        self._compile_queue.append((node, parent_module, f_type, name, parent_closure_type))

    def import_module(self, em, name=None, fn=None):
        assert not (name and fn)
        assert name or fn
        if name and name in BUILTIN_MODULES:
            return BUILTIN_MODULES[name].dup({})

        if name:
            assert '.' not in name
            fns = [os.path.join(dirname, name + ".py") for dirname in self._pythonpath]
        else:
            fns = [fn]
            assert fn.endswith(".py")
            name = os.path.basename(fn)[:-3]

        assert name
        for fn in fns:
            if os.path.exists(fn):
                if fn not in self._loaded_modules:
                    source = open(fn).read()
                    node = ast_utils.parse(source, fn)

                    self._load_module(em, node, name, fn)

                rtn = self._loaded_modules[fn]
                rtn.t.load(em)
                return rtn.dup({})

        raise Exception("don't know how to import '%s'" % name)

    def _load_module(self, em, node, name, fn):
        self._closure_results[node] = closure_analyzer.analyze_closures(node)
        ts_module = self.type_info.get_module(fn)
        module = UserModuleMT.make(em, name, node, fn, self._closure_results[node][node], ts_module, self.type_info)
        self.modules[node] = self._loaded_modules[fn] = module
        self._module_filenames[node] = fn
        self.queue_function(node, node, UnboxedFunctionMT(self, None, [], None_), "@%s_global" % name, None)
        self.type_info.map_module(ts_module, module.t)

        module.t.load_modules(em, self, self._closure_results[node][node], ts_module, self.type_info)

    def compile(self, main_module, fn, llvm_f, c_f, deps_f):
        assert isinstance(main_module, _ast.Module)
        self.compile = None # Hacky way of saying+enforcing that this function should only be called once

        # type_info = MockTypeOutput()
        self.type_info = InferredTypeOutput(fn, self._typepath + self._pythonpath)

        llvm_body = StringIO()
        llvm_head = StringIO()
        llvm_tail = StringIO()
        c_head = StringIO()
        c_tail = StringIO()
        root_emitter = CodeEmitter((llvm_head, llvm_tail, c_head, c_tail))

        llvm_head.write(eval_template("prologue", root_emitter, {}))
        c_head.write(eval_ctemplate("cheader", root_emitter, {}))

        # Need to have basic lists that the runtime deals with
        ListMT.make_list(Str).initialize(root_emitter, "write")
        ListMT.make_list(Int).initialize(root_emitter, "write")
        TupleMT.make_tuple((Str, Str)).initialize(root_emitter, "write")
        TupleMT.make_tuple((Int, Int)).initialize(root_emitter, "write")
        BUILTINS["divmod"] = Variable(UnboxedFunctionMT(None, None, [Int, Int], TupleMT.make_tuple([Int, Int])), ("@divmod", [], None), 1, False)
        FileClass.set_clsattr_value("readlines", Variable(UnboxedFunctionMT(None, None, [File], ListMT.make_list(Str)), ("@file_readlines", [], None), 1, False), _init=True)

        assert "range" not in BUILTINS
        # TODO xrange shouldnt do this
        BUILTINS["xrange"] = BUILTINS["range"] = Variable(UnboxedFunctionMT(None, None, [Int], ListMT.make_list(Int)), ("@range", [], None), 1, False)

        assert "argv" not in BUILTIN_MODULES['sys'].t._attrs
        BUILTIN_MODULES['sys'].t._attrs['argv'] = Variable(ListMT.make_list(Str), "@sys_argv", 1, False)

        self._compile_queue = collections.deque()

        self._loaded_modules = {}
        self._module_filenames = {}
        self.modules = {}
        self._closure_results = {}

        TypeClass.initialize(root_emitter, "write")

        for t in STDLIB_TYPES:
            t.initialize(root_emitter, "write")

        self._load_module(root_emitter, main_module, "__main__", fn)

        llvm_tail.write(eval_template("epilogue", root_emitter, {
        }))

        def is_inlined_constant(sym, cr):
            return sym in cr.functions or sym in cr.classes or sym in cr.modules

        while self._compile_queue:
            emitter = CodeEmitter(root_emitter)

            node, parent_module, f_type, f_name, parent_closure_type = self._compile_queue.popleft()
            # print "\ncompiling", getattr(node, "name", "<module>"), parent_closure_type
            cr = self._closure_results[parent_module][node]

            live_inputs, live_outputs, liveness_warnings = usage_checker.get_liveness(node, fn=self.modules[parent_module].t.fn)
            # for (l, c), s in liveness_warnings:
                # print "WARNING at %s:%s: %s" % (fn, l, s)
            # defined_inputs, defined_outputs, defined_errs = defined_checker.get_definedness(node)
            # assert not defined_errs, defined_errs
            required_phis = phi_analyzer.determine_phi_instructions(node)

            globals_ = []
            if isinstance(node, _ast.FunctionDef):
                globals_ = ast_utils.find_global_vars(node)

            body = node.body
            if isinstance(node, _ast.Lambda):
                body = [_ast.Return(node.body, lineno=node.lineno, col_offset=node.col_offset, not_real=True)]
            cfg = cfa.cfa(node, body)
            # cfg.show()
            # Need to enforce that for every transition, we can determine at some point what transition was made.
            # ie on the way out of a block we either need to know where we're going, so we can prepare,
            # or we need to know once we got into a block where we came from, so we can clean up.
            for nid in cfg.blocks:
                if nid != cfg.end and len(cfg.connects_to[nid]) > 1:
                    for next_id in cfg.connects_to[nid]:
                        assert len(cfg.connects_from[next_id]) == 1, (nid, next_id)
                if nid != cfg.start and len(cfg.connects_from.get(nid, [])) > 1:
                    for prev_id in cfg.connects_from[nid]:
                        assert len(cfg.connects_to[prev_id]) == 1, (prev_id, nid)

            start_sym_table = {}
            defined_from_args = set()
            if isinstance(node, (_ast.FunctionDef, _ast.Lambda)):
                assert not node.args.vararg
                assert not node.args.kwarg
                for (i, a) in enumerate(node.args.args):
                    # This is the function arg contract: mark is not passed
                    raw_arg_name = "__arg%d" % (i,)
                    start_sym_table[raw_arg_name] = Variable(f_type.arg_types[i], "%" + raw_arg_name, 1, False)
                    cr.from_local.add(raw_arg_name)

                    for n in ast_utils.find_names(a):
                        defined_from_args.add(n.id)

            """
            Doing a bunch of closure-results checking:
            """

            nonlocal = set()
            for var in live_outputs[(node, cfg.start)]:
                if var in defined_from_args:
                    continue
                else:
                    assert var in cr.from_closure or var in cr.from_global or var in cr.from_builtins or var in cr.globals_, var
                    nonlocal.add(var)

            # Filter out range/xrange since the closure analyzer will report them but the compiler won't see them
            # also whitelist None since it's hard to find all occurrences of it (because it can implicitly be referenced)
            # also whitelist True and False, since the cfa pass can remove them
            whitelist = ["range", "xrange", "None", "True", "False"]
            if isinstance(node, _ast.Module):
                assert not nonlocal.difference(whitelist).difference(cr.from_builtins)
            else:
                pass
                # I don't think this is correct because the usage might not make it to being live...
                # assert nonlocal.difference(whitelist) == set(cr.from_closure).union(cr.from_global).union(cr.from_builtins).difference(whitelist), (nonlocal, cr.from_closure, cr.from_global, cr.from_builtins)

            for n in nonlocal:
                for nid in cfg.blocks:
                    live_inputs[(node, nid)].pop(n, None)
                    live_outputs[(node, nid)].pop(n, None)

            for name in cr.from_closure:
                assert parent_closure_type
                if cr.takes_closure:
                    assert parent_closure_type.has(name, include_parents=True), name
                else:
                    assert parent_closure_type.has_constant(name, include_parents=True), name
            for name in cr.from_builtins:
                assert name in BUILTINS or name == "__name__", name
            if not isinstance(node, _ast.Module):
                for name in list(cr.from_global) + list(cr.globals_):
                    assert self.modules[parent_module].t.has(name), name

            arg_str = ", ".join("%s %s" % (f_type.arg_types[i].llvm_type(), "%%__arg%d" % (i,)) for i in xrange(len(f_type.arg_types)))
            if isinstance(node, (_ast.FunctionDef, _ast.Lambda)):
                params = ""

                if cr.takes_closure:
                    arg_str = "%s %%__parent_closure__, " % (parent_closure_type.llvm_type(),) + arg_str
                    if arg_str.endswith(", "):
                        arg_str = arg_str[:-2]

                if parent_closure_type:
                    start_sym_table['__parent_closure__'] = Variable(parent_closure_type, "%__parent_closure__", 1, False)
                    for nid in cfg.blocks:
                        # Need to set this as live at the end of the block, so that we don't gc it
                        if nid != cfg.end and nid not in cfg.connects_from.get(cfg.end, []):
                            live_inputs[(node, nid)]['__parent_closure__'] = usage_checker.LIVE
                        # At some point we needed this; not sure if we still do:
                        if nid != cfg.start and nid != cfg.end:
                            live_outputs[(node, nid)]['__parent_closure__'] = usage_checker.LIVE
            else:
                params = ""
                arg_str = ""
                assert parent_closure_type is None

            rtn_type = f_type.rtn_type.llvm_type() if f_type.rtn_type is not None_ else "void"
            emitter.pl("define %s %s %s(%s)" % (params, rtn_type, f_name, arg_str))
            emitter.pl("{")

            # This is necessary if the start block is not the first one iterated over
            # which is possible becaues cfg.blocks is a dict and doesnt define the iteration order
            emitter.pl("func_start:")
            emitter.pl("    br label %%block%d" % (cfg.start,))
            emitter.pl()

            sym_tables = {}
            end_blocks = {} # maps node_id to the name of the final generated block in that original block

            # Have to go through them in roughly program order;
            # the main requirement is that for any block evaluation,
            # one of that block's predecessors has already been evaluated
            for node_id in sorted(cfg.blocks.keys()):
                # print >>sys.stderr, "compiling block", node_id

                body = cfg.blocks[node_id]

                if node_id == cfg.end:
                    assert not body
                    if f_type.rtn_type is None_:
                        emitter.pl("block%d:" % node_id)
                        emitter.indent(4)
                        emitter.pl("ret void")
                        emitter.indent(-4)
                    continue
                else:
                    emitter.pl("block%d:" % node_id)
                    emitter.indent(4)
                    if node_id == cfg.start:
                        initial_sym_table = start_sym_table

                        if isinstance(node, (_ast.FunctionDef, _ast.Lambda)):
                            body = [_ast.Assign(targets=[node.args.args[i]], value=_ast.Name(ctx=_ast.Load(), id="__arg%d" % (i,), not_real=True, lineno=node.lineno, col_offset=node.col_offset), not_real=True, lineno=node.lineno, col_offset=node.col_offset) for i in xrange(len(node.args.args))] + body
                            for a in node.args.args:
                                for n in ast_utils.find_names(a):
                                    assert isinstance(n.ctx, (_ast.Param, _ast.Store)), (n.ctx, n.id, n.lineno)
                                    assert n.id not in cr.globals_
                                    assert n.id not in cr.from_global
                                    assert n.id not in cr.from_closure
                                    assert n.id not in cr.from_builtins
                                    cr.from_local.add(n.id)

                        if isinstance(node, _ast.Module):
                            assert parent_closure_type is None
                        elif cr.has_data():
                            # print "allocating closure for", node.name
                            parent_closure = None
                            if cr.takes_closure:
                                # TODO shouldn't always use the parent closure just because it's available;
                                # the closure analyzer should determine when lookups pass through this scope
                                # to the parent one
                                assert "__parent_closure__" in start_sym_table
                                parent_closure = Variable(parent_closure_type, "%__parent_closure__", 1, False)

                            parent_obj = bool(parent_closure and parent_closure.v)
                            closure = ClosureMT.create(emitter, node, parent_closure_type, parent_obj, cr, self.type_info)
                            initial_sym_table["__closure__"] = closure.alloc(emitter, parent_closure if parent_obj else None)

                            # this would be significantly easier if we made sure that every exit path went through the exit node
                            # ie and just had a return phi there
                            for nid in cfg.blocks:
                                if nid != cfg.end and nid not in cfg.connects_from.get(cfg.end, []):
                                    live_inputs[(node, nid)]['__closure__'] = usage_checker.LIVE
                                if nid != cfg.start and nid != cfg.end:
                                    live_outputs[(node, nid)]['__closure__'] = usage_checker.LIVE
                    else:
                        if len(cfg.connects_from[node_id]) == 1:
                            assert not required_phis[node_id], (node_id, cfg.connects_from[node_id], required_phis[node_id])

                        initial_sym_table = {}

                        min_prev_id = min(cfg.connects_from[node_id])
                        assert min_prev_id in sym_tables

                        dup_cache = {}

                        # Different approaches to one-to-multi and multi-to-one links
                        if len(cfg.connects_from[node_id]) == 1:
                            # On one-to-multi, the predecessor can't clean out its dead symbols,
                            # so have to add those to the successors
                            starting_syms = sym_tables[min_prev_id].keys()
                        else:
                            # On multi-to-one, the successor can't know what dead variables there might be,
                            # so we rely on the predecessor to clean those up
                            starting_syms = live_outputs[(node, node_id)].keys()

                        for sym in starting_syms:
                            if sym in cr.from_global or sym in cr.globals_:
                                continue
                            elif sym in required_phis[node_id]:
                                types = []

                                def get_var_location(block):
                                    if block in sym_tables:
                                        types.append(sym_tables[block][sym].t)
                                        return sym_tables[block][sym].v
                                    return "#end_loc#%s#%d#" % (sym, block)

                                var = '%' + root_emitter.mkname(prefix="_%s_%d_" % (sym, node_id))
                                args = ', '.join('[ %s, #end_block#%d# ]' % (get_var_location(prev_id), prev_id) for prev_id in cfg.connects_from[node_id])
                                assert types # This is where we use the fact that we go through the blocks in program order
                                assert all(t == types[0] for t in types), "'%s' is live and has multiple possible types: %s (should be %s)" % (sym, types, self.type_info.get_block_starting_type(self, node, node_id, sym))
                                t = types[0]

                                emitter.pl("%s = phi %s %s" % (var, t.llvm_type(), args))
                                # This is the phi contract: mark is passed
                                initial_sym_table[sym] = Variable(t, var, 1, True)
                            else: # not a required phi

                                # Since we are only looking at live variables, and we are requiring
                                # that a live variable is defined on any possible path to this point,
                                # we can just pick any of the existing sym tables and it must have it
                                initial_sym_table[sym] = sym_tables[min_prev_id][sym].dup(dup_cache)


                    # print map(ast_utils.format_node, body)
                    # for n, v in initial_sym_table.iteritems():
                        # emitter.pl("; %s: %s" % (n, v.owned))

                    # All variables that will have to be phi'd have to get raised, since we can cheat no longer
                    vars_to_raise = {}
                    for sym, live in live_inputs[(node, node_id)].iteritems():
                        assert live == usage_checker.LIVE
                        for next_id in cfg.connects_to[node_id]:
                            if sym in required_phis[next_id]:
                                assert len(cfg.connects_to[node_id]) == 1, "didn't break this critical edge?"
                                (next_id,) = cfg.connects_to[node_id]
                                next_type = self.type_info.get_block_starting_type(emitter, node, next_id, sym)
                                vars_to_raise[sym] = next_type
                                break
                    self.blockname = "block%d" % node_id

                    # This is where all the code generation actually happens:
                    walker = CompileWalker(parent_module, node_id, f_type, self, emitter, initial_sym_table, self.type_info, live_inputs[(node, node_id)], vars_to_raise, self._closure_results, self._closure_results[parent_module][node], globals_, isinstance(node, _ast.Module))
                    ast_utils.crawl_ast(body, walker, err_missing=True, fn=self._module_filenames[parent_module])

                    sym_tables[node_id] = walker._st
                    end_blocks[node_id] = self.blockname
                    del self.blockname
                    # for n, v in walker._st.iteritems():
                        # emitter.pl("; %s: %s" % (n, v.owned))
                    for sym, live in live_inputs[(node, node_id)].iteritems():
                        if sym in cr.from_global or sym in cr.from_closure or sym in cr.from_builtins or sym in cr.globals_:
                            assert sym not in walker._st
                            continue
                        if sym in cr.used_in_nested:
                            assert isinstance(node, _ast.Module) or sym in walker._st, sym
                            continue
                        if is_inlined_constant(sym, cr):
                            assert isinstance(node, _ast.Module) or sym in walker._st, (sym, node_id)
                            continue
                        if sym in cr.from_local:
                            assert sym in walker._st

                emitter.indent(-4)
                emitter.pl()

            emitter.pl("}")
            emitter.pl()

            # Verify that the non-required-phi stuff actually works
            for node_id in cfg.blocks:
                if node_id == cfg.start or node_id == cfg.end:
                    continue
                for sym, live in live_outputs[(node, node_id)].iteritems():
                    if sym in cr.from_global or sym in cr.from_closure or sym in cr.from_builtins or sym in cr.globals_:
                        assert sym not in sym_tables[node_id]
                        continue

                    assert live == usage_checker.LIVE
                    for prev_id in cfg.connects_from[node_id]:
                        assert live_inputs[(node, prev_id)][sym] == usage_checker.LIVE

                    if sym in required_phis[node_id]:
                        # Make sure everyone going into the phi node followed the contract
                        t = None
                        for prev_id in cfg.connects_from[node_id]:
                            prev_var = sym_tables[prev_id][sym]
                            assert prev_var.nrefs == 1
                            assert prev_var.marked, (node_id, prev_id, sym, prev_var.__dict__)
                            prev_t = prev_var.t
                            assert prev_t.get_instantiated() is prev_t
                            if t is None:
                                t = prev_t
                            else:
                                assert t is prev_t, (sym, node_id, prev_id, t, prev_t)
                    else:
                        # Check to make sure that we really didn't need a phi node
                        var = None
                        var_node_id = None
                        for prev_id in cfg.connects_from[node_id]:
                            prev_var = sym_tables[prev_id][sym]
                            if var is None:
                                var = prev_var
                                var_node_id = prev_id
                                # print sym_tables[prev_id]['n'].__dict__
                                # print sym, prev_id, prev_var.__dict__, id(prev_var)
                            else:
                                # print sym_tables[prev_id]['n'].__dict__
                                # print sym, prev_id, prev_var.__dict__, id(prev_var)
                                assert var.equiv(prev_var), (sym, node_id, var_node_id, prev_id, var.__dict__, prev_var.__dict__)

            s = emitter.get_llvm() + '\n\n'

            def getloc(match):
                sym, block = match.groups()
                block = int(block)
                return str(sym_tables[block][sym].v)
            s = re.sub("#end_loc#([^#]+)#(\d+)#", getloc, s)

            def getblock(match):
                block, = match.groups()
                block = int(block)
                return "%" + end_blocks[block]
            s = re.sub("#end_block#(\d+)#", getblock, s)

            llvm_body.write(s)
            self._body = None

        def move_typedef(m):
            llvm_head.write(m.group()[1:])
            return "\n"

        llvm_head.write("; typedefs:\n")
        tail = re.sub("\n%[\w\d_]+ = type [^\n]+\n", move_typedef, llvm_tail.getvalue())
        llvm_head.write('\n')

        llvm_head.write("define i64 @main(i64 %argc, i8** %argv) {\n")
        llvm_head.write("    call void @init_runtime(i64 %argc, i8** %argv)\n")
        llvm_head.write("    call void @__main___global()\n")
        # TODO: do this more cleanly
        em = CodeEmitter(root_emitter)
        em.indent(4)
        for m in self.modules.values():
            for n, t in m.t._struct.fields:
                m.incvref(em)
                m.getattr(em, n, skip_incref=True).getattr(em, "__decref__").call(em, [])
            for n, t in m.t._struct.constants.iteritems():
                t.decvref(em)
        llvm_head.write("\n    ; decref'ing all module attributes:\n    " + em.get_llvm() + '\n\n')
        llvm_head.write("    call void @teardown_runtime()\n")
        llvm_head.write("    ret i64 0\n")
        llvm_head.write("}\n")

        def replace(s, c=False):
            def getrepl(match):
                rid, = match.groups()
                rid = int(rid)
                r = root_emitter._replacements[rid]
                if c:
                    assert r.startswith("@")
                    return r[1:]
                return r
            return re.sub("#!(\d+)!#", getrepl, s)

        llvm_f.write("; head\n")
        llvm_f.write(replace(llvm_head.getvalue()))
        llvm_f.write("; body\n")
        llvm_f.write(replace(llvm_body.getvalue()))
        llvm_f.write("; tail\n")
        llvm_f.write(replace(tail))

        c_f.write(replace(c_head.getvalue(), c=True))
        c_f.write(replace(c_tail.getvalue(), c=True))

        self._compile_queue = None
        self._head = None
        self._tail = None
        self._out_f = None
        self._cfile = None

        if deps_f:
            def fmt(fn):
                return fn.replace(" ", "\\ ")
            # TODO so hacky
            deps_f.write("%s: %s\n" % (fmt(fn.replace(".py", ".gen.ll")), " ".join(fmt(s) for s in self._loaded_modules)))
            for fn in self._loaded_modules:
                deps_f.write("%s:\n" % fmt(fn))
            deps_f.close()

        for t in ListMT._ListMT__lists.itervalues():
            t._MT__check_initialized("write")
