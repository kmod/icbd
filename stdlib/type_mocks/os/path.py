# generated with make_mock.py

def abspath(path):
    """Return a normalized absolutized version of the pathname *path*. On most
       platforms, this is equivalent to ``normpath(join(os.getcwd(), path))``."""
    return ''

altsep = None

def basename(path):
    """Return the base name of pathname *path*.  This is the second half of the pair
       returned by ``split(path)``.  Note that the result of this function is different
       from the Unix :program:`basename` program; where :program:`basename` for
       ``'/foo/bar/'`` returns ``'bar'``, the :func:`basename` function returns an
       empty string (``''``)."""
    return ''

def commonprefix(list):
    """Return the longest path prefix (taken character-by-character) that is a prefix
       of all paths in  *list*.  If *list* is empty, return the empty string (``''``).
       Note that this may return invalid paths because it works a character at a time."""
    return ''

curdir = '.'

defpath = ':/bin:/usr/bin'

devnull = '/dev/null'

def dirname(path):
    """Return the directory name of pathname *path*.  This is the first half of the
       pair returned by ``split(path)``."""
    return ''

def exists(path):
    """Return ``True`` if *path* refers to an existing path.  Returns ``False`` for
       broken symbolic links. On some platforms, this function may return ``False`` if
       permission is not granted to execute :func:`os.stat` on the requested file, even
       if the *path* physically exists."""
    return False

def expanduser(path):
    """On Unix and Windows, return the argument with an initial component of ``~`` or
       ``~user`` replaced by that *user*'s home directory."""
    return ''

def expandvars(path):
    """Return the argument with environment variables expanded.  Substrings of the form
       ``$name`` or ``${name}`` are replaced by the value of environment variable
       *name*.  Malformed variable names and references to non-existing variables are
       left unchanged."""
    return ''

extsep = '.'

def getatime(path):
    """Return the time of last access of *path*.  The return value is a number giving
       the number of seconds since the epoch (see the  :mod:`time` module).  Raise
       :exc:`os.error` if the file does not exist or is inaccessible."""
    return 0.0

def getctime(path):
    """Return the system's ctime which, on some systems (like Unix) is the time of the
       last change, and, on others (like Windows), is the creation time for *path*.
       The return value is a number giving the number of seconds since the epoch (see
       the  :mod:`time` module).  Raise :exc:`os.error` if the file does not exist or
       is inaccessible."""
    return 0.0

def getmtime(path):
    """Return the time of last modification of *path*.  The return value is a number
       giving the number of seconds since the epoch (see the  :mod:`time` module).
       Raise :exc:`os.error` if the file does not exist or is inaccessible."""
    return 0.0

def getsize(path):
    """Return the size, in bytes, of *path*.  Raise :exc:`os.error` if the file does
       not exist or is inaccessible."""
    return 0

def isabs(path):
    """Return ``True`` if *path* is an absolute pathname.  On Unix, that means it
       begins with a slash, on Windows that it begins with a (back)slash after chopping
       off a potential drive letter."""
    return False

def isdir(path):
    """Return ``True`` if *path* is an existing directory.  This follows symbolic
       links, so both :func:`islink` and :func:`isdir` can be true for the same path."""
    return False

def isfile(path):
    """Return ``True`` if *path* is an existing regular file.  This follows symbolic
       links, so both :func:`islink` and :func:`isfile` can be true for the same path."""
    return False

def islink(path):
    """Return ``True`` if *path* refers to a directory entry that is a symbolic link.
       Always ``False`` if symbolic links are not supported."""
    return False

def ismount(path):
    """Return ``True`` if pathname *path* is a :dfn:`mount point`: a point in a file
       system where a different file system has been mounted.  The function checks
       whether *path*'s parent, :file:`path/..`, is on a different device than *path*,
       or whether :file:`path/..` and *path* point to the same i-node on the same
       device --- this should detect mount points for all Unix and POSIX variants."""
    return False

