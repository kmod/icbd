import os
import re
import sys
import types
import urllib

# import inspect
# inspect.getargspec(f)

TRY_ARGS = (0, 1, 1.0, -1.0, 10.0, None, True, False, '', [], "/dev/null")
# TRY_ARGS = ()

_indent = 0
def indent(x):
    global _indent
    _indent += x
def p(*sl):
    sys.stdout.write(' '*_indent)
    for i, s in enumerate(sl):
        s = str(s).replace("\n", "\n" + " " * _indent)
        if i != len(sl) - 1:
            print s,
        else:
            print s

def _handle_literal(k, v):
    p("%s = %s" % (k, repr(v)))
    print

handle_tuple = handle_list = handle_dict = handle_bool = handle_int = handle_long = handle_str = handle_float = handle_nonetype = _handle_literal

handle_timedelta = handle_time = handle_date = handle_datetime = _handle_literal

def handle_module(k, v):
    pass

def handle_method_descriptor(k, v):
    for i, l in enumerate(docs):
        if "function:: %s(" % k in l:
            args = re.search('\((.*)\)', l).group(1)
            p("def %s(%s):" % (k, args))
            docstring = get_paragraph(i+2)
            indent(4)
            p('"""%s"""' % (docstring.strip()))
            indent(-4)

            narg = args.count(',') + 1
            found = False
            for a in TRY_ARGS:
                if found:
                    break
                for i in xrange(narg+1):
                    try:
                        r = v(*[a] * i)
                        indent(4)
                        p("return %s" % repr(r))
                        indent(-4)
                        found = True
                        break
                    except Exception:
                        pass
            print
            break
    else:
        p("def %s(*args, **kw):" % (v.__name__))
        p("    pass")
        print
handle_builtin_function_or_method = handle_method_descriptor
handle_function = handle_instancemethod = handle_method_descriptor

def get_paragraph(start):
    cur = start
    r = ""
    while docs[cur].strip():
        r += docs[cur]
        cur += 1
    return r

def handle_type(k, v):
    assert isinstance(v, type)
    p("class %s(%s):" % (k, ','.join([b.__name__ for b in v.__bases__])))

    indent(4)

    for i, l in enumerate(docs):
        if ("class:: %s\n" % k) in l:
            docstring = get_paragraph(i+3)
            p('"""%s"""' % (docstring.strip()))
            break

    attributes = set()
    if not any(not k2.startswith("_") for k2 in dir(v)):
        p("pass")

    for k2 in dir(v):
        if k2.startswith("_"):
            continue

        v2 = getattr(v, k2)
        n = type(v2).__name__.lower()
        if n == "type":
            continue
        handler = globals().get("handle_%s" % n, _handle_unknown)

        if handler == _handle_literal:
            handler(k2, v2)
        elif n in ("method_descriptor", "builtin_function_or_method", "instancemethod"):
            for i, l in enumerate(docs):
                if "classmethod:: %s.%s(" % (k, k2) in l:
                    args = re.search('\((.*)\)', l).group(1)
                    p("@classmethod")
                    if args:
                        p("def %s(cls, %s):" % (k2, args))
                    else:
                        p("def %s(cls):" % (k2,))
                    docstring = get_paragraph(i+2)
                    indent(4)
                    p('"""%s"""' % (docstring.strip()))
                    indent(-4)
                    print
                    break
                elif "method:: %s.%s(" % (k, k2) in l:
                    args = re.search('\((.*)\)', l).group(1)
                    if args:
                        p("def %s(self, %s):" % (k2, args))
                    else:
                        p("def %s(self):" % (k2,))
                    docstring = get_paragraph(i+2)
                    indent(4)
                    p('"""%s"""' % (docstring.strip()))
                    indent(-4)
                    print
                    break
                # elif "function:: %s(" % (k2) in l:
                    # args = re.search('\((.*)\)', l).group(1)
                    # p("def %s(%s):" % (k2, args))
                    # docstring = get_paragraph(i+2)
                    # indent(4)
                    # p('"""%s"""' % (docstring.strip()))
                    # indent(-4)
                    # print
                    # break
            else:
                print >>sys.stderr, "couldn't find", k, k2
        elif n == "getset_descriptor":
            for i, l in enumerate(docs):
                if "attribute:: %s.%s" % (k, k2) in l:
                    p("@property")
                    p("def %s(self):" % (k2,))
                    docstring = get_paragraph(i+2)
                    indent(4)
                    p('"""%s"""' % (docstring.strip()))
                    indent(-4)
                    print
                    break
            else:
                _handle_unknown(k2, v2)
        elif n == "member_descriptor":
            attributes.add(k2)
        else:
            _handle_unknown(k2, v2)

    for i, l in enumerate(docs):
        if ("class:: %s(" % k) in l:
            args = re.search('\((.*)\)', l).group(1)
            if args:
                p("def __init__(self, %s):" % args)
            else:
                p("def __init__(self):" % args)
            docstring = get_paragraph(i+2)
            indent(4)
            p('"""%s"""' % (docstring.strip()))
            indent(-4)

            for a in attributes:
                print >>sys.stderr, a
                for i, l in enumerate(docs):
                    if "``%s``" % a in l:
                        desc = re.search('\|([^`]*)\|', l).group(1)
                        p("    # %s" % (desc,))
                        break
                indent(4)
                p("self.%s = getattr(self, '%s')" % (a, a))
                indent(-4)

            print
            break

    print
    indent(-4)

def _handle_unknown(k, v):
    print >>sys.stderr, "Don't know how to handle", repr(v), type(v).__name__.lower()

if __name__ == "__main__":
    name = sys.argv[1]
    if not os.path.exists("/tmp/%s.txt" % name):
        s = urllib.urlopen("http://docs.python.org/_sources/library/%s.txt" % name).read()
        assert s
        open("/tmp/%s.txt" % name, "w").write(s)
    docs = open("/tmp/%s.txt" % name).readlines()

    m = __import__(name, fromlist=[''])
    print "# generated with make_mock.py\n"
    for k in dir(m):
        if k.startswith("_"):
            continue
        v = getattr(m, k)

        n = type(v).__name__.lower()
        globals().get("handle_%s" % n, _handle_unknown)(k, v)

