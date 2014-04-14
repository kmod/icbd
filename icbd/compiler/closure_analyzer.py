#!/usr/bin/env python

import _ast
import collections
import sys

from ..util import ast_utils
from ..util import cfa

# No idea why this is sometimes a dict and sometimes a module...
_builtins = set(__builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__)
_builtins.add('nrefs')
_builtins.add('__cast__')

def _is_constant(node):
    if isinstance(node, _ast.Name):
        return node.id in ("True", "False", "None")

    if isinstance(node, (_ast.Str, _ast.Num)):
        return True

    return False

class ScopeState(object):
    def __init__(self, node, parent):
        self.node = node
        self.parent = parent
        self.defined = set()
        self.referenced = set()
        self.functions = {}
        self.classes = {}
        self.modules = set()

        if isinstance(node, (_ast.FunctionDef, _ast.ClassDef)):
            self.globals_ = ast_utils.find_global_vars(node)
        else:
            self.globals_ = []

        if isinstance(node, (_ast.FunctionDef, _ast.Lambda)):
            if node.args.kwarg:
                self.defined.add(node.args.kwarg)
            if node.args.vararg:
                self.defined.add(node.args.vararg)
            for a in node.args.args:
                for n in ast_utils.find_names(a):
                    assert isinstance(n, _ast.Name), n
                    self.defined.add(n.id)

class ClosureResults(object):
    def __init__(self, parent):
        self.parent = parent
        self.takes_closure = False  # Whether this scope needs to have its parent closure passed in

        # List of things that this closure may set:
        self.globals_ = None        # Set of globals declared in this scope (as defined by ast_utils.find_global_vars)
        self.used_in_nested = set() # Non-constant names referenced from nested scopes
        self.functions = set()      # Set of constant functions (by name)
        self.classes = set()        # Set of constant classes (by name)
        self.modules = set()        # Set of constant modules (by name)
        self.local_only = set()     # Set of names that are not referenced from closures (excluding functions/classes/modules)

        # Lists of things that this closure gets:
        self.from_closure = set()   # Set of names gotten from the parent closure
        self.from_local = set()     # "" local scope
        self.from_global = set()    # "" global closure
        self.from_builtins = set()  # "" builtins


    def has_data(self):
        return bool(self.used_in_nested) or bool(self.functions) or bool(self.classes) or bool(self.modules)

class Analyzer(object):
    def __init__(self, state):
        self.state = state
        self.sub_nodes = []

    def _set_defined(self, name):
        if name in self.state.globals_:
            return

        self.state.functions.pop(name, None)
        self.state.classes.pop(name, None)
        try:
            self.state.modules.remove(name)
        except KeyError:
            pass
        self.state.defined.add(name)

    def have_name(self, name):
        return name in self.state.defined or name in self.state.functions or name in self.state.classes or name in self.state.modules or name in self.state.globals_

    def pre_name(self, node):
        if isinstance(node.ctx, _ast.Load):
            self.state.referenced.add(node.id)
        else:
            # HAX to support augassign:
            self.state.referenced.add(node.id)
            self._set_defined(node.id)
        return ()

    def pre_importfrom(self, node):
        # TODO should determine (with type info) if this is a (static) module, and if it's static, so we can statically resolve it
        # ie "from os import path" should have path map directly to the "os/path" module
        for n in node.names:
            self._set_defined(n.asname or n.name)
        return ()

    def pre_import(self, node):
        for n in node.names:
            assert not n.asname
            assert not '.' in n.name
            if self.have_name(n.name) and n.name not in self.state.modules:
                self._set_defined(n.name)
            else:
                self.state.modules.add(n.name)
        return ()

    def pre_classdef(self, node):
        self.sub_nodes.append(node)

        # HAX: the code generator currently doesn't create scopes for class definitions;
        # this is ok since it disallows anything but functiondefs and handles those appropriately.
        # This is a problem when it has to go and compute function defaults, since technically
        # those should be evaluated in the class scope, ie they could refer to class members
        # without qualification.  Come up with a hacky solution for now, which is to
        # pseudo-support evaluating them in the class's parent scope, by marking the variables
        # as referenced.
        hax_defaults = []
        for f in ast_utils.find_functions(node):
            hax_defaults += f.args.defaults

        if self.have_name(node.name):
            self._set_defined(node.name)
        else:
            self.state.classes[node.name] = node
        return node.bases + node.decorator_list + hax_defaults

    def pre_lambda(self, node):
        self.sub_nodes.append(node)
        return ()

    def pre_functiondef(self, node):
        self.sub_nodes.append(node)
        if self.have_name(node.name) or any(not _is_constant(d) for d in node.args.defaults) or node not in self.state.node.body:
            self._set_defined(node.name)
        else:
            self.state.functions[node.name] = node
        # The default args get evaluated in the defining scope:
        return node.args.defaults

