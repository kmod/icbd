#!/usr/bin/env python

import getopt
import os
import sys

from icbd.util import ast_utils, cfa
from icbd.type_analyzer import builtins, type_checker, type_system
from icbd.compiler.codegen import CodeGenerator

def main():
    # setting this to true let's us compile programs with pseudo-errors, like this:
    # while True:
    #     x = 1
    # print y
    cfa.PRUNE_UNREACHABLE_BLOCKS = True

    # This enables an experimental optimization that converts for loops into more optimizable while loops.
    # Not sure why it doesnt help at all.
    cfa.REDUCE_FORS_TO_WHILES = True

    # don't allow blocks with multiple out-edges to go to blocks with multiple in-edges
    cfa.ENFORCE_NO_MULTIMULTI = True

    type_checker.VERBOSE = False

    opts, args = getopt.getopt(sys.argv[1:], "t:p:")

    fn = args[0]
    llvm_fn = args[1]
    llvm_f = open(llvm_fn, 'w')
    c_fn = args[2]
    c_f = open(c_fn, 'w')
    if len(args) >= 4:
        d_fn = args[3]
        d_f = open(d_fn, 'w')
    else:
        d_fn = None
        d_f = None
    assert len(args) <= 4

    source = open(fn).read()
    node = ast_utils.parse(source, fn)

    pythonpath = [
            os.path.dirname(fn),
            ]
    typepath = [
            ]
    for flag, value in opts:
        if flag == '-p':
            typepath.append(value)
            pythonpath.append(value)
        elif flag == '-t':
            typepath.append(value)
        else:
            raise Exception(flag)

    c = CodeGenerator(typepath, pythonpath)
    try:
        c.compile(node, fn, llvm_f=llvm_f, c_f=c_f, deps_f=d_f)
    except:
        llvm_f.close()
        c_f.close()
        os.remove(llvm_fn)
        os.remove(c_fn)
        if d_f:
            d_f.close()
            os.remove(d_fn)
        raise

if __name__ == "__main__":
    main()
