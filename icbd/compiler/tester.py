#!/usr/bin/env python
import commands
import glob
import os
import Queue
import subprocess
import sys
import tempfile
import threading
import time

NUM_THREADS = 4
BUILD_ONLY = False
NOOPT = True
LIMIT_TIME = True

def compile_file(fn, version):
    assert fn.endswith(".py")
    output = fn[:-3] + ".out" + version
    make_args = ["make", output]
    if NOOPT:
        make_args += ["OPTLEVEL="]

    subprocess.check_call(make_args, stdout=open("/dev/null", 'w'), stderr=subprocess.PIPE)
    return [output]

def get_expected_output(fn):
    assert fn.endswith(".py")
    expected_fn = fn[:-3] + ".expected"
    if os.path.exists(expected_fn):
        return open(expected_fn).read()
    start = time.time()
    p = subprocess.Popen(["python", fn], stdout=subprocess.PIPE, stdin=open("/dev/null"))
    out, err = p.communicate()
    assert p.wait() == 0
    if LIMIT_TIME:
        assert time.time() - start < .2, (fn, time.time() - start)
    return out

def run_test(fn, run_prog, check_output, check_refcounts):
    r = fn.rjust(20)

    run_args = compile_file(fn, '3')
    r += "    Build succeeded"

    if not run_prog:
        r += "    (not running)"
        return r

    start = time.time()
    p = subprocess.Popen(run_args, stdout=subprocess.PIPE, stdin=open("/dev/null"))
    out, err = p.communicate()
    assert p.wait() == 0, (fn, run_args, p.wait())
    if LIMIT_TIME:
        assert time.time() - start < .1, (fn, time.time() - start)

    if check_output:
        expected = get_expected_output(fn)
        if out != expected:
            exp_fd, exp_fn = tempfile.mkstemp()
            out_fd, out_fn = tempfile.mkstemp()
            os.fdopen(exp_fd, 'w').write(expected)
            os.fdopen(out_fd, 'w').write(out)
            p = subprocess.Popen(["diff", "-a", exp_fn, out_fn], stdout=subprocess.PIPE)
            diff = p.stdout.read()
            assert p.wait() in (0, 1)
            raise Exception("Failed on %s:\n%s" % (fn, diff))
        r += "    Correct output   "
    else:
        r += "    (Ignoring output)"

    if check_refcounts:
        run_args = compile_file(fn, '2')
        p = subprocess.Popen(' '.join(run_args + ["|", "tail"]), shell=True, stdout=subprocess.PIPE, stdin=open("/dev/null"))
        while True:
            l = p.stdout.readline()
            if not l:
                break
            assert "did not get freed" not in l, (fn, l)
        r += "    Refcounts zeroed"
    else:
        r += "    (Ignoring refcounts)"

    return r

q = Queue.Queue()
cv = threading.Condition()
results = {}
quit = []
def worker_thread():
    while not quit:
        try:
            job = q.get()
            if job is None:
                break

            results[job[0]] = run_test(*job)
            with cv:
                cv.notifyAll()
        except:
            import traceback
            # traceback.print_exc()
            results[job[0]] = None
            quit.append(traceback.format_exc())
            with cv:
                cv.notifyAll()
            # os._exit(-1)

if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    start = 1
    if len(sys.argv) >= 2:
        start = int(sys.argv[1])

    if "--build-only" in sys.argv:
        BUILD_ONLY = True

    SKIP = ["tests/%d.py" % i for i in
            14, # Don't handle polymorphic functions yet (list.__getitem__)
            16, # Don't support 'map' yet
            19, # Don't handle polymorphic functions yet (list.__getitem__)
            21, # Don't handle polymorphic functions yet (list.__getitem__)
            23, # Don't handle polymorphic functions yet (list.__getitem__)
            37, # Don't support printing functions, map()
            43, # Don't support exceptions
            74, # Don't support inheritance
            76, # Don't support inheritance
            77, # Don't support this yet
            78, # This is too hard
            79, # Don't support this yet

            81, # boxes ([int], [str]) as [(int,str)] which is incorrect
            82, # This is too hard
            85, # Don't support inheritance of builtins
            87, # Don't support making lists of boxed objects
            96, # Don't support this yet
            105, # Don't support this yet
            110, # Don't support keywords yet, so can't do [].sort(reverse=True)
            114,
            ]

    DONT_RUN = ["tests/%d.py" % i for i in
            2,  # Doesn't return
            41, # does time.time
            52, # This asks for input from stdin
        ] + [
            "benchmarks/modified/pidigits.py", # Don't support arbitrary-sized longs
        ]

    IGNORE_OUTPUT = ["tests/%d.py" % i for i in (
        40, # Float formatting
        47, # Looks at sys.argv
        49, # Looks at sys.argv
        57, # Looks at time.time and time.clock
        58, # Does a bunch of type upconverting, which is an implementation difference
        60, # cPython does some simple string interning, but I don't
        66, # prints out timing
        75, # enumerate objects don't print out the same
        84, # Haven't matched this particular cPython optimization
        92, # Generator expressions aren't correctly supported
        93, # This is invalid python but currently compiles
        97, # Iterates over dict, and python does it in weird order
        99, # Don't print out instances/classes exactly like cPython yet
        )] + [
            "benchmarks/modified/raytrace.py",
            "benchmarks/modified/pystone.py",
        ]
    IGNORE_REFCOUNT = ["tests/%d.py" % i for i in (
        25, 44, # These all do too many allocs, so the output takes too long
        34, 55, # Cycle when something is in its own closure; broken
        64, # This is a linked list with a cycle in it; broken
        100, # Construct a reference cycle on purpose
        )] + [
        ]
    tests = sorted([t for t in glob.glob("tests/[0-9]*.py") if int(t[6:-3]) >= start], key=lambda t:int(t[6:-3]))
    tests += [
            # "tests/space fn.py",
            # "tests/imports_basic.py",
            ]
    big_tests = [
            "benchmarks/modified/raytrace.py",
            "benchmarks/modified/nbody.py",
            "benchmarks/modified/pystone.py",
            "benchmarks/modified/pidigits.py",
            "benchmarks/modified/float.py",
            ]
    tests += big_tests

    if "--long" in sys.argv:
        NOOPT = False
        LIMIT_TIME = False
    else:
        DONT_RUN += big_tests

    # An aborted compilation will sometimes leave 0-byte intermediate files; I've tried to get rid of them, but just do that here:
    subprocess.check_call(["find", "tests", "-size", "0", "-delete"])
    subprocess.check_call(["make", "-j4", "compiler"], stdout=open("/dev/null", 'w'), stderr=subprocess.PIPE)

    for fn in tests:
        if fn in SKIP:
            continue
        if BUILD_ONLY:
            q.put((fn, 0,0,0))
        else:
            q.put((fn, fn not in DONT_RUN, fn not in IGNORE_OUTPUT, fn not in IGNORE_REFCOUNT))

    threads = []
    for i in xrange(NUM_THREADS):
        t = threading.Thread(target=worker_thread)
        t.setDaemon(True)
        t.start()
        threads.append(t)
        q.put(None)

    for fn in tests:
        if fn in SKIP:
            print fn.rjust(20),
            print "   Skipping"
            continue

        with cv:
            while fn not in results:
                try:
                    cv.wait(1)
                except KeyboardInterrupt:
                    print >>sys.stderr, "Interrupted"
                    sys.exit(1)

        if results[fn] is None:
            assert quit
            print quit[0]
            break
        print results[fn]

    for t in threads:
        t.join()
