import cStringIO
import os
import pygments
import re
import simplejson

from pygments.formatter import Formatter
from pygments.lexers import PythonLexer
from pygments.token import STANDARD_TYPES, Token


class AnnotatingHtmlFormatter(Formatter):
    _html_escape_table = {
        ord('&'): u'&amp;',
        ord('<'): u'&lt;',
        ord('>'): u'&gt;',
        ord('"'): u'&quot;',
        ord("'"): u'&#39;',
    }

    def __init__(self, type_info, error_info, links):
        self.type_info = type_info
        self.type_positions = set((row, col) for (row, col, s) in type_info)
        self.links = links
        self.error_info = error_info + []
        self.original_errors = error_info
        self.current_errors = []
        self.comments = set() # set of lines with comments
        super(AnnotatingHtmlFormatter, self).__init__()

    def _have_type_info_for_pos(self, pos):
        return pos in self.type_positions

    def _num_errors_start(self, pos):
        errors_found = 0
        while self.error_info:
            row, start, end, error_str = self.error_info[0]
            if row == pos[0] and pos[1] >= start and pos[1] < end:
                self.current_errors.append(self.error_info.pop(0))
                errors_found += 1
            else:
                break

        return errors_found

    def _num_errors_end(self, pos):
        errors_ended = 0
        while self.current_errors:
            row, start, end, error_str = self.current_errors[0]
            if row != pos[0] or pos[1] >= end:
                self.current_errors.pop(0)
                errors_ended += 1
            else:
                break

        return errors_ended

    def _errors_for_line(self, lineno):
        return [error for error in self.original_errors if error[0] == lineno]

    def _output_errors_for_line(self, lineno, outfile):
        comments = []
        for row, start, end, error_str in self._errors_for_line(lineno):
            comments.append(error_str)

        if comments:
            outfile.write('<span class="error_comment">')
            outfile.write(' ' + ', '.join(comments))
            outfile.write('</span>')

    def _output_token(self, ttype, value, pos, outfile):
        # Manually split things like the "os.path" in "import os.path" into separate tokens so we can annotate them separately
        if ttype == Token.Name.Namespace and '.' in value:
            names = value.split('.')
            r, c = pos
            for i, n in enumerate(names):
                if i:
                    self._output_token(Token.Text, u'.', (r, c), outfile)
                    c += 1
                self._output_token(Token.Name.Namespace, n, (r, c), outfile)
                c += len(n)
            return

        outfile.write('<span class="error">' * self._num_errors_start(pos))

        outfile.write('</span>' * self._num_errors_end(pos))

        if ttype == Token.Text and pos[1] > 0:
            if '\n' in value:
                outfile.write('</span>')
                self.current_errors = []

        id_str = ''
        if self._have_type_info_for_pos(pos):
            id_str = ' id="%d_%d"' % pos

        def output_preview(should_slide=False):
            slide_class = ' slide' if should_slide else ''
            outfile.write('<span class="anno_preview%s" id="col_%d"></span>' % (slide_class, pos[0]))
            self._output_errors_for_line(pos[0], outfile)

        # This currently outputs errors and annotations before comments
        if ttype == Token.Comment and pos[1] > 0:
            self.comments.add(pos[0])
            output_preview(True)
        elif ttype == Token.Text and pos[1] > 0 and pos[0] not in self.comments:
            try:
                value.index('\n')
                should_slide = len(self._errors_for_line(pos[0])) > 0
                output_preview(should_slide)
            except ValueError:
                pass
            
        cls_str = ''
        cls = STANDARD_TYPES.get(ttype)
        if cls or id_str:
            cls_str = ' class="'
            if id_str:
                cls_str += 'anno '
            if cls:
                cls_str += cls
            cls_str += '"'

        if pos in self.links:
            outfile.write("<a href='%s'>" % self.links[pos])

        if cls_str or id_str:
            outfile.write('<span%s%s>' % (cls_str, id_str))

        translated_val = value.translate(self._html_escape_table)
        outfile.write(translated_val.encode("utf8"))

        if cls:
            outfile.write('</span>')

        if pos in self.links:
            outfile.write("</a>")

    def format(self, tokensource, outfile):
        col = 1
        row = 0
        outfile.write('<div class="highlight"><pre><a name="line1"/>\n')
        for ttype, value in tokensource:
            self._output_token(ttype, value, (col, row), outfile)

            # print ttype, len(value), value
            if ttype in (Token.Text, Token.Literal.String.Doc, Token.Literal.String, Token.Literal.String.Escape):
                last_row = row
                for c in value:
                    if c == '\n':
                        col += 1
                        outfile.write("<a name='line%d'/>" % col)
                        last_row = 0
                    else:
                        last_row += 1
                row = last_row
            else:
                row += len(value)

        outfile.write('</pre></div>')


def do_replace(val):
    val = val.replace('->', '&rarr;')
    val = val.replace('<', '&lt;')
    val = val.replace('>', '&gt;')
    return val
def build_type_table(type_info):
    table = {}
    for col, row, val in type_info:
        key = '%d_%d' % (col, row)
        table[key] = do_replace(val)

    return table


def annotate(src, type_info, error_info, link_info, static_dir=None):
    if static_dir is None:
        static_dir = os.path.dirname(os.path.abspath(__file__))

    src_code = open(src).read()

    error_info = [(a,b,c,do_replace(s)) for (a,b,c,s) in error_info]
    html_formatter = AnnotatingHtmlFormatter(type_info, error_info, link_info)
    outfile = cStringIO.StringIO()
    pygments.highlight(src_code, PythonLexer(), html_formatter, outfile)
    formatted = outfile.getvalue()

    type_table = build_type_table(type_info)
    type_table_str = '<script> type_table = ' + simplejson.dumps(type_table) + ';</script>'

    res = (tmpl_head % (static_dir, static_dir, static_dir)) + formatted + type_table_str + tmpl_tail

    return res

tmpl_head = """\
<html>
<head>
    <script src="%s/jquery.min.js"></script>
    <script src="%s/annotate.js"></script>
    <link href="%s/default.css" rel="stylesheet" type="text/css">
</head>
<body>
"""

tmpl_tail = """
</body>
</html>
"""

example_type_info = [(1, 5, '<unknown>'), (1, 14, '<unknown>'), (2, 7, '<unknown>'), (3, 7, '<module sys>'), (5, 0, '[num]'), (5, 4, '(num) -> [num]'), (6, 0, '[num]'), (6, 2, '(num) -> None'), (7, 0, '[num]'), (7, 2, '(num) -> None')]
example_error_info = [(7, 0, 12, 'Argument error: expected num but got str')]
example_links = {(1,5):"http://www.google.com/"}

def annotate_example():
    annotate('example.py', example_type_info, example_error_info, example_links)
