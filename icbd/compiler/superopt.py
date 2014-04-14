#!/usr/bin/env python

import os
import subprocess
import sys

def clean(l):
    if ';' in l:
        return l[:l.find(';')].strip()
    return l.strip()

if __name__ == "__main__":
    opt = os.environ.get("OPT", "opt")
    optlevel = os.environ.get("OPTLEVEL")
    load = os.environ.get("LOAD", "").split(":")
    infile = sys.argv[1]
    assert os.path.exists(infile)

    last = open(infile).read()
    prev_lines = []
    last_lines = last.split('\n')
    if last_lines[0].startswith("; ModuleID ="):
        last_lines.pop(0)
    MAX_ITERS = 10
    iters = 0
    # print >>sys.stderr, len(last_lines)
    while True:

        iters += 1

        args = [opt, "-S", "-o", "-"]
        for l in load:
            args += ["-load", l]
        if optlevel:
            args += optlevel.split()

        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate(last)
        assert p.wait() == 0
        out_lines = out.split('\n')
        # print >>sys.stderr, len(out_lines)

        if len(out_lines) == len(last_lines) or len(out_lines) == len(prev_lines):
            # This heuristic seems to work
            eq = True
        else:
            eq = False

        if eq or iters >= MAX_ITERS:
            break
        last = out
        prev_lines = last_lines
        last_lines = out_lines

    print >>sys.stderr, "finished after %d iterations" % (iters,)
    sys.stderr.flush()
    print last
