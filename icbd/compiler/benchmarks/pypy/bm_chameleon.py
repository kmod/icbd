
from chameleon import PageTemplate

BIGTABLE_ZPT = """\
<table xmlns="http://www.w3.org/1999/xhtml"
xmlns:tal="http://xml.zope.org/namespaces/tal">
<tr tal:repeat="row python: options['table']">
<td tal:repeat="c python: row.values()">
<span tal:define="d python: c + 1"
tal:attributes="class python: 'column-' + unicode(d)"
tal:content="python: d" />
</td>
</tr>
</table>"""

def main(n):
    tmpl = PageTemplate(BIGTABLE_ZPT)
    options = {'table': [dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9, j=10)
                         for x in range(1000)]}
    import time
    l = []
    for k in range(n):
        t0 = time.time()
        tmpl(options=options)
        l.append(time.time() - t0)
    return l

if __name__ == '__main__':
    import util, optparse
    parser = optparse.OptionParser(
        usage="%prog [options]",
        description="Test the performance of the Go benchmark")
    util.add_standard_options_to(parser)
    options, args = parser.parse_args()

    util.run_benchmark(options, options.num_runs, main)


