__mixed = getattr(None, '')
__f = open('/dev/null')

def load(f):
    return __mixed
load(__f)

def loads(s):
    return __mixed
loads('')

def dump(o, f):
    return
dump(__mixed, __f)

def dumps(o):
    return ''
dumps(__mixed)
