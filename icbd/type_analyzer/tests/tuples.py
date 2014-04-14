t = (1, '', object()) # 0 (int,str,object)
a = t[0] # 0 int # 4 (int,str,object)
b = t[1] # 0 str
c = t[2] # 0 object
d = t[3] # 0 <unknown> # e 4
x,y,z = t # 0 int # 2 str # 4 object # 8 (int,str,object)
x,y,z,w = t # 0 <unknown> # 2 <unknown> # 4 <unknown> # 6 <unknown> # 10 (int,str,object) # e 0

for i in (1,''): # 4 <int|str>
    i # 4 <int|str>

t = tuple() # 0 ()
t = tuple(()) # 0 ()
t = tuple((1,)) # 0 (int,)
t = tuple((1,'')) # 0 (int,str)
t = tuple((1,'',True)) # 0 (int,str,bool)

b = str in (str, list) # 0 bool