def join(*paths):
    """Join one or more path components intelligently.  If any component is an absolute
       path, all previous components (on Windows, including the previous drive letter,
       if there was one) are thrown away, and joining continues.  The return value is
       the concatenation of *path1*, and optionally *path2*, etc., with exactly one
       directory separator (``os.sep``) following each non-empty part except the last.
       (This means that an empty last part will result in a path that ends with a
       separator.)  Note that on Windows, since there is a current directory for
       each drive, ``os.path.join("c:", "foo")`` represents a path relative to the
       current directory on drive :file:`C:` (:file:`c:foo`), not :file:`c:\\foo`."""
    return ''

def lexists(path):
    """Return ``True`` if *path* refers to an existing path. Returns ``True`` for
       broken symbolic links.   Equivalent to :func:`exists` on platforms lacking
       :func:`os.lstat`."""
    return False

def normcase(path):
    """Normalize the case of a pathname.  On Unix and Mac OS X, this returns the
       path unchanged; on case-insensitive filesystems, it converts the path to
       lowercase.  On Windows, it also converts forward slashes to backward slashes."""
    return 0

def normpath(path):
    """Normalize a pathname.  This collapses redundant separators and up-level
       references so that ``A//B``, ``A/B/``, ``A/./B`` and ``A/foo/../B`` all become
       ``A/B``."""
    return '.'

pardir = '..'

pathsep = ':'

def realpath(path):
    """Return the canonical path of the specified filename, eliminating any symbolic
       links encountered in the path (if they are supported by the operating system)."""
    return ''

def relpath(path, start=''):
    """Return a relative filepath to *path* either from the current directory or from
       an optional *start* point."""
    return ''

def samefile(path1, path2):
    """Return ``True`` if both pathname arguments refer to the same file or directory
       (as indicated by device number and i-node number). Raise an exception if a
       :func:`os.stat` call on either pathname fails."""
    return True

def sameopenfile(fp1, fp2):
    """Return ``True`` if the file descriptors *fp1* and *fp2* refer to the same file."""
    return True

def samestat(stat1, stat2):
    """Return ``True`` if the stat tuples *stat1* and *stat2* refer to the same file.
       These structures may have been returned by :func:`fstat`, :func:`lstat`, or
       :func:`stat`.  This function implements the underlying comparison used by
       :func:`samefile` and :func:`sameopenfile`."""
    return True

sep = '/'

def split(path):
    """Split the pathname *path* into a pair, ``(head, tail)`` where *tail* is the
       last pathname component and *head* is everything leading up to that.  The
       *tail* part will never contain a slash; if *path* ends in a slash, *tail*
       will be empty.  If there is no slash in *path*, *head* will be empty.  If
       *path* is empty, both *head* and *tail* are empty.  Trailing slashes are
       stripped from *head* unless it is the root (one or more slashes only).  In
       all cases, ``join(head, tail)`` returns a path to the same location as *path*
       (but the strings may differ)."""
    return ('', '')

def splitdrive(path):
    """Split the pathname *path* into a pair ``(drive, tail)`` where *drive* is either
       a drive specification or the empty string.  On systems which do not use drive
       specifications, *drive* will always be the empty string.  In all cases, ``drive
       + tail`` will be the same as *path*."""
    return ('', '')

def splitext(path):
    """Split the pathname *path* into a pair ``(root, ext)``  such that ``root + ext ==
       path``, and *ext* is empty or begins with a period and contains at most one
       period. Leading periods on the basename are  ignored; ``splitext('.cshrc')``
       returns  ``('.cshrc', '')``."""
    return ('', '')

supports_unicode_filenames = False

def walk(path, visit, arg):
    """Calls the function *visit* with arguments ``(arg, dirname, names)`` for each
       directory in the directory tree rooted at *path* (including *path* itself, if it
       is a directory).  The argument *dirname* specifies the visited directory, the
       argument *names* lists the files in the directory (gotten from
       ``os.listdir(dirname)``). The *visit* function may modify *names* to influence
       the set of directories visited below *dirname*, e.g. to avoid visiting certain
       parts of the tree.  (The object referred to by *names* must be modified in
       place, using :keyword:`del` or slice assignment.)"""
    return None

