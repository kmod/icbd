# generated with make_mock.py

MAXYEAR = 9999

MINYEAR = 1

class date(object):
    """An idealized naive date, assuming the current Gregorian calendar always was, and
       always will be, in effect. Attributes: :attr:`year`, :attr:`month`, and
       :attr:`day`."""

    def ctime(self):
        """Return a string representing the date, for example ``date(2002, 12,
           4).ctime() == 'Wed Dec 4 00:00:00 2002'``. ``d.ctime()`` is equivalent to
           ``time.ctime(time.mktime(d.timetuple()))`` on platforms where the native C
           :c:func:`ctime` function (which :func:`time.ctime` invokes, but which
           :meth:`date.ctime` does not invoke) conforms to the C standard."""
        return ""

    @property
    def day(self):
        """Between 1 and the number of days in the given month of the given year."""
        return 0

    @classmethod
    def fromordinal(cls, ordinal):
        """Return the date corresponding to the proleptic Gregorian ordinal, where January
           1 of year 1 has ordinal 1.  :exc:`ValueError` is raised unless ``1 <= ordinal <=
           date.max.toordinal()``. For any date *d*, ``date.fromordinal(d.toordinal()) ==
           d``."""
        return date()

    @classmethod
    def fromtimestamp(cls, timestamp):
        """Return the local date corresponding to the POSIX timestamp, such as is returned
           by :func:`time.time`.  This may raise :exc:`ValueError`, if the timestamp is out
           of the range of values supported by the platform C :c:func:`localtime` function.
           It's common for this to be restricted to years from 1970 through 2038.  Note
           that on non-POSIX systems that include leap seconds in their notion of a
           timestamp, leap seconds are ignored by :meth:`fromtimestamp`."""
        return date()

    def isocalendar(self):
        """Return a 3-tuple, (ISO year, ISO week number, ISO weekday)."""
        return (0,0,0)

    def isoformat(self):
        """Return a string representing the date in ISO 8601 format, 'YYYY-MM-DD'.  For
           example, ``date(2002, 12, 4).isoformat() == '2002-12-04'``."""
        return ""

    def isoweekday(self):
        """Return the day of the week as an integer, where Monday is 1 and Sunday is 7.
           For example, ``date(2002, 12, 4).isoweekday() == 3``, a Wednesday. See also
           :meth:`weekday`, :meth:`isocalendar`."""
        return 0

    @property
    def month(self):
        """Between 1 and 12 inclusive."""
        return 0

    def replace(self, year, month, day):
        """Return a date with the same value, except for those parameters given new
           values by whichever keyword arguments are specified.  For example, if ``d ==
           date(2002, 12, 31)``, then ``d.replace(day=26) == date(2002, 12, 26)``."""
        return self

    def strftime(self, format):
        """Return a string representing the date, controlled by an explicit format string.
           Format codes referring to hours, minutes or seconds will see 0 values. See
           section :ref:`strftime-strptime-behavior`."""
        return ""

    def timetuple(self):
        """Return a :class:`time.struct_time` such as returned by :func:`time.localtime`.
           The hours, minutes and seconds are 0, and the DST flag is -1. ``d.timetuple()``
           is equivalent to ``time.struct_time((d.year, d.month, d.day, 0, 0, 0,
           d.weekday(), yday, -1))``, where ``yday = d.toordinal() - date(d.year, 1,
           1).toordinal() + 1`` is the day number within the current year starting with
           ``1`` for January 1st."""
        return getattr(self, "crap")

    @classmethod
    def today(cls):
        """Return the current local date.  This is equivalent to
           ``date.fromtimestamp(time.time())``."""
        return date()

    def toordinal(self):
        """Return the proleptic Gregorian ordinal of the date, where January 1 of year 1
           has ordinal 1.  For any :class:`date` object *d*,
           ``date.fromordinal(d.toordinal()) == d``."""
        return 0

    def weekday(self):
        """Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
           For example, ``date(2002, 12, 4).weekday() == 2``, a Wednesday. See also
           :meth:`isoweekday`."""
        return 0

    @property
    def year(self):
        """Between :const:`MINYEAR` and :const:`MAXYEAR` inclusive."""
        return 0

    def __init__(self, year, month, day):
        """All arguments are required.  Arguments may be ints or longs, in the following
           ranges:"""


