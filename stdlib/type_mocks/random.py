# generated with make_mock.py

BPF = 53

LOG4 = 1.3862943611198906

NV_MAGICCONST = 1.7155277699214135

RECIP_BPF = 1.1102230246251565e-16

class Random(object):

    VERSION = 3


SG_MAGICCONST = 2.504077396776274

class SystemRandom(Random):

    VERSION = 3

    def __init__(self, seed=0):
        """Class that uses the :func:`os.urandom` function for generating random numbers
           from sources provided by the operating system. Not available on all systems.
           Does not rely on software state and sequences are not reproducible. Accordingly,
           the :meth:`seed` and :meth:`jumpahead` methods have no effect and are ignored.
           The :meth:`getstate` and :meth:`setstate` methods raise
           :exc:`NotImplementedError` if called."""


TWOPI = 6.283185307179586

class WichmannHill(Random):

    VERSION = 1

    def __init__(self, seed=0):
        """Class that implements the Wichmann-Hill algorithm as the core generator. Has all
           of the same methods as :class:`Random` plus the :meth:`whseed` method described
           below.  Because this class is implemented in pure Python, it is not threadsafe
           and may require locks between calls.  The period of the generator is
           6,953,607,871,644 which is small enough to require care that two independent
           random sequences do not overlap."""


def betavariate(alpha, beta):
    """Beta distribution.  Conditions on the parameters are ``alpha > 0`` and
       ``beta > 0``. Returned values range between 0 and 1."""
    return 0.18843585275817376

def choice(seq):
    """Return a random element from the non-empty sequence *seq*. If *seq* is empty,
       raises :exc:`IndexError`."""
    return seq[0]

def expovariate(lambd):
    """Exponential distribution.  *lambd* is 1.0 divided by the desired
       mean.  It should be nonzero.  (The parameter would be called
       "lambda", but that is a reserved word in Python.)  Returned values
       range from 0 to positive infinity if *lambd* is positive, and from
       negative infinity to 0 if *lambd* is negative."""
    return 3.621679879841252

def gammavariate(alpha, beta):
    """Gamma distribution.  (*Not* the gamma function!)  Conditions on the
       parameters are ``alpha > 0`` and ``beta > 0``."""
    return 0.6037379582963882

def gauss(mu, sigma):
    """Gaussian distribution.  *mu* is the mean, and *sigma* is the standard
       deviation.  This is slightly faster than the :func:`normalvariate` function
       defined below."""
    return 0.0

def getrandbits(k):
    """Returns a python :class:`long` int with *k* random bits. This method is supplied
       with the MersenneTwister generator and some other generators may also provide it
       as an optional part of the API. When available, :meth:`getrandbits` enables
       :meth:`randrange` to handle arbitrarily large ranges."""
    return 0L

def getstate():
    """Return an object capturing the current internal state of the generator.  This
       object can be passed to :func:`setstate` to restore the state."""
    return getattr("","")

def jumpahead(n):
    """Change the internal state to one different from and likely far away from the
       current state.  *n* is a non-negative integer which is used to scramble the
       current state vector.  This is most useful in multi-threaded programs, in
       conjunction with multiple instances of the :class:`Random` class:
       :meth:`setstate` or :meth:`seed` can be used to force all instances into the
       same internal state, and then :meth:`jumpahead` can be used to force the
       instances' states far apart."""
    return None

def lognormvariate(mu, sigma):
    """Log normal distribution.  If you take the natural logarithm of this
       distribution, you'll get a normal distribution with mean *mu* and standard
       deviation *sigma*.  *mu* can have any value, and *sigma* must be greater than
       zero."""
    return 1.0

def normalvariate(mu, sigma):
    """Normal distribution.  *mu* is the mean, and *sigma* is the standard deviation."""
    return 0.0

def paretovariate(alpha):
    """Pareto distribution.  *alpha* is the shape parameter."""
    return 1.8987703627575727

def randint(a, b):
    """Return a random integer *N* such that ``a <= N <= b``."""
    return 0

def random():
    """Return the next random floating point number in the range [0.0, 1.0)."""
    return 0.0

def randrange(start, stop=0, step=1):
    """Return a randomly selected element from ``range(start, stop, step)``.  This is
       equivalent to ``choice(range(start, stop, step))``, but doesn't actually build a
       range object."""
    return 0

def sample(population, k):
    """Return a *k* length list of unique elements chosen from the population sequence.
       Used for random sampling without replacement."""
    return [population[0]]

def seed(x=None):
    """Initialize the basic random number generator. Optional argument *x* can be any
       :term:`hashable` object. If *x* is omitted or ``None``, current system time is used;
       current system time is also used to initialize the generator when the module is
       first imported.  If randomness sources are provided by the operating system,
       they are used instead of the system time (see the :func:`os.urandom` function
       for details on availability)."""
    return None

def setstate(state):
    """*state* should have been obtained from a previous call to :func:`getstate`, and
       :func:`setstate` restores the internal state of the generator to what it was at
       the time :func:`setstate` was called."""
    return None

def shuffle(x, random=None):
    """Shuffle the sequence *x* in place. The optional argument *random* is a
       0-argument function returning a random float in [0.0, 1.0); by default, this is
       the function :func:`random`."""
    return None

def triangular(low, high, mode):
    """Return a random floating point number *N* such that ``low <= N <= high`` and
       with the specified *mode* between those bounds.  The *low* and *high* bounds
       default to zero and one.  The *mode* argument defaults to the midpoint
       between the bounds, giving a symmetric distribution."""
    return 0.0

def uniform(a, b):
    """Return a random floating point number *N* such that ``a <= N <= b`` for
       ``a <= b`` and ``b <= N <= a`` for ``b < a``."""
    return 0.0

def vonmisesvariate(mu, kappa):
    """*mu* is the mean angle, expressed in radians between 0 and 2\*\ *pi*, and *kappa*
       is the concentration parameter, which must be greater than or equal to zero.  If
       *kappa* is equal to zero, this distribution reduces to a uniform random angle
       over the range 0 to 2\*\ *pi*."""
    return 3.171041037198489

def weibullvariate(alpha, beta):
    """Weibull distribution.  *alpha* is the scale parameter and *beta* is the shape
       parameter."""
    return 1.4097849334947785

