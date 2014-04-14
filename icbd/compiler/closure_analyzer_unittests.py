#!/usr/bin/env python

import sys
if sys.version_info >= (2,7):
    import unittest as unittest2
else:
    import unittest2

from icbd.util import ast_utils
from icbd.compiler.closure_analyzer import analyze_closures

def get_func(results, name):
    rtn = None
    for fd in results:
        if getattr(fd, "name", "<module>") == name:
            assert not rtn
            rtn = fd
    return rtn

def get_results(results, name):
    return results[get_func(results, name)]

class ClosureUnittests(unittest2.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_defaults_evaluated_in_defining_scope(self):
        source = """
def f():
    def g(x=x):
        pass
x = 1
"""

        node = ast_utils.parse(source, "__test__")
        results = analyze_closures(node)

        assert 'x' in get_results(results, 'f').from_global
        assert 'x' not in get_results(results, 'g').from_global

    def test_checks_dynamic_defaults(self):
        source = """
def f(x=1):
    pass
y = 2
def g(y=y):
    pass
def h():
    f, g
"""

        node = ast_utils.parse(source, "__test__")
        results = analyze_closures(node)

        module = get_results(results, "<module>")
        assert "f" in module.functions
        assert "f" not in module.used_in_nested
        assert "g" not in module.functions
        assert "g" in module.used_in_nested

if __name__ == "__main__":
    unittest2.main()
