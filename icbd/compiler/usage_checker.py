#!/usr/bin/env python

import _ast
import collections
import functools
import sys

from ..util import ast_utils, cfa, fpc
from ..type_analyzer import builtins

# DEAD = 0
LIVE = 1


ERR_UNUSED_GLOBALS = 1
ERR_UNUSED_UNPACKED = 1

assert ERR_UNUSED_UNPACKED, "dont support turning this off"

class LivenessAnalyzer(object):
    def __init__(self, scope, state, e):
        self._scope = scope
        self._state = state
        self._e = e

        for n in ("expr", "print", "pass", "compare", "str", "call", "attribute", "num", "keyword", "unaryop", "dict", "subscript", "index", "boolop", "assert", "tuple", "binop", "return", "slice", "list", "raise", "ifexp", "yield", "jump", "hasnext", "global"):
            setattr(self, "pre_%s" % n, lambda node:None)

    def _set(self, target, node):
        q = collections.deque([target])

        # Note: this doesn't behave correctly with chained assignments, ex in
        # c = c.x = C() [this actually works...]
        # this does _not_ make c live.
        # I think it should work correctly as long as you go through the assigments one by one

        defined = set()
        referenced = set()
        while q:
            t = q.pop()
            if t is None:
                continue

            if isinstance(t, _ast.Name):
                if isinstance(t.ctx, _ast.Load):
                    referenced.add(t.id)
                else:
                    defined.add(t.id)
            elif isinstance(t, (_ast.Tuple, _ast.List)):
                q.extend(t.elts)
            elif isinstance(t, (tuple, list)):
                q.extend(t)
            elif isinstance(t, _ast.Attribute):
                q.append(t.value)
            elif isinstance(t, _ast.Subscript):
                q.append(t.value)
                q.append(t.slice)
            elif isinstance(t, _ast.Index):
                q.append(t.value)
            elif isinstance(t, (_ast.Num, _ast.Str)):
                continue
            elif isinstance(t, str):
                defined.add(t)
            elif isinstance(t, _ast.BinOp):
                # TODO this could get arbitrarily tough; should just use ast_utils.crawl_ast
                q.append(t.left)
                q.append(t.right)
            elif isinstance(t, _ast.Slice):
                q.append(t.upper)
                q.append(t.lower)
                q.append(t.step)
            elif isinstance(t, _ast.Call):
                # TODO I will have to do this for every item... I should use ast_utils
                q.append(t.starargs)
                q.append(t.func)
                q.append(t.kwargs)
                q.extend(t.args)
                q.extend(t.keywords)
            else:
                raise Exception(t, type(t))

        for n in defined:
            self._handle_def(node, n)

        for n in referenced:
            self._state[n] = LIVE

    def pre_branch(self, node):
        pass

    def pre_name(self, node):
        self._state[node.id] = LIVE
        return ()

    def pre_import(self, node):
        for n in node.names:
            assert not n.asname
            assert '.' not in n.name
            self._set(n.name, node)
        return ()

    def pre_importfrom(self, node):
        for n in node.names:
            name = n.asname or n.name
            assert '.' not in n.name
            assert '.' not in name
            self._set(name, node)
        return ()

    def pre_getnext(self, node):
        return (node.iter,)

    def pre_augassign(self, node):
        self._set(node.target, node)
        return (node.target, node.value)

    def _handle_def(self, node, n):
        if n in self._state:
            assert self._state[n] == LIVE
            del self._state[n]
            return

        if isinstance(self._scope, fpc.ModuleScope) and not ERR_UNUSED_GLOBALS:
            return

        if isinstance(self._scope, fpc.ClassScope):
            # Don't worry about class attributes that we didn't detect were used
            return

        if isinstance(self._scope, (fpc.FunctionScope, fpc.ClassScope)) and n in self._scope.global_names:
            return

        if hasattr(node, "lineno"):
            self._e.do_error(node.lineno, node.col_offset, "'%s' defined but never used" % (n,))

    def pre_assign(self, node):
        for t in reversed(node.targets):
            self._set(t, node)
        return [node.value]

    def pre_functiondef(self, node):
        self._handle_def(node, node.name)
        self._e.queue_scope(node, {}, self._scope)

        return node.decorator_list

    def pre_lambda(self, node):
        self._e.queue_scope(node, {}, self._scope)
        return ()

    def pre_classdef(self, node):
        self._handle_def(node, node.name)
        self._e.queue_scope(node, {}, self._scope)

        return node.bases + node.decorator_list

    def pre_comprehension(self, node):
        do_set = functools.partial(self._set, node.target, node)
        # return node.ifs + [do_set, node.iter]
        return [node.iter, do_set] + node.ifs

    def pre_generatorexp(self, node):
        return self.pre_listcomp(node)

    def pre_listcomp(self, node):
        assert len(node.generators) == 1

        old_live = dict(self._state)
        # print old_live
        new_live = liveness_bb(self._e, fpc.FunctionScope(self._scope), [node.elt], self._state)
        # print new_live
        new_live = liveness_bb(self._e, fpc.FunctionScope(self._scope), [node.generators[0]], new_live)
        # print new_live

        # print "newly live:", set(new_live).difference(old_live)
        # print "no longer live:", set(old_live).difference(new_live)

        for n in set(new_live).difference(old_live):
            self._state[n] = LIVE
        return ()

