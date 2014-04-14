#!/usr/bin/env python
# -*- coding: utf-8 -*-

def print_time():
    import time
    print time.time()
    # print "%0.3f" % time.time()

print_time()
table = [range(1000) for i in range(1000)]
print_time()

class a(object):
  def main(self, table):
    _buffer = []
    _buffer_write = _buffer.append
    _buffer_write('<table xmlns:py="http://spitfire/">')
    _buffer_write('\n')
    for i in xrange(len(table)):
      row = table[i]
      _buffer_write('<tr>')
      _buffer_write('\n')
      for j in xrange(len(row)):
        column = row[j]
        _buffer_write('<td>')
        _buffer_write(str(column))
        _buffer_write('</td>')
        _buffer_write('\n')
      _buffer_write('</tr>')
      _buffer_write('\n')
    _buffer_write('</table>')
    _buffer_write('\n')
    print_time()
    return ''.join(_buffer)


a().main(table)
print_time()
