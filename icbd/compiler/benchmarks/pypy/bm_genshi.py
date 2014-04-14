
import time
import util
import optparse


from genshi.template import MarkupTemplate, NewTextTemplate

BIGTABLE_XML = """\
<table xmlns:py="http://genshi.edgewall.org/">
<tr py:for="row in table">
<td py:for="c in row.values()" py:content="c"/>
</tr>
</table>
"""

BIGTABLE_TEXT = """\
<table>
{% for row in table %}<tr>
{% for c in row.values() %}<td>$c</td>{% end %}
</tr>{% end %}
</table>
"""


def main(n, bench):
    tmpl_cls, tmpl_str = {
        'xml': (MarkupTemplate, BIGTABLE_XML),
        'text': (NewTextTemplate, BIGTABLE_TEXT),
        }[bench]
    tmpl = tmpl_cls(tmpl_str)
    context = {'table':
               [dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9, j=10)
                for x in range(1000)]}
    l = []
    for k in range(n):
        t0 = time.time()
        stream = tmpl.generate(**context)
        stream.render()
        l.append(time.time() - t0)
    return l

if __name__ == '__main__':
    parser = optparse.OptionParser(
        usage="%prog [options]",
        description="Test the performance of the Genshi benchmark")
    parser.add_option('--benchmark', action='store', default=None,
                      help='select a benchmark name')
    util.add_standard_options_to(parser)
    options, args = parser.parse_args()
    util.run_benchmark(options, options.num_runs, main, options.benchmark)
