#!/usr/bin/env python

"""Some simple microbenchmarks for Python's threading support.

Current microbenchmarks:
    - *_count: count down from a given large number. Example used by David
               Beazley in his talk on the GIL (http://blip.tv/file/2232410). The
               iterative version is named iterative_count, the threaded version
               is threaded_count.

Example usage:
    ./bm_threading.py --num_threads=8 --check_interval=1000 threaded_count
"""

# Python imports
import optparse
import sys
import threading
import time

# Local imports
import util


def count(iterations=1000000):
    """Count down from a given starting point."""
    while iterations > 0:
        iterations -= 1


def test_iterative_count(iterations, num_threads):
    # Warm up.
    count(1000)

    times = []
    for _ in xrange(iterations):
        t0 = time.time()
        for _ in xrange(num_threads):
            count()
        t1 = time.time()
        times.append(t1 - t0)
    return times


def test_threaded_count(iterations, num_threads):
    # Warm up.
    count(1000)

    times = []
    for _ in xrange(iterations):
        threads = [threading.Thread(target=count) for _ in xrange(num_threads)]
        t0 = time.time()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        t1 = time.time()
        times.append(t1 - t0)
    return times


if __name__ == "__main__":
    parser = optparse.OptionParser(
        usage="%prog [options] benchmark_name",
        description="Test the performance of Python's threads.")
    parser.add_option("--num_threads", action="store", type="int", default=2,
                      dest="num_threads", help="Number of threads to test.")
    parser.add_option("--check_interval", action="store", type="int",
                      default=sys.getcheckinterval(),
                      dest="check_interval",
                      help="Value to pass to sys.setcheckinterval().")
    util.add_standard_options_to(parser)
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments")

    bm_name = args[0].lower()
    func = globals().get("test_" + bm_name)
    if not func:
        parser.error("unknown benchmark: %s" % bm_name)

    sys.setcheckinterval(options.check_interval)
    util.run_benchmark(options, options.num_runs, func, options.num_threads)
