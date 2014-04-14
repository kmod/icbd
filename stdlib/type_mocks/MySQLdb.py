class MySQLCursor(object):
    def execute(self, sql, args=[]):
        pass
    def fetchall(self):
        return [["", 1]]
    def close(self):
        pass

class MySQLConnection(object):
    def cursor(self, cursorclass=None):
        return MySQLCursor()
    def affected_rows(self):
        return 5
    def autocommit(self, flag):
        # haha hax:
        self.autocommit(True)
        return
    def close(self):
        pass
    def commit(self):
        pass


def connect(host='', user='', passwd='', db=''):
    return MySQLConnection()
