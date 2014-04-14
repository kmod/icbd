# generated with make_mock.py

accept2dyear = 1

altzone = 25200

def asctime(t=0.0):
    """Convert a tuple or :class:`struct_time` representing a time as returned by
       :func:`gmtime` or :func:`localtime` to a 24-character string of the following
       form: ``'Sun Jun 20 23:21:05 1993'``.  If *t* is not provided, the current time
       as returned by :func:`localtime` is used. Locale information is not used by
       :func:`asctime`."""
    return 'Thu May  3 22:09:55 2012'

def clock():
    return 0.02

def ctime(secs=0.0):
    """Convert a time expressed in seconds since the epoch to a string representing
       local time. If *secs* is not provided or :const:`None`, the current time as
       returned by :func:`time` is used.  ``ctime(secs)`` is equivalent to
       ``asctime(localtime(secs))``. Locale information is not used by :func:`ctime`."""
    return 'Thu May  3 22:09:55 2012'

daylight = 1

def gmtime(secs=0.0):
    """Convert a time expressed in seconds since the epoch to a :class:`struct_time` in
       UTC in which the dst flag is always zero.  If *secs* is not provided or
       :const:`None`, the current time as returned by :func:`time` is used.  Fractions
       of a second are ignored.  See above for a description of the
       :class:`struct_time` object. See :func:`calendar.timegm` for the inverse of this
       function."""
    return struct_time(tm_year=2012, tm_mon=5, tm_mday=4, tm_hour=5, tm_min=9, tm_sec=55, tm_wday=4, tm_yday=125, tm_isdst=0)

def localtime(secs=0.0):
    """Like :func:`gmtime` but converts to local time.  If *secs* is not provided or
       :const:`None`, the current time as returned by :func:`time` is used.  The dst
       flag is set to ``1`` when DST applies to the given time."""
    return struct_time(tm_year=2012, tm_mon=5, tm_mday=3, tm_hour=22, tm_min=9, tm_sec=55, tm_wday=3, tm_yday=124, tm_isdst=1)

def mktime(t):
    """This is the inverse function of :func:`localtime`.  Its argument is the
       :class:`struct_time` or full 9-tuple (since the dst flag is needed; use ``-1``
       as the dst flag if it is unknown) which expresses the time in *local* time, not
       UTC.  It returns a floating point number, for compatibility with :func:`time`.
       If the input value cannot be represented as a valid time, either
       :exc:`OverflowError` or :exc:`ValueError` will be raised (which depends on
       whether the invalid value is caught by Python or the underlying C libraries).
       The earliest date for which it can generate a time is platform-dependent."""

def sleep(secs):
    """Suspend execution for the given number of seconds.  The argument may be a
       floating point number to indicate a more precise sleep time. The actual
       suspension time may be less than that requested because any caught signal will
       terminate the :func:`sleep` following execution of that signal's catching
       routine.  Also, the suspension time may be longer than requested by an arbitrary
       amount because of the scheduling of other activity in the system."""
    return None

def strftime(format, t=None):
    """Convert a tuple or :class:`struct_time` representing a time as returned by
       :func:`gmtime` or :func:`localtime` to a string as specified by the *format*
       argument.  If *t* is not provided, the current time as returned by
       :func:`localtime` is used.  *format* must be a string.  :exc:`ValueError` is
       raised if any field in *t* is outside of the allowed range."""
    return ''

def strptime(string, format=''):
    """Parse a string representing a time according to a format.  The return  value is
       a :class:`struct_time` as returned by :func:`gmtime` or :func:`localtime`."""
    return struct_time(tm_year=1900, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=0, tm_yday=1, tm_isdst=-1)

class struct_time(object):
    """:func:`localtime`, and :func:`strptime`.  It is an object with a :term:`named
       tuple` interface: values can be accessed by index and by attribute name.  The
       following values are present:"""
    def __init__(self, **kw):
        pass

    n_fields = 9
    n_sequence_fields = 9
    n_unnamed_fields = 0


def time():
    """Return the time in seconds since the epoch as a floating point number.
       Note that even though the time is always returned as a floating point
       number, not all systems provide time with a better precision than 1 second.
       While this function normally returns non-decreasing values, it can return a
       lower value than a previous call if the system clock has been set back between
       the two calls."""
    return 0.0

timezone = 0

tzname = ('PST', 'PDT')

def tzset():
    """Resets the time conversion rules used by the library routines. The environment
       variable :envvar:`TZ` specifies how this is done."""
    return None