def liveness_bb(e, scope, block, start):
    assert isinstance(start, dict)

    a = LivenessAnalyzer(scope, dict(start), e)
    ast_utils.crawl_ast(block, a, err_missing=True, backwards=True, fn=e.fn)
    return a._state

def liveness_aggregator(output_dict, cur, prev_input):
    live = {}
    keys = set()
    for state in output_dict.itervalues():
        if state is not None:
            keys.update(state)

    for k in keys:
        if any(d is None or d.get(k, None) == LIVE for d in output_dict.itervalues()):
            live[k] = LIVE

    if live == prev_input:
        return None
    return live

def get_liveness(node, fn=None):
    comp = fpc.FixedPointComputator(backwards=True, fn=fn)
    parent_scope = None
    if isinstance(node, (_ast.FunctionDef, _ast.Lambda)):
        parent_scope = fpc.ModuleScope()
    comp.queue_scope(node, {}, parent_scope)
    for nid in comp.cfgs[node].blocks:
        comp.mark_changed((node, nid))
        comp.input_states[(node, nid)] = {}
    input, output = comp.compute(liveness_bb, liveness_aggregator)
    if isinstance(node, (_ast.FunctionDef, _ast.Lambda)):
        assert not parent_scope.names
    warnings = []
    for errs in comp.errors.itervalues():
        warnings += errs.items()
    return input, output, warnings

if __name__ == "__main__":
    cfa.PRUNE_UNREACHABLE_BLOCKS = True
    cfa.REDUCE_FORS_TO_WHILES = True
    cfa.ENFORCE_NO_MULTIMULTI = True

    fn = sys.argv[1]
    if len(sys.argv) >= 3:
        out_fn = sys.argv[2]
    else:
        out_fn = fn.replace(".py", ".ll")

    source = open(fn).read()
    try:
        node = ast_utils.parse(source, fn)
    except SyntaxError:
        print "Failed to parse %s due to a syntax error" % (fn,)
        sys.exit(1)
    assert isinstance(node, _ast.Module), node

    try:
        input, output, warnings = get_liveness(node)
    except:
        print "Failed on", fn
        raise

    nodes = set([n for n, id in input.keys()])

    for node in nodes:
        print getattr(node, "name", "<module>")
        cfa.cfa(node).show()

        print "input:"
        for n, s in sorted(input.items()):
            if n[0] == node:
                print n, s
        print
        print "output:"
        for n, s in sorted(output.items()):
            if n[0] == node:
                print n, s
        print

    for (l, c), s in warnings:
        print "At %s:%d: %s" % (fn, l, s)

