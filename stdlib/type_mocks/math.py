# generated with make_mock.py

def acos(x):
    """Return the arc cosine of *x*, in radians."""
    return 1.5707963267948966

def acosh(x):
    """Return the inverse hyperbolic cosine of *x*."""
    return 0.0

def asin(x):
    """Return the arc sine of *x*, in radians."""
    return 0.0

def asinh(x):
    """Return the inverse hyperbolic sine of *x*."""
    return 0.0

def atan(x):
    """Return the arc tangent of *x*, in radians."""
    return 0.0

def atan2(y, x):
    """Return ``atan(y / x)``, in radians. The result is between ``-pi`` and ``pi``.
       The vector in the plane from the origin to point ``(x, y)`` makes this angle
       with the positive X axis. The point of :func:`atan2` is that the signs of both
       inputs are known to it, so it can compute the correct quadrant for the angle.
       For example, ``atan(1)`` and ``atan2(1, 1)`` are both ``pi/4``, but ``atan2(-1,
       -1)`` is ``-3*pi/4``."""
    return 0.0

def atanh(x):
    """Return the inverse hyperbolic tangent of *x*."""
    return 0.0

def ceil(x):
    """Return the ceiling of *x* as a float, the smallest integer value greater than or
       equal to *x*."""
    return 0.0

def copysign(x, y):
    """Return *x* with the sign of *y*.  On a platform that supports
       signed zeros, ``copysign(1.0, -0.0)`` returns *-1.0*."""
    return 0.0

def cos(x):
    """Return the cosine of *x* radians."""
    return 1.0
cos(0.0)

def cosh(x):
    """Return the hyperbolic cosine of *x*."""
    return 1.0

def degrees(x):
    """Converts angle *x* from radians to degrees."""
    return 0.0

e = 2.718281828459045

def erf(x):
    """Return the error function at *x*."""
    return 0.0

def erfc(x):
    """Return the complementary error function at *x*."""
    return 1.0

def exp(x):
    """Return ``e**x``."""
    return 1.0

def expm1(x):
    """Return ``e**x - 1``.  For small floats *x*, the subtraction in
       ``exp(x) - 1`` can result in a significant loss of precision; the
       :func:`expm1` function provides a way to compute this quantity to
       full precision::"""
    return 0.0

def fabs(x):
    """Return the absolute value of *x*."""
    return 0.0

def factorial(x):
    """Return *x* factorial.  Raises :exc:`ValueError` if *x* is not integral or
       is negative."""
    return 1

def floor(x):
    """Return the floor of *x* as a float, the largest integer value less than or equal
       to *x*."""
    return 0.0

def fmod(x, y):
    """Return ``fmod(x, y)``, as defined by the platform C library. Note that the
       Python expression ``x % y`` may not return the same result.  The intent of the C
       standard is that ``fmod(x, y)`` be exactly (mathematically; to infinite
       precision) equal to ``x - n*y`` for some integer *n* such that the result has
       the same sign as *x* and magnitude less than ``abs(y)``.  Python's ``x % y``
       returns a result with the sign of *y* instead, and may not be exactly computable
       for float arguments. For example, ``fmod(-1e-100, 1e100)`` is ``-1e-100``, but
       the result of Python's ``-1e-100 % 1e100`` is ``1e100-1e-100``, which cannot be
       represented exactly as a float, and rounds to the surprising ``1e100``.  For
       this reason, function :func:`fmod` is generally preferred when working with
       floats, while Python's ``x % y`` is preferred when working with integers."""
    return 0.0

def frexp(x):
    """Return the mantissa and exponent of *x* as the pair ``(m, e)``.  *m* is a float
       and *e* is an integer such that ``x == m * 2**e`` exactly. If *x* is zero,
       returns ``(0.0, 0)``, otherwise ``0.5 <= abs(m) < 1``.  This is used to "pick
       apart" the internal representation of a float in a portable way."""
    return (0.0, 0)

def fsum(iterable):
    """Return an accurate floating point sum of values in the iterable.  Avoids
       loss of precision by tracking multiple intermediate partial sums::"""
    return 0.0

def gamma(x):
    """Return the Gamma function at *x*."""
    return 1.0

def hypot(x, y):
    """Return the Euclidean norm, ``sqrt(x*x + y*y)``. This is the length of the vector
       from the origin to point ``(x, y)``."""
    return 0.0

def isinf(x):
    """Check if the float *x* is positive or negative infinity."""
    return False

def isnan(x):
    """Check if the float *x* is a NaN (not a number).  For more information
       on NaNs, see the IEEE 754 standards."""
    return False

def ldexp(x, i):
    """Return ``x * (2**i)``.  This is essentially the inverse of function
       :func:`frexp`."""
    return 0.0

def lgamma(x):
    """Return the natural logarithm of the absolute value of the Gamma
       function at *x*."""
    return 0.0

def log(x, base=e):
    """With one argument, return the natural logarithm of *x* (to base *e*)."""
    return 1.0

def log10(x):
    """Return the base-10 logarithm of *x*.  This is usually more accurate
       than ``log(x, 10)``."""
    return 0.0

def log1p(x):
    """Return the natural logarithm of *1+x* (base *e*). The
       result is calculated in a way which is accurate for *x* near zero."""
    return 0.0

def modf(x):
    """Return the fractional and integer parts of *x*.  Both results carry the sign
       of *x* and are floats."""
    return (0.0, 0.0)

pi = 3.141592653589793

def pow(x, y):
    """Return ``x`` raised to the power ``y``.  Exceptional cases follow
       Annex 'F' of the C99 standard as far as possible.  In particular,
       ``pow(1.0, x)`` and ``pow(x, 0.0)`` always return ``1.0``, even
       when ``x`` is a zero or a NaN.  If both ``x`` and ``y`` are finite,
       ``x`` is negative, and ``y`` is not an integer then ``pow(x, y)``
       is undefined, and raises :exc:`ValueError`."""
    return 1.0

def radians(x):
    """Converts angle *x* from degrees to radians."""
    return 0.0

def sin(x):
    """Return the sine of *x* radians."""
    return 0.0
sin(0.0)

def sinh(x):
    """Return the hyperbolic sine of *x*."""
    return 0.0

def sqrt(x):
    """Return the square root of *x*."""
    return 0.0
sqrt(0.0)

def tan(x):
    """Return the tangent of *x* radians."""
    return 0.0
tan(0.0)

def tanh(x):
    """Return the hyperbolic tangent of *x*."""
    return 0.0

def trunc(x):
    """Return the :class:`Real` value *x* truncated to an :class:`Integral` (usually
       a long integer).  Uses the ``__trunc__`` method."""
    return 0




# temporary hax:
def _itof(x):
    return 1.0

def _ftoi(x):
    return 1

