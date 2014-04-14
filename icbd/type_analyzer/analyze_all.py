from __future__ import absolute_import

"""
Script to do a whole-program analysis over an entire codebase.
See run.sh to see how to use it.
"""


import getopt
import glob
import os
import shutil
import sys
import time
import traceback

from icbd.util import cfa
from icbd.type_analyzer import type_checker

def usage():
    print >>sys.stderr, "Usage:"
    print >>sys.stderr, "%s [-I LIB_DIR]* [-o OUTPUT_DIR] [-p PRUNE_LINKS_AMOUNT] [-n PROJECT_NAME] [-c PLUGIN_NAME]* SOURCE_DIR" % (sys.argv[0],)
    sys.exit(-1)

ICBD_DIR = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], "I:o:p:nN:c:E:", [])
    if len(args) != 1:
        usage()
    [src_dir] = args
    src_dir = os.path.abspath(src_dir)

    lib_dirs = [
            (os.path.join(ICBD_DIR, "../../../stdlib/type_mocks"), "builtin_mocks"),
        ]
    plugins = []
    exclude_dirs = []
    output_dir = None
    prune_amount = None
    proj_name = None
    do_output = True
    for n, v in optlist:
        if n == "-o":
            if output_dir is not None:
                usage()
            output_dir = os.path.abspath(v)
        elif n == "-I":
            lib_dirs.append((os.path.abspath(os.path.expanduser(v)), os.path.basename(v)))
        elif n == "-p":
            if prune_amount is not None:
                usage()
            prune_amount = int(v)
        elif n == "-n":
            do_output = False
        elif n == "-N":
            if proj_name is not None:
                usage()
            proj_name = v
        elif n == "-c":
            plugins.append(v)
        elif n == "-E":
            exclude_dirs.append(v)
        else:
            raise Exception(n)

    import random
    random.seed(12345)

    if proj_name is None:
        proj_name = os.path.basename(src_dir)
    if prune_amount is None:
        prune_amount = 0

    if output_dir is None:
        output_dir = os.path.join("/tmp", "icbd_%s" % proj_name)

    static_dir = os.path.join(output_dir, "static")

    # Do this first to detect permissions errors
    if not os.path.isdir(static_dir):
        os.makedirs(static_dir)
    # Unfortunately glob can't expand curly braces; the expression should be *.{css,js}
    for fn in glob.glob(os.path.join(ICBD_DIR, "visualizer", "*.*s")):
        dest = os.path.join(static_dir, os.path.basename(fn))
        print "%s -> %s" % (fn, dest)
        shutil.copy(fn, dest)


    cfa.ADD_IF_ASSERTS = True

    e = type_checker.Engine()
    for path, name in lib_dirs:
        e.python_path.append(path)

    for plugin_name in plugins:
        plugin_name = "icbd.type_analyzer." + plugin_name
        m = __import__(plugin_name)
        for n in plugin_name.split('.')[1:]:
            m = getattr(m, n)
        m.load(e)

    if do_output:
        e.loadFormatter()

    for dirpath, dirnames, filenames in os.walk(src_dir, followlinks=True):
        if any(dirpath.startswith(d) for d in exclude_dirs):
            continue
        for fn in filenames:
            if fn.endswith(".py"):
                if fn == "__init__.py":
                    mname = os.path.basename(dirpath)
                else:
                    mname = fn[:-3]
                e._load(os.path.join(dirpath, fn), mname)
            else:
                with open(os.path.join(dirpath, fn)) as f:
                    l = f.readline(100).strip()
                if l.startswith("#!") and l.endswith(" python"):
                    mname = os.path.basename(fn)
                    e._load(os.path.join(dirpath, fn), mname)

    start = time.time()
    e.analyze()
    print "Took %.1f seconds to analyze" % (time.time() - start)

    def out_func(fn):
        assert fn.startswith('/')
        for dirname, name in [(src_dir, proj_name)] + lib_dirs:
            if fn.startswith(dirname):
                r = os.path.join(output_dir, name, fn[len(dirname)+1:])
                if r.endswith(".py"):
                    return r.replace(".py", ".html")
                return r + ".html"
        raise Exception(fn)

    def link_func(fn):
        out = out_func(fn)
        return os.path.join('/', *out.split('/')[prune_amount+1:])

    def output(fn):
        out_fn = out_func(fn)
        static_link_dir = os.path.join('/', *(static_dir.split('/')[prune_amount+1:]))
        try:
            html = e.format_html(fn, link_func, static_dir=static_link_dir)
        except Exception:
            print >>sys.stderr, "FAILED FORMATTING", fn
            html = "<pre>%s</pre>" % (''.join(traceback.format_exc()))
        if not os.path.isdir(os.path.dirname(out_fn)):
            os.makedirs(os.path.dirname(out_fn))
        print "%s -> %s" % (fn, out_fn)
        with open(out_fn, 'w') as f:
            f.write(html)

    print
    e.print_score(show_files=True, filter=lambda fn:fn.startswith(src_dir))
    print

    if do_output:
        for fn in e._loaded_modules:
            output(fn)