class datetime(date):
    """A combination of a date and a time. Attributes: :attr:`year`, :attr:`month`,
       :attr:`day`, :attr:`hour`, :attr:`minute`, :attr:`second`, :attr:`microsecond`,
       and :attr:`tzinfo`."""

    def astimezone(self, tz):
        """Return a :class:`.datetime` object with new :attr:`tzinfo` attribute *tz*,
           adjusting the date and time data so the result is the same UTC time as
           *self*, but in *tz*'s local time."""
        return self

    @classmethod
    def combine(cls, date, time):
        """Return a new :class:`.datetime` object whose date components are equal to the
           given :class:`date` object's, and whose time components and :attr:`tzinfo`
           attributes are equal to the given :class:`.time` object's. For any
           :class:`.datetime` object *d*,
           ``d == datetime.combine(d.date(), d.timetz())``.  If date is a
           :class:`.datetime` object, its time components and :attr:`tzinfo` attributes
           are ignored."""
        return datetime()

    def ctime(self):
        """Return a string representing the date and time, for example ``datetime(2002, 12,
           4, 20, 30, 40).ctime() == 'Wed Dec  4 20:30:40 2002'``. ``d.ctime()`` is
           equivalent to ``time.ctime(time.mktime(d.timetuple()))`` on platforms where the
           native C :c:func:`ctime` function (which :func:`time.ctime` invokes, but which
           :meth:`datetime.ctime` does not invoke) conforms to the C standard."""
        return ""

    def date(self):
        """Return :class:`date` object with same year, month and day."""
        return date()

    @property
    def day(self):
        """Between 1 and the number of days in the given month of the given year."""
        return 0

    def dst(self):
        """If :attr:`tzinfo` is ``None``, returns ``None``, else returns
           ``self.tzinfo.dst(self)``, and raises an exception if the latter doesn't return
           ``None``, or a :class:`timedelta` object representing a whole number of minutes
           with magnitude less than one day."""
        return 0

    @classmethod
    def fromordinal(cls, ordinal):
        """Return the :class:`.datetime` corresponding to the proleptic Gregorian ordinal,
           where January 1 of year 1 has ordinal 1. :exc:`ValueError` is raised unless ``1
           <= ordinal <= datetime.max.toordinal()``.  The hour, minute, second and
           microsecond of the result are all 0, and :attr:`tzinfo` is ``None``."""
        return datetime()

    @classmethod
    def fromtimestamp(cls, timestamp, tz=None):
        """Return the local date and time corresponding to the POSIX timestamp, such as is
           returned by :func:`time.time`. If optional argument *tz* is ``None`` or not
           specified, the timestamp is converted to the platform's local date and time, and
           the returned :class:`.datetime` object is naive."""
        return datetime()

    @property
    def hour(self):
        """In ``range(24)``."""
        return 0

    def isocalendar(self):
        """Return a 3-tuple, (ISO year, ISO week number, ISO weekday).  The same as
           ``self.date().isocalendar()``."""
        return (0,0,0)

    def isoformat(self, sep=''):
        """Return a string representing the date and time in ISO 8601 format,
           YYYY-MM-DDTHH:MM:SS.mmmmmm or, if :attr:`microsecond` is 0,
           YYYY-MM-DDTHH:MM:SS"""
        return ''

    def isoweekday(self):
        """Return the day of the week as an integer, where Monday is 1 and Sunday is 7.
           The same as ``self.date().isoweekday()``. See also :meth:`weekday`,
           :meth:`isocalendar`."""
        return 0

    @property
    def microsecond(self):
        """In ``range(1000000)``."""
        return 0

    @property
    def minute(self):
        """In ``range(60)``."""
        return 0

    @property
    def month(self):
        """Between 1 and 12 inclusive."""
        return 0

    @classmethod
    def now(cls, tz=None):
        """Return the current local date and time.  If optional argument *tz* is ``None``
           or not specified, this is like :meth:`today`, but, if possible, supplies more
           precision than can be gotten from going through a :func:`time.time` timestamp
           (for example, this may be possible on platforms supplying the C
           :c:func:`gettimeofday` function)."""
        return datetime()

    def replace(self, year=0, month=0, day=0, hour=0, minute=0, second=0, microsecond=0, tzinfo=0):
        """Return a datetime with the same attributes, except for those attributes given
           new values by whichever keyword arguments are specified.  Note that
           ``tzinfo=None`` can be specified to create a naive datetime from an aware
           datetime with no conversion of date and time data."""
        return self

    @property
    def second(self):
        """In ``range(60)``."""
        return 0

    def strftime(self, format):
        """Return a string representing the date and time, controlled by an explicit format
           string.  See section :ref:`strftime-strptime-behavior`."""
        return ""

    @classmethod
    def strptime(cls, date_string, format):
        """Return a :class:`.datetime` corresponding to *date_string*, parsed according to
           *format*.  This is equivalent to ``datetime(*(time.strptime(date_string,
           format)[0:6]))``. :exc:`ValueError` is raised if the date_string and format
           can't be parsed by :func:`time.strptime` or if it returns a value which isn't a
           time tuple. See section :ref:`strftime-strptime-behavior`."""
        return datetime()

    def time(self):
        """Return :class:`.time` object with same hour, minute, second and microsecond.
           :attr:`tzinfo` is ``None``.  See also method :meth:`timetz`."""
        return getattr(self, "crap")

    def timetuple(self):
        """Return a :class:`time.struct_time` such as returned by :func:`time.localtime`.
           ``d.timetuple()`` is equivalent to ``time.struct_time((d.year, d.month, d.day,
           d.hour, d.minute, d.second, d.weekday(), yday, dst))``, where ``yday =
           d.toordinal() - date(d.year, 1, 1).toordinal() + 1`` is the day number within
           the current year starting with ``1`` for January 1st. The :attr:`tm_isdst` flag
           of the result is set according to the :meth:`dst` method: :attr:`tzinfo` is
           ``None`` or :meth:`dst` returns ``None``, :attr:`tm_isdst` is set to ``-1``;
           else if :meth:`dst` returns a non-zero value, :attr:`tm_isdst` is set to ``1``;
           else :attr:`tm_isdst` is set to ``0``."""
        return getattr(self, "crap")

    def timetz(self):
        """Return :class:`.time` object with same hour, minute, second, microsecond, and
           tzinfo attributes.  See also method :meth:`time`."""
        return getattr(self, "crap")

    @classmethod
    def today(cls):
        """Return the current local datetime, with :attr:`tzinfo` ``None``. This is
           equivalent to ``datetime.fromtimestamp(time.time())``. See also :meth:`now`,
           :meth:`fromtimestamp`."""
        return datetime()

    def toordinal(self):
        """Return the proleptic Gregorian ordinal of the date.  The same as
           ``self.date().toordinal()``."""
        return 0

    @property
    def tzinfo(self):
        """The object passed as the *tzinfo* argument to the :class:`.datetime` constructor,
           or ``None`` if none was passed."""
        return tzinfo()

    def tzname(self):
        """If :attr:`tzinfo` is ``None``, returns ``None``, else returns
           ``self.tzinfo.tzname(self)``, raises an exception if the latter doesn't return
           ``None`` or a string object,"""
        return ""

    @classmethod
    def utcfromtimestamp(cls, timestamp):
        """Return the UTC :class:`.datetime` corresponding to the POSIX timestamp, with
           :attr:`tzinfo` ``None``. This may raise :exc:`ValueError`, if the timestamp is
           out of the range of values supported by the platform C :c:func:`gmtime` function.
           It's common for this to be restricted to years in 1970 through 2038. See also
           :meth:`fromtimestamp`."""
        return datetime()

    @classmethod
    def utcnow(cls):
        """Return the current UTC date and time, with :attr:`tzinfo` ``None``. This is like
           :meth:`now`, but returns the current UTC date and time, as a naive
           :class:`.datetime` object. See also :meth:`now`."""
        return datetime()

    def utcoffset(self):
        """If :attr:`tzinfo` is ``None``, returns ``None``, else returns
           ``self.tzinfo.utcoffset(self)``, and raises an exception if the latter doesn't
           return ``None``, or a :class:`timedelta` object representing a whole number of
           minutes with magnitude less than one day."""
        return 0.0

    def utctimetuple(self):
        """If :class:`.datetime` instance *d* is naive, this is the same as
           ``d.timetuple()`` except that :attr:`tm_isdst` is forced to 0 regardless of what
           ``d.dst()`` returns.  DST is never in effect for a UTC time."""
        return getattr(self, "crap")

    def weekday(self):
        """Return the day of the week as an integer, where Monday is 0 and Sunday is 6.
           The same as ``self.date().weekday()``. See also :meth:`isoweekday`."""
        return 0

    @property
    def year(self):
        """Between :const:`MINYEAR` and :const:`MAXYEAR` inclusive."""
        return 0

    def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        """The year, month and day arguments are required.  *tzinfo* may be ``None``, or an
           instance of a :class:`tzinfo` subclass.  The remaining arguments may be ints or
           longs, in the following ranges:"""


