import _ast
import glob
import os
import re
import subprocess
import sys

from icbd.util import cfa
from icbd.type_analyzer import type_checker
import plugins.sqlalchemy

def parse_annotations(s):
    offset, s = s.split(' ', 1)
    return {int(offset):s}

def test(fn):
    cfa.ADD_IF_ASSERTS = True

    fn = os.path.abspath(fn)
    engine = type_checker.Engine()

    plugins.sqlalchemy.load(engine)

    # engine.python_path.append(os.path.dirname(os.path.abspath(fn)))
    engine.python_path.append(os.path.abspath(os.path.join(__file__, "../../../stdlib/type_mocks")))

    # engine.load("stdlib/builtins.py")
    # type_checker.BUILTINS.update(type_checker.KNOWN_MODULES['builtins'].scope.globals_)

    src = open(fn).read()
    engine._load(fn, "__main__")
    good = engine.analyze()

    for i in xrange(0):
        for k in engine.inputs:
            engine.queue.append(k)
        engine.analyze()

    found = engine.annotations[fn]

    source_lines = src.split('\n')

    expected_errors = set()

    for i, l in enumerate(source_lines):
        if '#' not in l:
            continue
        annotations = {}
        for c in l.split('#')[1:]:
            c = c.strip()
            if c.startswith('e'):
                expected_errors.add((i+1, int(c.split(' ', 1)[1])))
            else:
                if not re.match('[0-9]', c.strip()):
                    print "Warning: weird comment at %s: '%s'" % (i+1, c.strip())
                else:
                    annotations.update(parse_annotations(c.strip()))
        for offset, a in annotations.items():
            key = (i+1, offset)
            if key not in found:
                print "Did not find annotation at %s; expected '%s'" % (key, a)
                good = False
            elif found[key][0].prettify().display() != a:
                print "Got annotation '%s' at %s instead of '%s'" % (found[key][0].prettify().display(), key, a)
                good = False

    found_errors = {}
    for k, d in engine.errors.iteritems():
        if engine.scopes[k[0]].filename() != fn:
            continue
        for (lineno, start, end), msg in d.iteritems():
            found_errors[(lineno, start)] = msg
    for p in sorted(expected_errors.difference(found_errors)):
        print "Expected to find an error at %s, but didn't" % (p,)
        good = False
    for p in sorted(set(found_errors).difference(expected_errors)):
        print "Didn't expect to find an error at %s, but got '%s'" % (p, found_errors[p])
        good = False

    return good

if __name__ == "__main__":
    fn, args = sys.argv[1], sys.argv[2:]
    good = True

    do_output = "--nooutput" not in args

    good = test(fn)

    if do_output:
        print "Generating output"
        p = subprocess.Popen(["python", "type_checker.py", fn], stdout=open("/dev/null", 'w'))
        r = p.wait()
        good = (r == 0) and good

    if not good:
        sys.exit(1)