def analyze_closures(module):
    assert isinstance(module, _ast.Module)
    to_analyze = [(module, None)]

    states = {}
    output = {}
    while to_analyze:
        node, parent = to_analyze.pop()
        state = ScopeState(node, states.get(parent, None))

        a = Analyzer(state)
        # Compute the CFG, so that we analyze the exact same code that everything else will operate on
        if isinstance(node, _ast.Lambda):
            ast_utils.crawl_ast(node.body, a)
        else:
            cfg = cfa.cfa(node)
            for body in cfg.blocks.itervalues():
                ast_utils.crawl_ast(body, a)

        for n in ("True", "False", "None", "range", "xrange"):
            assert n not in state.defined, "%s is a keyword now" % (n, getattr(node, "name", "<module>"))

        states[node] = state
        output[node] = ClosureResults(output.get(parent, None))
        output[node].globals_ = state.globals_

        for n in a.sub_nodes:
            to_analyze.append((n, node))

    # Function constant-ness takes some work to compute.  A reference to a constant function
    # requires the intervening scopes to have closures iff the referenced function itself takes a closure,
    # since then even though the name->func.code map is static, the func itself isn't.
    #
    # This means that when we learn a function needs to take a closure, there may be a set of other functions
    # that then also need to take closures (ie anything scopes traversed while searching for the original function).
    # This in turn could recursively set more functions to take closures.
    #
    # Instead of processing this on the fly, keep track of all the dependencies, and after we compute
    # the root set of surely-closured functions, compute the transitive "takes-closure" property

    # map of functiondefs -> the node that contains them; need this for bookkeeping
    function_parents = {}
    # map of functiondefs -> set of functions that need to take a closure if the key function takes a closure
    function_references = {}

    for node, results in output.iteritems():
        # 'None' can be implicitly referenced by not adding a return statement
        # Ideally we'd detect those cases, which would let people redefine None,
        # but I don't think it's a very important feature
        results.from_builtins.add("None")

        state = states[node]

        for name in state.referenced:
            # Special-casing None; see above comment at line 161
            if name == "None":
                continue

            if name in state.defined or name in state.functions or name in state.classes or name in state.modules:
                continue

            if name in state.globals_:
                continue

            searched = set([node])
            parent = state.parent
            while True:
                def add_from_scope(name):
                    if isinstance(parent.node, _ast.Module):
                        results.from_global.add(name)
                    else:
                        results.from_closure.add(name)

                if parent is None:
                    assert name in _builtins, "%s is undefined in %s" % (name, getattr(node, 'name', type(node).__name__))
                    results.from_builtins.add(name)
                    break
                if name in parent.globals_:
                    # This lookup skips to the global scope
                    results.from_global.add(name)
                    output[module].used_in_nested.add(name)
                    break
                if name in parent.defined:
                    add_from_scope(name)
                    output[parent.node].used_in_nested.add(name)
                    # If this hits the global closure, don't need to set any of them as closured
                    if not isinstance(parent.node, _ast.Module):
                        for n in searched:
                            # The global closure is special: since we know where it is, we don't need to pass it
                            # around; this lets us avoid making top-level functions closured.
                            if n not in module.body:
                                output[n].takes_closure = True
                    break
                if name in parent.classes or name in parent.modules:
                    add_from_scope(name)
                    # Don't need to create closures for these
                    break
                # Have to do a little more work for potentially-constant functions, because we don't
                # know if they're constant yet (due to closure issues).
                if name in parent.functions:
                    add_from_scope(name)
                    f = parent.functions[name]
                    assert f in parent.node.body
                    function_parents[f] = parent.node
                    function_references.setdefault(f, set()).update(searched)
                    break

                searched.add(parent.node)
                parent = parent.parent

        output[node].classes = set(state.classes)
        output[node].modules = set(state.modules)

    assert set(function_parents) == set(function_references)

    # Calculate the "takes-closure" property for functions here (see above comment):
    q = collections.deque([fd for fd in function_references if output[fd].takes_closure])
    while q:
        fd = q.popleft()
        assert output[fd].takes_closure

        if fd not in function_references:
            continue

        refs = function_references[fd]
        p = function_parents[fd]
        assert fd.name not in output[p].used_in_nested
        assert fd.name not in output[p].functions
        output[p].used_in_nested.add(fd.name)

        for r in refs:
            # This doesn't need to be true, but if it's not we should filter these out,
            # and I'm pretty sure that this shouldn't happen
            assert r not in module.body
            if not output[r].takes_closure:
                output[r].takes_closure = True
                q.append(r)

    # Use the takes-closure property to determine which functions can be lowered
    # to direct function calls rather than indirect.
    for fd in function_references:
        p = function_parents[fd]
        assert fd.name not in output[p].functions
        if output[fd].takes_closure:
            assert fd.name in output[p].used_in_nested, fd.name
        else:
            assert fd.name not in output[p].used_in_nested
            output[p].functions.add(fd.name)

    # The global closure is special (doesn't get passed around explicitly), so double-check that
    # we treated it as such:
    assert not output[module].takes_closure
    for node, results in output.iteritems():
        if node in module.body:
            assert not results.takes_closure

    output[module].used_in_nested.update(ast_utils.find_global_vars(module, recursive=True))

    # Now that we've calculated where things are used, we can calculate
    # which names are local-only:
    for node, results in output.iteritems():
        state = states[node]
        for name in state.referenced:
            # Special-casing None; see above comment at line 161
            if name == "None":
                continue

            if name in state.defined:
                if isinstance(node, _ast.Module) and name in results.used_in_nested:
                    results.from_global.add(name)
                else:
                    results.from_local.add(name)
                continue

            if name in state.functions:
                results.from_local.add(name)
                continue
            if name in state.classes:
                results.from_local.add(name)
                continue
            if name in state.modules:
                results.from_local.add(name)
                continue

            if name in state.globals_:
                results.from_global.add(name)
                continue

            if name in _builtins and name not in results.from_global and name not in results.from_closure:
                results.from_builtins.add(name)
                continue

            # results.from_local.add(name)

    # Finally, do some computation around where things get defined to:
    for node, results in output.iteritems():
        state = states[node]
        for name in state.defined.union(state.functions).union(state.modules).union(state.classes):
            assert name not in results.from_closure
            assert name not in results.from_builtins

            if name in results.globals_:
                continue
            if name in results.used_in_nested or name in results.functions or name in results.classes or name in results.modules:
                continue

            if name in state.functions:
                results.functions.add(name)
            else:
                results.local_only.add(name)

    # For the global closure, all local variable accesses hit the global scope.
    # We special-case variables like '__foriter_', which are generated by the cfa pass,
    # since they cannot be referenced by other scopes
    mod_cr = output[module]
    for n in list(mod_cr.local_only):
        if not n.startswith("__foriter_"):
            mod_cr.used_in_nested.add(n)
            mod_cr.local_only.remove(n)
    for n in list(mod_cr.from_local):
        if not n.startswith("__foriter_"):
            mod_cr.from_global.add(n)
            mod_cr.from_local.remove(n)

    # And some sanity checking
    for node, results in output.iteritems():
        froms = [results.from_local, results.from_closure, results.from_global, results.from_builtins]
        for i in xrange(len(froms)):
            for j in xrange(i):
                assert not froms[i].intersection(froms[j]), (getattr(node, "name", "<module>"), froms)

    return output

if __name__ == "__main__":
    # Match the compiler:
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

    output = analyze_closures(node)

    for node, results in sorted(output.items(), key=lambda x:getattr(x[0], "lineno", 0)):
        print "%s:" % (ast_utils.node_name(node),)
        print "needs to get passed a closure" if results.takes_closure else "doesn't get passed a closure"
        print "Referenced from nested:", results.used_in_nested
        print "Singly-defined functions", results.functions
        print "Classes defined:", results.classes
        print "Modules imported:", results.modules
        print "Defined only for locals:", results.local_only
        print "Gets from local:", results.from_local
        print "Gets from closure:", results.from_closure
        print "Gets from global:", results.from_global
        print "Gets from builtins:", results.from_builtins
        print

