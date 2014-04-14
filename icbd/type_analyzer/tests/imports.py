import basic # 7 module 'basic'
a = basic.a # 0 int

import sys # 7 module 'sys'
sys # 0 module 'sys'

import os.path
os # 0 module 'os'
p = path # 0 <unknown> # 4 <unknown> # e 4

from os import path
path # 0 module 'path'

import os.doesnt_exist # e 0

from foo import bar # e 0 # 5 <unknown> # 16 <unknown>
bar # 0 <unknown>

from re import search, match # 15 (str,str,int?) -> Match # 23 (str,str,int?) -> Match

import os.path as a
a # 0 module 'path'

from . import control_flow # e 0
