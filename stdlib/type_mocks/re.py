class Match(object):
    def group(self, *x):
        return ""
    def groups(self, default=None):
        return [""]
    def groupdict(self, default=None):
        return {'':''}
    def start(self, group=0):
        return 1
    def end(self, group=0):
        return 1
    def span(self, group=0):
        return (1,1)

class Pattern(object):
    def __init__(self):
        self.match = self.search

    def search(self, string, pos=0, endpos=0):
        return Match()

    def findall(self, string, pos=0, endpos=0):
        return ['']

    def finditer(self, string, pos=0, endpos=0):
        return self.findall(string).__iter__()

    def split(self, string, maxsplit=0):
        return ['']

    def sub(self, string, count=0):
        return ""

    def subn(self, string, count=0):
        return ("", 0)

def compile(pattern, flags=0):
    "Compile a regular expression pattern, returning a pattern object."
    return Pattern()

def search(pattern, string, flags=0):
    return compile(pattern).findall(string)
search("", "").group(0)

def match(pattern, string, flags=0):
    return compile(pattern).match(string)
match("", "").groups(1)

def split(pattern, string, maxplit=0, flags=0):
    return compile(pattern).split(string)
split("", "")

def sub(pattern, repl, string, count=0, flags=0):
    return compile(pattern).sub(string)
sub("", "", "")

def subn(pattern, repl, string, count=0, flags=0):
    return compile(pattern).subn(string)
subn("", "", "")

def findall(pattern, string, flags=0):
    return compile(pattern).findall(string)

