import cStringIO
import os
import simplejson

import pygments
from pygments.formatter import Formatter
from pygments.lexers import PythonLexer
from pygments.token import STANDARD_TYPES, Token

from icbd.type_analyzer.type_system import Union, ClassType, UserClassType

class BrowserFormatter(Formatter):
    _html_escape_table = {
        ord('&'): u'&amp;',
        ord('<'): u'&lt;',
        ord('>'): u'&gt;',
        ord('"'): u'&quot;',
        ord("'"): u'&#39;',
    }

    def __init__(self, pos_nodes, node_types):
        super(BrowserFormatter, self).__init__()
        self.pos_nodes = pos_nodes
        self.node_types = node_types

        self.all_types = []
        self.type_idxs = {}

    def _get_type_idx(self, t):
        if isinstance(t, Union):
            return map(self._get_type_idx, t.types())
        if t not in self.type_idxs:
            self.type_idxs[t] = len(self.type_idxs)
            self.all_types.append(t)
        return self.type_idxs[t]

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

        if ttype == Token.Text and pos[1] > 0:
            if '\n' in value:
                outfile.write('</span>')
                self.current_errors = []

        id_str = ' id="%d_%d"' % pos

        cls_str = ''
        cls = STANDARD_TYPES.get(ttype)
        classes = []
        if cls:
            classes.append(cls)
        type_idx = ''
        if ttype in Token.Name:
            classes.append("anno")
            classes.append("usedef-" + value.encode("base64").replace('=', '').replace('\n', ''))

            # print pos, ttype
            node = self.pos_nodes.get(pos, None)
            u = self.node_types.get(node, None)
            if u:
                type_idx = ' type_idx="%s"' % ','.join(str(self._get_type_idx(t)) for t in u.types())
            else:
                print "missed", pos, node
        if classes:
            cls_str = ' class="%s"' % ' '.join(classes)

        outfile.write('<span%s%s%s>' % (cls_str, id_str, type_idx))

        translated_val = value.translate(self._html_escape_table)
        outfile.write(translated_val.encode("utf8"))

        outfile.write('</span>')

    def format(self, tokensource, outfile):
        row = 1
        col = 0
        outfile.write('<div class="highlight"><pre><a name="line1"/>')
        for ttype, value in tokensource:
            self._output_token(ttype, value, (row, col), outfile)

            # print ttype, len(value), value
            if ttype in (Token.Text, Token.Literal.String.Doc, Token.Literal.String, Token.Literal.String.Escape):
                last_col = col
                for c in value:
                    if c == '\n':
                        row += 1
                        outfile.write("<a name='line%d'></a>" % row)
                        last_col = 0
                    else:
                        last_col += 1
                col = last_col
            else:
                col += len(value)
        outfile.write('</pre></div>')

        type_table = {}
        class_table = {}
        instance_table = {}

        idx = 0
        while idx < len(self.all_types):
            t = self.all_types[idx]
            type_table[idx] = t.display().decode("utf8").translate(self._html_escape_table)
            if isinstance(t, ClassType):
                class_table[idx] = {}
                class_table[idx]['cls_attrs'] = {attr:self._get_type_idx(t2) for (attr, t2) in t._attributes.iteritems()}
                if isinstance(t, UserClassType):
                    class_table[idx]['inst_attrs'] = {attr:self._get_type_idx(t2) for (attr, t2) in t._instance._attrs.iteritems()}
                    instance_table[self._get_type_idx(t._instance)] = idx
            idx += 1
        outfile.write('<script> type_table = ' + simplejson.dumps(type_table) + '; class_table = ' + simplejson.dumps(class_table) + '; instance_table = ' + simplejson.dumps(instance_table) + ';</script>')

TMPL = """
<html>
<head>
    <script src="%(static_dir)s/jquery.min.js"></script>
    <script src="%(static_dir)s/browser.js"></script>
    <link href="%(static_dir)s/tokens.css" rel="stylesheet" type="text/css">
    <link href="%(static_dir)s/style.css" rel="stylesheet" type="text/css">
</head>
<body>
<div id="container">
<div id="content">
%(formatted)s
</div>
</div>
<div id="sidebar-container">
<div id="sidebar">
testing
</div>
</div>
</body>
</html>
"""
class SourceBrowserOutputPass(object):
    def __init__(self, main_fn):
        self.main_fn = main_fn

    def run(self, cb):
        formatter = BrowserFormatter(cb.pos_to_token['__main__'], cb.node_types)
        src_code = open(self.main_fn).read()
        outfile = cStringIO.StringIO()
        pygments.highlight(src_code, PythonLexer(), formatter, outfile)
        formatted = outfile.getvalue()
        out = TMPL % {
                'formatted': formatted,
                # 'static_dir': os.path.abspath(os.path.join(os.path.dirname(__file__), '../type_analyzer/visualizer')),
                'static_dir': os.path.abspath(os.path.dirname(__file__)),
                }
        print >>open("/tmp/out.html", 'w'), out

