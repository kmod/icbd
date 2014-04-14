"""
know that some blocks will never get exited successfully, and modify the CFG accordingly
"""

def w():
    def t():
        return True

    if t():
        x = 0
    else:
        raise Exception()
    print x

    for i in xrange(5):
        y = i
        if t():
            break
    else:
        assert 0
    print y
