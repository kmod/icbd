#!/usr/bin/env python

"""
shedskin has a bad habit of spewing out intermediate files
this script wraps it to just take a .py file and produce an executable
"""

import os
import shutil
import subprocess
import sys
import tempfile

if __name__ == "__main__":
    infile, outfile = sys.argv[1:]
    assert infile.endswith(".py")

    tempdir = tempfile.mkdtemp(prefix="shedskin")
    intemp = os.path.join(tempdir, os.path.basename(infile))
    outtemp = os.path.join(tempdir, os.path.basename(infile[:-3]))

    try:
        shutil.copy(infile, intemp)
        subprocess.check_call(["shedskin", "-l", os.path.basename(intemp)], cwd=tempdir)

        # This is technically a sub-make, but we don't really care that it is because we want to treat shedder.py as a single command
        # Unsetting MAKEFLAGS makes sure that shedskin is built the same way regardless of where shedder.py is run
        environ = dict(os.environ)
        environ.pop("MAKEFLAGS", None)

        subprocess.check_call(["make", os.path.basename(outtemp), "CC=/usr/lib/gcc-snapshot/bin/g++"], cwd=tempdir, env=environ)
        shutil.copy(outtemp, outfile)
    finally:
        shutil.rmtree(tempdir)
