import multi_module_target as mmt
from multi_module_target import t

mmt.x = 2 # 0 module 'multi_module_target' # 4 int
x = mmt.f() # 0 int # 8 () -> int

y = mmt.y # 0 str # 8 str
y2 = mmt.y2 # 0 None # 9 None
mmt.k("") # 4 (str) -> None

t # 0 int
