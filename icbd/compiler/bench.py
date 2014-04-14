#!/usr/bin/env python

import collections
import os
import subprocess
import sys
import time
import threading

class TimeoutException(Exception):
    pass

class ProcDiedException(Exception):
    pass

def check_call(*args, **kw):
    timeout = kw.pop("timeout", None)
    kw['stdout'] = subprocess.PIPE
    kw['stderr'] = subprocess.STDOUT
    if timeout is None:
        try:
            return subprocess.check_call(*args, **kw)
        except subprocess.CalledProcessError:
            raise ProcDiedException()

    done_by = time.time() + timeout
    p = subprocess.Popen(*args, **kw)
    def inner():
        p.communicate()
        p.wait()

    t = threading.Thread(target=inner)
    t.setDaemon(True)
    t.start()

    t.join(done_by - time.time())
    if p.poll() is None:
        p.terminate()
        time.sleep(.01)
        if p.poll() is None:
            p.kill()
            time.sleep(.01)
            assert p.poll() is not None
        raise TimeoutException()

    if p.poll() != 0:
        raise ProcDiedException()

MAX_RUNTIME = 5.0
MAX_CPYTHON_TIME = 30.0
MAX_BUILDTIME = 25.0
MAX_TIME = 10.0
MAX_RUNS = 5
field_width = 19

RUNNERS = []
def make_runners():
    class ICBDRunner(object):
        def make(self, fn):
            assert fn.endswith(".py")
            # check_call("rm -fv -- %(p)s.out* %(p)s*gen.ll %(p)s*opt.ll %(p)s*.s" % {'p':fn[:-3]}, shell=True)
            check_call(["make", fn[:-3] + ".out3", "OPTLEVEL=-O3"], timeout=MAX_BUILDTIME)

        def get_cmd(self, fn):
            return os.path.join('.', fn[:-3] + ".out3")

    class ShedskinRunner(object):
        def make(self, fn):
            assert fn.endswith(".py")
            check_call(["make", fn[:-3] + ".shed"], timeout=MAX_BUILDTIME)

        def get_cmd(self, fn):
            return os.path.join('.', fn[:-3] + ".shed")

    class CppRunner(object):
        def make(self, fn):
            assert fn.endswith(".py")
            cpp = fn[:-3] + "_byhand.cpp"
            if not os.path.exists(cpp):
                raise ProcDiedException()
            check_call(["g++", "-O3", "-funroll-loops", cpp, "-o", fn[:-3]], timeout=MAX_BUILDTIME)

        def get_cmd(self, fn):
            assert fn.endswith(".py")
            cpp = fn[:-3] + "_byhand.cpp"
            if not os.path.exists(cpp):
                return None
                return float("nan")
            return os.path.join('.', fn[:-3])

    class InterpretedRunner(object):
        def __init__(self, interpreter):
            self._int = interpreter
            if interpreter == "python":
                self.timeout = MAX_CPYTHON_TIME
            else:
                self.timeout = MAX_RUNTIME

        def make(self, fn):
            pass

        def get_cmd(self, fn):
            return "%s %s" % (self._int, fn)

    class CPythonRunner(InterpretedRunner):
        def __init__(self):
            super(CPythonRunner, self).__init__("python")

    class PypyRunner(InterpretedRunner):
        def __init__(self):
            super(PypyRunner, self).__init__("pypy")

    RUNNERS.append(('cpython', CPythonRunner()))
    RUNNERS.append(('pypy', PypyRunner()))
    RUNNERS.append(('shedskin', ShedskinRunner()))
    RUNNERS.append(('icbd', ICBDRunner()))
    RUNNERS.append(('cpp', CppRunner()))
make_runners()

