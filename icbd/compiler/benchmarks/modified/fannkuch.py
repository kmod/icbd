# -*- coding: utf-8 -*-
# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
#
# contributed by Sokolov Yura
# modified by Tupteq

import time

def range_(start, end):
    rtn = []
    for i in xrange(start,end):
        rtn.append(i)
    return rtn

def fannkuch(n):
    count = range_(1, n+1)
    max_flips = 0
    m = n-1
    r = n
    check = 0
    perm1 = range(n)
    perm = range(n)
    perm1_ins = perm1.insert
    perm1_pop = perm1.pop

    while 1:
        if check < 30:
            #print "".join(str(i+1) for i in perm1)
            check += 1

        while r != 1:
            count[r-1] = r
            r -= 1

        if perm1[0] != 0 and perm1[m] != m:
            perm = perm1[:]
            flips_count = 0
            k = perm[0]
            while k:
                perm[:k+1] = perm[k::-1]
                flips_count += 1
                k = perm[0]

            if flips_count > max_flips:
                max_flips = flips_count

        while r != n:
            perm1_ins(r, perm1_pop(0))
            count[r] -= 1
            if count[r] > 0:
                break
            r += 1
        else:
            return max_flips

DEFAULT_ARG = 10

def main(n):
    times = []
    for i in range(n):
        for j in xrange(2, DEFAULT_ARG):
            print fannkuch(j)
    return times

main(2)