class time(object):
    """An idealized time, independent of any particular day, assuming that every day
       has exactly 24\*60\*60 seconds (there is no notion of "leap seconds" here).
       Attributes: :attr:`hour`, :attr:`minute`, :attr:`second`, :attr:`microsecond`,
       and :attr:`tzinfo`."""

    def dst(self):
        """If :attr:`tzinfo` is ``None``, returns ``None``, else returns
           ``self.tzinfo.dst(None)``, and raises an exception if the latter doesn't return
           ``None``, or a :class:`timedelta` object representing a whole number of minutes
           with magnitude less than one day."""
        return 0

    @property
    def hour(self):
        """In ``range(24)``."""
        return 0

    def isoformat(self):
        """Return a string representing the time in ISO 8601 format, HH:MM:SS.mmmmmm or, if
           self.microsecond is 0, HH:MM:SS If :meth:`utcoffset` does not return ``None``, a
           6-character string is appended, giving the UTC offset in (signed) hours and
           minutes: HH:MM:SS.mmmmmm+HH:MM or, if self.microsecond is 0, HH:MM:SS+HH:MM"""
        return ""

    @property
    def microsecond(self):
        """In ``range(1000000)``."""
        return 0

    @property
    def minute(self):
        """In ``range(60)``."""
        return 0

    def replace(self, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        """Return a :class:`.time` with the same value, except for those attributes given
           new values by whichever keyword arguments are specified.  Note that
           ``tzinfo=None`` can be specified to create a naive :class:`.time` from an
           aware :class:`.time`, without conversion of the time data."""
        return self

    @property
    def second(self):
        """In ``range(60)``."""
        return 0

    def strftime(self, format):
        """Return a string representing the time, controlled by an explicit format string.
           See section :ref:`strftime-strptime-behavior`."""
        return ""

    @property
    def tzinfo(self):
        """The object passed as the tzinfo argument to the :class:`.time` constructor, or
           ``None`` if none was passed."""
        return tzinfo()

    def tzname(self):
        """If :attr:`tzinfo` is ``None``, returns ``None``, else returns
           ``self.tzinfo.tzname(None)``, or raises an exception if the latter doesn't
           return ``None`` or a string object."""
        return ""

    def utcoffset(self):
        """If :attr:`tzinfo` is ``None``, returns ``None``, else returns
           ``self.tzinfo.utcoffset(None)``, and raises an exception if the latter doesn't
           return ``None`` or a :class:`timedelta` object representing a whole number of
           minutes with magnitude less than one day."""
        return ""

    def __init__(self, hour, minute=0, second=0, microsecond=0, tzinfo=None):
        """All arguments are optional.  *tzinfo* may be ``None``, or an instance of a
           :class:`tzinfo` subclass.  The remaining arguments may be ints or longs, in the
           following ranges:"""


class timedelta(object):
    """A duration expressing the difference between two :class:`date`, :class:`.time`,
       or :class:`.datetime` instances to microsecond resolution."""

    def total_seconds(self):
        """Return the total number of seconds contained in the duration.
           Equivalent to ``(td.microseconds + (td.seconds + td.days * 24 *
           3600) * 10**6) / 10**6`` computed with true division enabled."""
        return 0

    def __init__(self, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        """All arguments are optional and default to ``0``.  Arguments may be ints, longs,
           or floats, and may be positive or negative."""
        #  Between 0 and 86399 inclusive              
        self.seconds = 0
        #  Between -999999999 and 999999999 inclusive 
        self.days = 0
        #  Between 0 and 999999 inclusive             
        self.microseconds = 0


class tzinfo(object):
    """:class:`.datetime` and :class:`.time` classes to provide a customizable notion of
       time adjustment (for example, to account for time zone and/or daylight saving
       time)."""

    def dst(self, dt):
        """Return the daylight saving time (DST) adjustment, in minutes east of UTC, or
           ``None`` if DST information isn't known.  Return ``timedelta(0)`` if DST is not
           in effect. If DST is in effect, return the offset as a :class:`timedelta` object
           (see :meth:`utcoffset` for details). Note that DST offset, if applicable, has
           already been added to the UTC offset returned by :meth:`utcoffset`, so there's
           no need to consult :meth:`dst` unless you're interested in obtaining DST info
           separately.  For example, :meth:`datetime.timetuple` calls its :attr:`tzinfo`
           attribute's :meth:`dst` method to determine how the :attr:`tm_isdst` flag
           should be set, and :meth:`tzinfo.fromutc` calls :meth:`dst` to account for
           DST changes when crossing time zones."""

    def fromutc(self, dt):
        """This is called from the default :class:`datetime.astimezone()`
           implementation.  When called from that, ``dt.tzinfo`` is *self*, and *dt*'s
           date and time data are to be viewed as expressing a UTC time.  The purpose
           of :meth:`fromutc` is to adjust the date and time data, returning an
           equivalent datetime in *self*'s local time."""
        return datetime()

    def tzname(self, dt):
        """Return the time zone name corresponding to the :class:`.datetime` object *dt*, as
           a string. Nothing about string names is defined by the :mod:`datetime` module,
           and there's no requirement that it mean anything in particular.  For example,
           "GMT", "UTC", "-500", "-5:00", "EDT", "US/Eastern", "America/New York" are all
           valid replies.  Return ``None`` if a string name isn't known.  Note that this is
           a method rather than a fixed string primarily because some :class:`tzinfo`
           subclasses will wish to return different names depending on the specific value
           of *dt* passed, especially if the :class:`tzinfo` class is accounting for
           daylight time."""
        return ""

    def utcoffset(self, dt):
        """Return offset of local time from UTC, in minutes east of UTC.  If local time is
           west of UTC, this should be negative.  Note that this is intended to be the
           total offset from UTC; for example, if a :class:`tzinfo` object represents both
           time zone and DST adjustments, :meth:`utcoffset` should return their sum.  If
           the UTC offset isn't known, return ``None``.  Else the value returned must be a
           :class:`timedelta` object specifying a whole number of minutes in the range
           -1439 to 1439 inclusive (1440 = 24\*60; the magnitude of the offset must be less
           than one day).  Most implementations of :meth:`utcoffset` will probably look
           like one of these two::"""
        return ""


date.max = date(9999, 12, 31)
date.min = date(1, 1, 1)
date.resolution = timedelta(1)

datetime.max = datetime(9999, 12, 31, 23, 59, 59, 999999)
datetime.min = datetime(1, 1, 1, 0, 0)
datetime.resolution = timedelta(0, 0, 1)

time.max = time(23, 59, 59, 999999)
time.min = time(0, 0)
time.resolution = timedelta(0, 0, 1)

timedelta.max = timedelta(999999999, 86399, 999999)
timedelta.min = timedelta(-999999999)
timedelta.resolution = timedelta(0, 0, 1)

