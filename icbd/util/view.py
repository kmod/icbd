import pstats
import sys

# Profile command:
# time python -m cProfile -o prof.out dbops.py

if __name__ == "__main__":
    fn = sys.argv[1]
    if len(sys.argv) > 2:
        name = sys.argv[2]
    else:
        name = "_fill_buffer"

    p = pstats.Stats(fn)
    print '=' * 80
    p.sort_stats("time").print_stats(name, 30)
    print '=' * 80
    p.sort_stats("time").print_callers(name, 2)
    print '=' * 80
    p.sort_stats("time").print_callees(name, 2)
    print '=' * 80
