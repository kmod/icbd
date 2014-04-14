#!/usr/bin/env python

import _ast
import collections
import functools
import sys

import ast_utils
import builtins
import fpc

UNDEFINED = 0 # not used
MAYBE = 1
DEFINED = 2

BUILTINS = list(builtins.BUILTINS)
BUILTINS.extend(dir(__builtins__))
BUILTINS.append("__builtins__")

class DefinednessAnalyzer(object):
    def __init__(self, scope, state, e):
        self._scope = scope
        self._state = state
        self._e = e

        for n in ("expr", "print", "pass", "compare", "str", "call", "attribute", "num", "keyword", "unaryop", "dict", "subscript", "index", "boolop", "assert", "tuple", "binop", "return", "slice", "list", "raise", "ifexp", "yield", "jump", "branch", "hasnext"):
            setattr(self, "pre_%s" % n, lambda node:None)

    def _set(self, target, action=None):
        q = collections.deque([target])
        to_set = set()
        while q:
            t = q.pop()
            if isinstance(t, _ast.Name):
                to_set.add(t.id)
            elif isinstance(t, str):
                to_set.add(t)
            elif isinstance(t, (_ast.Tuple, _ast.List)):
                q.extend(t.elts)
            elif isinstance(t, (tuple, list)):
                q.extend(t)
            elif isinstance(t, (_ast.Attribute, _ast.Subscript)):
                pass
            else:
                raise Exception(t)

        for n in to_set:
            if action:
                action(n)
            else:
                self._state[n] = DEFINED
                self._scope.set_name(n, DEFINED)

    def pre_assign(self, node):
        return [functools.partial(self._set, node.targets), node.value]

    def pre_augassign(self, node):
        return [functools.partial(self._set, node.target), node.target, node.value]

    def pre_global(self, node):
        pass

    def pre_delete(self, node):
        def do_delete(n):
            if not isinstance(self._scope, fpc.ModuleScope) and n in self._scope.global_names:
                self._e.do_error(node.lineno, node.col_offset, "deleted global variable '%s'" % n)
                return

            v = self._state.pop(n, None)
            if v is None or v == UNDEFINED:
                self._e.do_error(node.lineno, node.col_offset, "'%s' is definitely undefined" % n)
            elif v == MAYBE:
                self._e.do_error(node.lineno, node.col_offset, "'%s' is potentially undefined" % n)
        self._set(node.targets, action=do_delete)
        return ()

    def pre_name(self, node):
        n = node.id
        if n in BUILTINS:
            return

        if self._scope.get_name(n, self._e.my_listener(), skip=True):
            return
        # 'import *' will actually set the name *
        if self._scope.get_name('*', self._e.my_listener(), global_=True):
            return

        if self._state.get(n, UNDEFINED) == UNDEFINED:
            self._e.do_error(node.lineno, node.col_offset, "'%s' is definitely undefined" % (n,))
        elif self._state.get(n, UNDEFINED) == MAYBE:
            self._e.do_error(node.lineno, node.col_offset, "'%s' is potentially undefined" % (n,))

    def pre_import(self, node):
        for a in node.names:
            if a.asname:
                name = a.asname
            elif '.' in a.name:
                name = a.name[:a.name.find('.')]
            else:
                name = a.name
            self._set(name)
        return ()

    def pre_importfrom(self, node):
        for a in node.names:
            assert not a.asname
            self._set(a.name)
        return ()

    def pre_classdef(self, node):
        def after_check():
            self._set(node.name)
            self._e.queue_scope(node, {}, self._scope)

        return [after_check] + list(reversed(node.decorator_list)) + list(reversed(node.bases))

    def pre_functiondef(self, node):
        def after_check():
            self._set(node.name)
            init = {}

            args = []
            for a in node.args.args:
                args.append(a)
            if node.args.vararg:
                args.append(node.args.vararg)
            if node.args.kwarg:
                args.append(node.args.kwarg)

            for a in args:
                self._set(a, action=lambda n: init.setdefault(n, DEFINED))

            scope = self._e.queue_scope(node, init, self._scope)
            for a in args:
                self._set(a, action=lambda n: scope.set_name(n, DEFINED))

        return [after_check] + list(reversed(node.decorator_list))

    def pre_lambda(self, node):
        return ()

    def pre_listcomp(self, node):
        orig_state = dict(self._state)
        def restore():
            for k, v in self._state.iteritems():
                if orig_state.get(k, UNDEFINED) != DEFINED:
                    self._state[k] = MAYBE
        return reversed(node.generators + [node.elt, restore])

    def pre_generatorexp(self, node):
        orig_state = dict(self._state)
        def restore():
            self._state = orig_state
        return reversed(node.generators + [node.elt, restore])

    def pre_comprehension(self, node):
        def add():
            extra = self._set(node.target)
            return extra

        return node.ifs + [add, node.iter]

def definedness_bb(e, scope, block, start):
    assert isinstance(start, dict)

    a = DefinednessAnalyzer(scope, dict(start), e)
    ast_utils.crawl_ast(block, a, err_missing=True)
    return a._state

def definedness_aggregator(output_dict, cur, prev_input):
    defined = {}
    keys = set()
    for state in output_dict.itervalues():
        if state is not None:
            keys.update(state)

    for k in keys:
        # the 'd is None' part is ok (and required) because we iterate through things in forward order of program execution
        if all(d is None or d.get(k, UNDEFINED) == DEFINED for d in output_dict.itervalues()):
            defined[k] = DEFINED
        else:
            defined[k] = MAYBE

    if defined == prev_input:
        return None
    return defined

def get_definedness(node):
    comp = fpc.FixedPointComputator()
    parent_scope = None
    initial_state = {}
    if isinstance(node, (_ast.FunctionDef, _ast.Lambda)):
        parent_scope = fpc.ModuleScope()
        assert not node.args.vararg
        assert not node.args.kwarg
        for a in node.args.args:
            assert isinstance(a, _ast.Name), "unhandled"
            initial_state[a.id] = DEFINED

    comp.queue_scope(node, initial_state, parent_scope)
    input, output = comp.compute(definedness_bb, definedness_aggregator)

    if isinstance(node, (_ast.FunctionDef, _ast.Lambda)):
        assert not parent_scope.names
    errors = []
    for errs in comp.errors.itervalues():
        errors += errs.items()
    return input, output, errors

if __name__ == "__main__":
    fn = sys.argv[1]

    source = open(fn).read()
    try:
        node = ast_utils.parse(source, fn)
    except SyntaxError:
        print "Failed to parse %s due to a syntax error" % (fn,)
        sys.exit(1)
    assert isinstance(node, _ast.Module), node

    try:
        input, output, errors = get_definedness(node)
    except:
        print "Failed on", fn
        raise
    print "input:"
    for n, s in sorted(input.items()):
        print n, s
    print
    print "output:"
    for n, s in sorted(output.items()):
        print n, s
    print

    for (l, c), s in errors:
        print "At %s:%d: %s" % (fn, l, s)
