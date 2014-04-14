class Popen(object):
    def __init__(self, args, **kw):
        self.stdin = self.stderr = self.stdout = open("/dev/null")

    def communicate(self):
        return "",""

    def wait(self):
        return 0

    def poll(self):
        if self:
            return 0
        return None

PIPE=-1
STDOUT=-2
