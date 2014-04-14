from __future__ import with_statement

from threading import Lock

def f():
    with open("") as f: # 21 file
        pass

with Lock() as l: # 15 Lock
    Lock = None
