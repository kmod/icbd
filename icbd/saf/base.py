import _ast
import cPickle
import getopt
import os
import sys

from icbd.type_analyzer import type_checker
from icbd.util import ast_utils

from browser import SourceBrowserOutputPass

class Codebase(object):
    def __init__(self):
        self.modules = {} # module_name => _ast.Module
        # self.node_types = {} # _ast.AST => Type
        # self.uses = {} # _ast.AST => [_ast.AST]
        # self.defs = {} # _ast.AST => [_ast.AST]

class PassManager(object):
    @staticmethod
    def run(python_path, passes):
        # TODO: the type analysis should just be a normal pass, but for it's special
        # since it also resolves imports; this should be handled separately though.
        engine = type_checker.Engine()
        engine.python_path.extend(python_path)
        engine._load(script_fn, "__main__")
        success = engine.analyze()
        assert success

        cb = Codebase()
        for node, scope in engine.scopes.iteritems():
            if isinstance(node, _ast.Module):
                assert scope._t.name not in cb.modules, "need to fix this behavior in the type analyzer"
                cb.modules[scope._t.name] = node
        cb.node_types = engine.node_types

        for p in passes:
            p.run(cb)

        return cb

"""
class DefFinderWalker(object):
    def __init__(self):
        self.found = []

    def pre_name(self, n):
        if isinstance(n.ctx, _ast.Store):
            self.found.append(n)
        return ()

    def _add_found(self, n):
        self.found.append(n)
        return ()
    pre_functiondef = _add_found
    pre_classdef = _add_found

class UseDefPass(object):
    def run(self, cb):
        assert not hasattr(cb, 'uses')
        assert not hasattr(cb, 'defj')
        cb.uses = {}
        cb.defs = {}

        def_finder = DefFinderWalker()
        for node in cb.modules.itervalues():
            ast_utils.crawl_ast(node, def_finder)
        print def_finder.found
        def_types = {}
"""

class AstTokenMatchingPass(object):
    def run(self, cb):
        assert not hasattr(cb, "pos_to_token")
        cb.pos_to_token = {}
        for n, m in cb.modules.iteritems():
            d = {}
            cb.pos_to_token[n] = d

            self.d = d
            ast_utils.crawl_ast(m, self)

    def pre_name(self, node):
        self.d[(node.lineno, node.col_offset)] = node
    def pre_functiondef(self, node):
        self.d[(node.lineno, node.col_offset + 4)] = node
    def pre_classdef(self, node):
        self.d[(node.lineno, node.col_offset + 6)] = node
    def pre_attribute(self, node):
        self.d[(node.lineno, node.col_offset + ast_utils.est_expr_length(node.value) + 1)] = node

if __name__ == "__main__":
    optlist, args = getopt.gnu_getopt(sys.argv[1:], "I:c:", [])
    assert len(args) == 1
    [script_fn] = args

    python_path = []
    python_path.append(os.path.join(os.path.dirname(__file__), '../../stdlib/python2.5_small'))
    python_path.append(os.path.join(os.path.dirname(__file__), '../../stdlib/type_mocks'))

    cache = None
    for n,v in optlist:
        if n == '-I':
            python_path.append(v)
        elif n == '-c':
            cache = v
        else:
            raise Exception(n)

    passes = [
            AstTokenMatchingPass(),
            SourceBrowserOutputPass(script_fn),
            ]
    cb = PassManager.run(python_path, passes)
