l1 = [1] # 0 [<bool|int>]
l2 = [''] # 0 [<bool|str>]
l3 = l1 or l2
l3.append(True)
l3 # 0 [<bool|int|str>]
