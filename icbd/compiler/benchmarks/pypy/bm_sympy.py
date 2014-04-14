
from sympy import expand, symbols, integrate, tan, summation
from sympy.core.cache import clear_cache
import time

def bench_expand():
    x, y, z = symbols('x y z')
    expand((1+x+y+z)**20)

def bench_integrate():
    x, y = symbols('x y')
    f = (1 / tan(x)) ** 10
    return integrate(f, x)

def bench_sum():
    x, i = symbols('x i')
    summation(x**i/i, (i, 1, 400))

def bench_str():
    x, y, z = symbols('x y z')
    str(expand((x+2*y+3*z)**30))

def main(n, bench):
    func = globals()['bench_' + bench]
    l = []
    for i in range(n):
        clear_cache()
        t0 = time.time()
        func()
        l.append(time.time() - t0)
    return l

if __name__ == '__main__':
    import util, optparse
    parser = optparse.OptionParser(
        usage="%prog [options]",
        description="Test the performance of the Go benchmark")
    parser.add_option('--benchmark', action='store', default=None,
                      help='select a benchmark name')
    util.add_standard_options_to(parser)
    options, args = parser.parse_args()
    util.run_benchmark(options, options.num_runs, main, options.benchmark)
