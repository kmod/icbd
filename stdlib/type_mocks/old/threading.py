class Lock(object):
    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        pass

class Condition(object):
    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        pass

class Thread(object):
    pass
