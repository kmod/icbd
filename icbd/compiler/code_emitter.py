from cStringIO import StringIO

class CodeEmitter(object):
    def __init__(self, em):
        assert em

        self._lio = StringIO()
        self._cio = StringIO()
        self._indent = 0
        self._ntemps = {} # (prefix, suffix) -> num
        self._nplaceholders = 0
        self._replacements = {} # subfunctions can register replacements to be dealt with later (since the name of a given variable might not be known in advance, for certain loop constructs like list comprehensions)

        if isinstance(em, CodeEmitter):
            # self.mkname = lambda prefix='_v', suffix="": em.mkname(prefix="_sub"+prefix, suffix=suffix)
            self.mkname = em.mkname
            self.root_mkname = em.root_mkname
            self.llvm_head, self.llvm_tail, self.c_head, self.c_tail = em.llvm_head, em.llvm_tail, em.c_head, em.c_tail
            self._str_table = em._str_table
            self.register_replacement = em.register_replacement
            self.get_placeholder = em.get_placeholder
        else:
            self.root_mkname = self.mkname
            self.llvm_head, self.llvm_tail, self.c_head, self.c_tail = em
            self._str_table = {}

    def get_str(self, s):
        l = len(s)

        s = ''.join(['\\%02X' % ord(c) for c in s])
        # s = s.replace('\n', '\\0A')
        if s in self._str_table:
            return self._str_table[s]

        n = self.root_mkname("str_")
        self.llvm_tail.write('''@%s = internal constant [%d x i8] c"%s\\00"\n''' % (n, l + 1, s))
        self._str_table[s] = n
        return n

    def get_str_ptr(em, s):
        n = em.get_str(s)
        return "getelementptr inbounds ([%d x i8]* @%s, i32 0, i32 0)" % (len(s) + 1, n)

    def get_placeholder(self):
        self._nplaceholders += 1
        return "#!%d!#" % self._nplaceholders

    def register_replacement(self, token, s):
        id = int(token[2:-2])
        assert 1 <= id <= self._nplaceholders
        assert id not in self._replacements
        self._replacements[id] = s

    def mkname(self, prefix="_v", suffix=""):
        assert not (prefix and prefix[-1].isdigit())
        assert not (suffix and suffix[0].isdigit())
        n = self._ntemps.get((prefix, suffix), 0)
        rtn = "%s%s%s" % (prefix, n, suffix)
        self._ntemps[(prefix, suffix)] = n+1
        return rtn

    def indent(self, x):
        self._indent += x

    def get_llvm(self):
        return self._lio.getvalue().strip()

    def get_c(self):
        return self._cio.getvalue().strip()

    def pl(self, s=''):
        self.__p(self._lio, s)

    def pc(self, s=''):
        self.__p(self._cio, s)

    def __p(self, f, s):
        if s is None:
            return
        if self._indent:
            print >>f, ' '*(self._indent-1), s
        else:
            print >>f, s

