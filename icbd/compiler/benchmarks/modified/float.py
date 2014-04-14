#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import sin, cos, sqrt
import time

class Point(object):

    def __init__(self, i):
        self.x = x = sin(i)
        self.y = cos(i) * 3
        self.z = (x * x) / 2

    def __repr__(self):
        return "<Point: x=%s, y=%s, z=%s>" % (self.x, self.y, self.z)

    def normalize(self):
        x = self.x
        y = self.y
        z = self.z
        norm = sqrt(x * x + y * y + z * z)
        self.x /= norm
        self.y /= norm
        self.z /= norm

    def maximize(self, other):
        self.x = self.x if self.x > other.x else other.x
        self.y = self.y if self.y > other.y else other.y
        self.z = self.z if self.z > other.z else other.z
        return self


def maximize(points):
    next = points[0]
    for p in points[1:]:
        next = next.maximize(p)
    return next

def benchmark(n):
    points = []
    for i in xrange(n):
        points.append(Point(i))
    for p in points:
        p.normalize()
    return maximize(points)

POINTS = 100000

def main(arg):
    # XXX warmup
    
    times = []
    for i in xrange(arg):
        t0 = time.time()
        print benchmark(POINTS)
        tk = time.time()
        times.append(tk - t0)

main(10)
