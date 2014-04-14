#!/usr/bin/env python

import _ast
import collections
import sys

from ..util import ast_utils
from ..util import cfa
from ..util import fpc

class PhiAnalyzer(object):
    def __init__(self, state, e):
        self._state = state
        self._id = e.cur_key[1]
        assert isinstance(self._id, int)

        for n in ("expr", "print", "pass", "compare", "str", "call", "attribute", "num", "keyword", "unaryop", "dict", "subscript", "index", "boolop", "assert", "tuple", "binop", "return", "slice", "list", "raise", "ifexp", "yield", "jump", "hasnext", "name", "branch", "global"):
            setattr(self, "pre_%s" % n, lambda node:())

    def _set(self, t):
        if isinstance(t, _ast.Name):
            self._state[t.id] = (self._id, False)
        elif isinstance(t, str):
            self._state[t] = (self._id, False)
        elif isinstance(t, (_ast.Subscript, _ast.Attribute)):
            pass
        elif isinstance(t, (_ast.Tuple, _ast.List)):
            for e in t.elts:
                self._set(e)
        else:
            raise Exception(t)

    def pre_import(self, node):
        for n in node.names:
            assert not n.asname
            assert '.' not in n.name
            self._set(n.name)
        return ()

    def pre_importfrom(self, node):
        for n in node.names:
            name = n.asname or n.name
            assert '.' not in n.name
            assert '.' not in name
            self._set(name)
        return ()

    def pre_assign(self, node):
        for t in node.targets:
            self._set(t)
        return ()

    def pre_augassign(self, node):
        self._set(node.target)
        return ()

    def pre_functiondef(self, node):
        self._set(node.name)
        return ()

    def pre_classdef(self, node):
        self._set(node.name)
        return ()

def phi_bb(e, scope, block, start_state):
    assert isinstance(start_state, dict)

    copy = dict(start_state)
    a = PhiAnalyzer(copy, e)
    ast_utils.crawl_ast(block, a, err_missing=True)
    return a._state

def phi_aggregator(outputs, cur_id, prev_input):
    changed = False
    if prev_input is None:
        changed = True
        merged = {}
    else:
        merged = prev_input

    keys = set()
    for state in outputs.itervalues():
        if state is not None:
            keys.update(state)

    for k in keys:
        possible = set([d[k] for d in outputs.itervalues() if d and k in d])

        # Don't create a phi like 'x = phi x, y', since that could just be y.
        # This is why we have to mark if a def was a phi or not, because we would need a phi
        # if there was a definition later in the block
        if (cur_id, True) in possible:
            possible.remove((cur_id, True))

        assert possible
        assert len(set([p[0] for p in possible])) == len(possible), "Found both a phi and non-phi from the same BB???"

        if len(possible) == 1:
            [def_node] = possible
        else:
            def_node = (cur_id, True)

        if def_node != merged.get(k):
            # print "Changed because %s updated from %s to %s at %d" % (k, merged.get(k), def_node, cur_id)
            merged[k] = def_node
            changed = True

    if changed:
        return merged

def determine_phi_instructions(node):
    # q = fpc.RandomizedQueue()
    q = fpc.MinQueue()
    # q = fpc.FifoQueue()
    comp = fpc.FixedPointComputator(queue=q)

    parent_scope = None
    if isinstance(node, (_ast.FunctionDef, _ast.Lambda)):
        parent_scope = fpc.ModuleScope()

    initial = {}
    if isinstance(node, _ast.FunctionDef):
        for a in node.args.args:
            for n in ast_utils.find_names(a):
                assert isinstance(n, _ast.Name)
                # TODO don't know this is the actual cfg.start
                initial[n.id] = (0, False)
    comp.queue_scope(node, initial, parent_scope)
    input, output = comp.compute(phi_bb, phi_aggregator)

    if isinstance(node, (_ast.FunctionDef, _ast.Lambda)):
        assert not parent_scope.names

    # print "input:"
    # for n, s in sorted(input.items()):
        # print n, s
    # print
    # print "output:"
    # for n, s in sorted(output.items()):
        # print n, s
    # print

    r = {}
    cfg = comp.cfgs[node]
    for node_id in cfg.blocks:
        if node_id == cfg.start or node_id == cfg.end:
            continue
        l = r.setdefault(node_id, [])
        # cfg.show()

        # This gets triggered when there are return statements inside the try block of a try-finally
        assert (node, node_id) in input, (node, node_id, node.body[0].lineno)
        for k, v in input[(node, node_id)].iteritems():
            needs = False
            for prev_id in cfg.connects_from[node_id]:
                if k in output[(node, prev_id)] and output[(node, prev_id)][k] != v:
                    needs = True
                    break
            if needs:
                l.append(k)

    return r

def main():
    # Match the compiler for consistency:
    cfa.REDUCE_FORS_TO_WHILES = True
    cfa.PRUNE_UNREACHABLE_BLOCKS = True
    cfa.ENFORCE_NO_MULTIMULTI = True

    fn = sys.argv[1]

    source = open(fn).read()
    try:
        node = ast_utils.parse(source, fn)
    except SyntaxError:
        print "Failed to parse %s due to a syntax error" % (fn,)
        sys.exit(1)

    assert isinstance(node, _ast.Module), node
    q = [node]
    while q:
        n = q.pop()

        print
        if isinstance(n, _ast.Module):
            print "main"
        else:
            print n.name
        cfa.cfa(n).show()
        print determine_phi_instructions(n)
        q.extend(ast_utils.find_functions(n))

if __name__ == "__main__":
    main()

