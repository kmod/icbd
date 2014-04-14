# generated with make_mock.py

DN_ACCESS = 1
DN_ATTRIB = 32
DN_CREATE = 4
DN_DELETE = 8
DN_MODIFY = 2
DN_MULTISHOT = 2147483648
DN_RENAME = 16
FASYNC = 8192
FD_CLOEXEC = 1
F_DUPFD = 0
F_EXLCK = 4
F_GETFD = 1
F_GETFL = 3
F_GETLEASE = 1025
F_GETLK = 5
F_GETLK64 = 5
F_GETOWN = 9
F_GETSIG = 11
F_NOTIFY = 1026
F_RDLCK = 0
F_SETFD = 2
F_SETFL = 4
F_SETLEASE = 1024
F_SETLK = 6
F_SETLK64 = 6
F_SETLKW = 7
F_SETLKW64 = 7
F_SETOWN = 8
F_SETSIG = 10
F_SHLCK = 8
F_UNLCK = 2
F_WRLCK = 1
I_ATMARK = 21279
I_CANPUT = 21282
I_CKBAND = 21277
I_FDINSERT = 21264
I_FIND = 21259
I_FLUSH = 21253
I_FLUSHBAND = 21276
I_GETBAND = 21278
I_GETCLTIME = 21281
I_GETSIG = 21258
I_GRDOPT = 21255
I_GWROPT = 21268
I_LINK = 21260
I_LIST = 21269
I_LOOK = 21252
I_NREAD = 21249
I_PEEK = 21263
I_PLINK = 21270
I_POP = 21251
I_PUNLINK = 21271
I_PUSH = 21250
I_RECVFD = 21262
I_SENDFD = 21265
I_SETCLTIME = 21280
I_SETSIG = 21257
I_SRDOPT = 21254
I_STR = 21256
I_SWROPT = 21267
I_UNLINK = 21261
LOCK_EX = 2
LOCK_MAND = 32
LOCK_NB = 4
LOCK_READ = 64
LOCK_RW = 192
LOCK_SH = 1
LOCK_UN = 8
LOCK_WRITE = 128

def fcntl(fd, op, arg=0):
    """Perform the requested operation on file descriptor *fd* (file objects providing
       a :meth:`fileno` method are accepted as well). The operation is defined by *op*
       and is operating system dependent.  These codes are also found in the
       :mod:`fcntl` module. The argument *arg* is optional, and defaults to the integer
       value ``0``.  When present, it can either be an integer value, or a string.
       With the argument missing or an integer value, the return value of this function
       is the integer return value of the C :c:func:`fcntl` call.  When the argument is
       a string it represents a binary structure, e.g. created by :func:`struct.pack`.
       The binary data is copied to a buffer whose address is passed to the C
       :c:func:`fcntl` call.  The return value after a successful call is the contents
       of the buffer, converted to a string object.  The length of the returned string
       will be the same as the length of the *arg* argument.  This is limited to 1024
       bytes.  If the information returned in the buffer by the operating system is
       larger than 1024 bytes, this is most likely to result in a segmentation
       violation or a more subtle data corruption."""
    return 3

def flock(fd, op):
    """Perform the lock operation *op* on file descriptor *fd* (file objects providing
       a :meth:`fileno` method are accepted as well). See the Unix manual
       :manpage:`flock(2)` for details.  (On some systems, this function is emulated
       using :c:func:`fcntl`.)"""
    return None

def ioctl(fd, op, arg=0, mutate_flag=0):
    """This function is identical to the :func:`fcntl` function, except that the
       operations are typically defined in the library module :mod:`termios` and the
       argument handling is even more complicated."""
    return 0

def lockf(fd, operation, length=0, start=0, whence=0):
    """This is essentially a wrapper around the :func:`fcntl` locking calls.  *fd* is
       the file descriptor of the file to lock or unlock, and *operation* is one of the
       following values:"""
    return None

