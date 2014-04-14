class StringIO(object):
    def write(self, s):
        pass

    def getvalue(self):
        return ''

    def close(self):
        pass

    def flush(self):
        pass

_t = StringIO()
_t.write('')