_cfgs = {}
def get_config(fn):
    config_fn = os.path.join(os.path.dirname(fn), "tests.cfg")
    if config_fn not in _cfgs:
        if not os.path.exists(config_fn):
            _cfgs[config_fn] = None
        else:
            _cfgs[config_fn] = open(config_fn).read().split('\n')
    cfg = _cfgs[config_fn]
    if cfg is None:
        return "%(prog)s"

    bn = os.path.basename(fn)
    for l in cfg:
        if l.startswith(bn + ":"):
            cmd = l[len(bn) + 1:].strip()
            return cmd
    return "%(prog)s"

if __name__ == "__main__":
    progs = sys.argv[1:]
    if not progs:
        progs = [
                "benchmarks/micro/12.py",
                "benchmarks/micro/25.py",
                "benchmarks/micro/31.py",
                "benchmarks/micro/33.py",
                "benchmarks/micro/66.py",
                "benchmarks/cj/2012_1a_b.py",
                "benchmarks/cj/2012_2_a.py",
                "benchmarks/modified/nbody.py",
                "benchmarks/modified/raytrace.py",
                "benchmarks/modified/pystone.py",
                "benchmarks/modified/fannkuch.py",
                "benchmarks/modified/float.py",
                "benchmarks/us/tuple_gc_hell.py",
                ]
    q = collections.deque(progs)

    files = []
    while q:
        fn = q.popleft()
        if os.path.isdir(fn):
            for n in sorted(os.listdir(fn)):
                q.appendleft(os.path.join(fn, n))
        elif fn.endswith(".py"):
            cmd = get_config(fn)
            files.append((fn, cmd))
        else:
            print "Skipping", fn
    # files.sort()

    check_call(["make", "compiler", "-j4"])

    fn_len = max([len(f[0]) for f in files])

    sys.stdout.write(" " * fn_len)
    for name, runner in RUNNERS:
        sys.stdout.write(name.rjust(field_width))
    print

    for fn, runline in files:
        sys.stdout.write(fn.rjust(fn_len))
        sys.stdout.flush()

        cpython_time = None
        for name, runner in RUNNERS:
            start = time.time()
            try:
                runner.make(fn)
            except TimeoutException:
                sys.stdout.write("\033[33m" + "BT".rjust(field_width) + "\033[0m")
                sys.stdout.flush()
                continue
            except ProcDiedException:
                sys.stdout.write("\033[31m" + "BE".rjust(field_width) + "\033[0m")
                sys.stdout.flush()
                continue
            # print "%.1fms to build" % ((time.time() - start) * 1000.0)

            failed = False
            elapsed = []
            for i in xrange(MAX_RUNS):
                start = time.time()
                try:
                    prog = runner.get_cmd(os.path.basename(fn))
                    cmd = runline % {
                            'prog':prog
                            }
                    timeout = MAX_CPYTHON_TIME if name == "cpython" else MAX_RUNTIME
                    check_call(cmd, timeout=timeout, cwd=os.path.dirname(fn), shell=True)
                except TimeoutException:
                    if name == "cpython":
                        cpython_time = float("inf")
                    sys.stdout.write("\033[33m" + "RT".rjust(field_width) + "\033[0m")
                    sys.stdout.flush()
                    failed = True
                    break
                except ProcDiedException:
                    if name == "cpython":
                        cpython_time = float("inf")
                    sys.stdout.write("\033[1;31m" + "RE".rjust(field_width) + "\033[0m")
                    sys.stdout.flush()
                    failed = True
                    break
                elapsed.append(time.time() - start)
                if sum(elapsed) > MAX_TIME and len(elapsed) >= 2:
                    break

            if failed:
                continue
            runtime = min(elapsed)
            if name == "cpython":
                cpython_time = runtime
            sys.stdout.write(("%.1fms (%.2fx)" % (runtime * 1000.0, cpython_time / runtime)).rjust(field_width))
            sys.stdout.flush()
            # print "%.1fms - %.1fms (%d trials)" % (min(elapsed) * 1000.0, max(elapsed) * 1000.0, len(elapsed))
        print
