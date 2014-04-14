
import sys
import os
import util
import time
import optparse
from StringIO import StringIO

def relative(*args):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)

class FakePsyco(object):
    def bind(self, *args, **kwargs):
        pass
sys.modules["psyco"] = FakePsyco()

testdir = relative('..', 'unladen_swallow', 'lib', 'spitfire', 'tests', 'perf')
sys.path.insert(0, testdir)
sys.path.insert(0, relative('..', 'unladen_swallow', 'lib', 'spitfire'))
import bigtable
# bummer, timeit module is stupid
from bigtable import test_python_cstringio, test_spitfire_o4, test_spitfire

def runtest(n, benchmark):
    times = []
    for i in range(n):
        sys.stdout = StringIO()
        bigtable.run([benchmark], 100)
        times.append(float(sys.stdout.getvalue().split(" ")[-2]))
        sys.stdout = sys.__stdout__
    return times

if __name__ == '__main__':
    parser = optparse.OptionParser(
        usage="%prog [options]",
        description="Test the performance of the spitfire benchmark")
    parser.add_option('--benchmark', type="choice",
                      choices=['python_cstringio', 'spitfire_o4'],
                      default="spitfire_o4",
                      help="choose between cstringio and spitfire_o4")
    util.add_standard_options_to(parser)
    options, args = parser.parse_args(sys.argv)
    util.run_benchmark(options, options.num_runs, runtest, options.benchmark)
