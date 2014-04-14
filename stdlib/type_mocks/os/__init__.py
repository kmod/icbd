# generated with make_mock.py

import __builtin__
import sys

__file_object = __builtin__.open("/dev/null")

EX_CANTCREAT = 73
EX_CONFIG = 78
EX_DATAERR = 65
EX_IOERR = 74
EX_NOHOST = 68
EX_NOINPUT = 66
EX_NOPERM = 77
EX_NOUSER = 67
EX_OK = 0
EX_OSERR = 71
EX_OSFILE = 72
EX_PROTOCOL = 76
EX_SOFTWARE = 70
EX_TEMPFAIL = 75
EX_UNAVAILABLE = 69
EX_USAGE = 64
F_OK = 0
NGROUPS_MAX = 65536
O_APPEND = 1024
O_ASYNC = 8192
O_CREAT = 64
O_DIRECT = 16384
O_DIRECTORY = 65536
O_DSYNC = 4096
O_EXCL = 128
O_LARGEFILE = 0
O_NDELAY = 2048
O_NOATIME = 262144
O_NOCTTY = 256
O_NOFOLLOW = 131072
O_NONBLOCK = 2048
O_RDONLY = 0
O_RDWR = 2
O_RSYNC = 1052672
O_SYNC = 1052672
O_TRUNC = 512
O_WRONLY = 1
P_NOWAIT = 1
P_NOWAITO = 1
P_WAIT = 0
R_OK = 4
SEEK_CUR = 1
SEEK_END = 2
SEEK_SET = 0
ST_APPEND = 256
ST_MANDLOCK = 64
ST_NOATIME = 1024
ST_NODEV = 4
ST_NODIRATIME = 2048
ST_NOEXEC = 8
ST_NOSUID = 2
ST_RDONLY = 1
ST_RELATIME = 4096
ST_SYNCHRONOUS = 16
ST_WRITE = 128
TMP_MAX = 238328
WCONTINUED = 8

import path

def WCOREDUMP(status):
    """Return ``True`` if a core dump was generated for the process, otherwise
       return ``False``."""
    return False

def WEXITSTATUS(status):
    """If ``WIFEXITED(status)`` is true, return the integer parameter to the
       :manpage:`exit(2)` system call.  Otherwise, the return value is meaningless."""
    return 0

def WIFCONTINUED(status):
    """Return ``True`` if the process has been continued from a job control stop,
       otherwise return ``False``."""
    return False

def WIFEXITED(status):
    """Return ``True`` if the process exited using the :manpage:`exit(2)` system call,
       otherwise return ``False``."""
    return False

def WIFSIGNALED(status):
    """Return ``True`` if the process exited due to a signal, otherwise return
       ``False``."""
    return False

def WIFSTOPPED(status):
    """Return ``True`` if the process has been stopped, otherwise return
       ``False``."""
    return False

WNOHANG = 1

def WSTOPSIG(status):
    """Return the signal which caused the process to stop."""
    return 0

def WTERMSIG(status):
    """Return the signal which caused the process to exit."""
    return 0

WUNTRACED = 2
W_OK = 2
X_OK = 1

def abort():
    """Generate a :const:`SIGABRT` signal to the current process.  On Unix, the default
       behavior is to produce a core dump; on Windows, the process immediately returns
       an exit code of ``3``.  Be aware that calling this function will not call the
       Python signal handler registered for :const:`SIGABRT` with
       :func:`signal.signal`."""

def access(path, mode):
    """Use the real uid/gid to test for access to *path*.  Note that most operations
       will use the effective uid/gid, therefore this routine can be used in a
       suid/sgid environment to test if the invoking user has the specified access to
       *path*.  *mode* should be :const:`F_OK` to test the existence of *path*, or it
       can be the inclusive OR of one or more of :const:`R_OK`, :const:`W_OK`, and
       :const:`X_OK` to test permissions.  Return :const:`True` if access is allowed,
       :const:`False` if not. See the Unix man page :manpage:`access(2)` for more
       information."""
    return True

altsep = None

def chdir(path):
    """getcwd()
       :noindex:"""

def chmod(path, mode):
    """Change the mode of *path* to the numeric *mode*. *mode* may take one of the
       following values (as defined in the :mod:`stat` module) or bitwise ORed
       combinations of them:"""

def chown(path, uid, gid):
    """Change the owner and group id of *path* to the numeric *uid* and *gid*. To leave
       one of the ids unchanged, set it to -1."""

def chroot(path):
    """Change the root directory of the current process to *path*. Availability:
       Unix."""

def close(fd):
    """Close file descriptor *fd*."""

def closerange(fd_low, fd_high):
    """Close all file descriptors from *fd_low* (inclusive) to *fd_high* (exclusive),
       ignoring errors. Equivalent to::"""

def confstr(name):
    """Return string-valued system configuration values. *name* specifies the
       configuration value to retrieve; it may be a string which is the name of a
       defined system value; these names are specified in a number of standards (POSIX,
       Unix 95, Unix 98, and others).  Some platforms define additional names as well.
       The names known to the host operating system are given as the keys of the
       ``confstr_names`` dictionary.  For configuration variables not included in that
       mapping, passing an integer for *name* is also accepted."""
    return ''

confstr_names = {'CS_XBS5_LP64_OFF64_CFLAGS': 1108, 'CS_LFS64_CFLAGS': 1004, 'CS_XBS5_LPBIG_OFFBIG_LIBS': 1114, 'CS_XBS5_ILP32_OFFBIG_LINTFLAGS': 1107, 'CS_XBS5_ILP32_OFF32_LIBS': 1102, 'CS_XBS5_ILP32_OFF32_LINTFLAGS': 1103, 'CS_LFS64_LIBS': 1006, 'CS_XBS5_ILP32_OFF32_CFLAGS': 1100, 'CS_XBS5_ILP32_OFFBIG_CFLAGS': 1104, 'CS_LFS_LDFLAGS': 1001, 'CS_LFS_LINTFLAGS': 1003, 'CS_LFS_LIBS': 1002, 'CS_PATH': 0, 'CS_LFS64_LINTFLAGS': 1007, 'CS_LFS_CFLAGS': 1000, 'CS_LFS64_LDFLAGS': 1005, 'CS_XBS5_ILP32_OFFBIG_LIBS': 1106, 'CS_XBS5_ILP32_OFF32_LDFLAGS': 1101, 'CS_XBS5_LPBIG_OFFBIG_LINTFLAGS': 1115, 'CS_XBS5_ILP32_OFFBIG_LDFLAGS': 1105, 'CS_XBS5_LP64_OFF64_LINTFLAGS': 1111, 'CS_XBS5_LP64_OFF64_LIBS': 1110, 'CS_XBS5_LPBIG_OFFBIG_CFLAGS': 1112, 'CS_XBS5_LPBIG_OFFBIG_LDFLAGS': 1113, 'CS_XBS5_LP64_OFF64_LDFLAGS': 1109}

def ctermid():
    """Return the filename corresponding to the controlling terminal of the process."""
    return ''

curdir = '.'
defpath = ':/bin:/usr/bin'
devnull = '/dev/null'

def dup(fd):
    """Return a duplicate of file descriptor *fd*."""
    return 0

def dup2(fd, fd2):
    """Duplicate file descriptor *fd* to *fd2*, closing the latter first if necessary."""
    return 2

class error(EnvironmentError):
    pass

extsep = '.'

def fchdir(fd):
    """Change the current working directory to the directory represented by the file
       descriptor *fd*.  The descriptor must refer to an opened directory, not an open
       file."""

def fchmod(fd, mode):
    """Change the mode of the file given by *fd* to the numeric *mode*.  See the docs
       for :func:`chmod` for possible values of *mode*."""

def fchown(fd, uid, gid):
    """Change the owner and group id of the file given by *fd* to the numeric *uid*
       and *gid*.  To leave one of the ids unchanged, set it to -1."""

def fdatasync(fd):
    """Force write of file with filedescriptor *fd* to disk. Does not force update of
       metadata."""

def fdopen(fd, mode='r', bufsize=0):
    return __file_object

def fork():
    """Fork a child process.  Return ``0`` in the child and the child's process id in the
       parent.  If an error occurs :exc:`OSError` is raised."""
    return 0

def forkpty():
    """Fork a child process, using a new pseudo-terminal as the child's controlling
       terminal. Return a pair of ``(pid, fd)``, where *pid* is ``0`` in the child, the
       new child's process id in the parent, and *fd* is the file descriptor of the
       master end of the pseudo-terminal.  For a more portable approach, use the
       :mod:`pty` module.  If an error occurs :exc:`OSError` is raised."""
    return (0,0)

def fpathconf(fd, name):
    """Return system configuration information relevant to an open file. *name*
       specifies the configuration value to retrieve; it may be a string which is the
       name of a defined system value; these names are specified in a number of
       standards (POSIX.1, Unix 95, Unix 98, and others).  Some platforms define
       additional names as well.  The names known to the host operating system are
       given in the ``pathconf_names`` dictionary.  For configuration variables not
       included in that mapping, passing an integer for *name* is also accepted."""

def fstat(fd):
    """Return status for file descriptor *fd*, like :func:`~os.stat`."""

def fstatvfs(fd):
    """Return information about the filesystem containing the file associated with file
       descriptor *fd*, like :func:`statvfs`."""

def fsync(fd):
    """Force write of file with filedescriptor *fd* to disk.  On Unix, this calls the
       native :c:func:`fsync` function; on Windows, the MS :c:func:`_commit` function."""

def ftruncate(fd, length):
    """Truncate the file corresponding to file descriptor *fd*, so that it is at most
       *length* bytes in size."""

def getcwd():
    """Return a string representing the current working directory."""
    return ''

def getcwdu():
    """Return a Unicode object representing the current working directory."""
    return u''

def getegid():
    """Return the effective group id of the current process.  This corresponds to the
       "set id" bit on the file being executed in the current process."""
    return 0

def getenv(varname, value=None):
    """Return the value of the environment variable *varname* if it exists, or *value*
       if it doesn't.  *value* defaults to ``None``."""
    return ''

def geteuid():
    return 0

def getgid():
    return 0

def getgroups():
    """Return list of supplemental group ids associated with the current process."""
    return [0]

def getloadavg():
    """Return the number of processes in the system run queue averaged over the last
       1, 5, and 15 minutes or raises :exc:`OSError` if the load average was
       unobtainable."""
    return (0.0, 0.0, 0.0)

def getlogin():
    """Return the name of the user logged in on the controlling terminal of the
       process.  For most purposes, it is more useful to use the environment variable
       :envvar:`LOGNAME` to find out who the user is, or
       ``pwd.getpwuid(os.getuid())[0]`` to get the login name of the currently
       effective user id."""
    return ''

def getpgid(pid):
    """Return the process group id of the process with process id *pid*. If *pid* is 0,
       the process group id of the current process is returned."""
    return 0

def getpgrp():
    return 0

def getpid():
    return 0

def getppid():
    return 0

def getresgid():
    """Return a tuple (rgid, egid, sgid) denoting the current process's
       real, effective, and saved group ids."""
    return (0,0,0)

def getresuid():
    """Return a tuple (ruid, euid, suid) denoting the current process's
       real, effective, and saved user ids."""
    return (0,0,0)

def getsid(pid):
    """Call the system call :c:func:`getsid`.  See the Unix manual for the semantics."""

def getuid():
    return 0

def initgroups(username, gid):
    """Call the system initgroups() to initialize the group access list with all of
       the groups of which the specified username is a member, plus the specified
       group id."""

def isatty(fd):
    """Return ``True`` if the file descriptor *fd* is open and connected to a
       tty(-like) device, else ``False``."""
    return True

def kill(pid, sig):
    pass

def killpg(pgid, sig):
    pass

def lchown(path, uid, gid):
    """Change the owner and group id of *path* to the numeric *uid* and *gid*. This
       function will not follow symbolic links."""

linesep = '\n'

def link(source, link_name):
    """Create a hard link pointing to *source* named *link_name*."""

def listdir(path):
    """Return a list containing the names of the entries in the directory given by
       *path*.  The list is in arbitrary order.  It does not include the special
       entries ``'.'`` and ``'..'`` even if they are present in the
       directory."""
    return ['']

def lseek(fd, pos, how):
    """Set the current position of file descriptor *fd* to position *pos*, modified
       by *how*: :const:`SEEK_SET` or ``0`` to set the position relative to the
       beginning of the file; :const:`SEEK_CUR` or ``1`` to set it relative to the
       current position; :const:`os.SEEK_END` or ``2`` to set it relative to the end of
       the file."""

def lstat(path):
    """Perform the equivalent of an :c:func:`lstat` system call on the given path.
       Similar to :func:`~os.stat`, but does not follow symbolic links.  On
       platforms that do not support symbolic links, this is an alias for
       :func:`~os.stat`."""

def major(device):
    """Extract the device major number from a raw device number (usually the
       :attr:`st_dev` or :attr:`st_rdev` field from :c:type:`stat`)."""

def makedev(major, minor):
    """Compose a raw device number from the major and minor device numbers."""

def makedirs(path, mode=0777):
    pass

def minor(device):
    """Extract the device minor number from a raw device number (usually the
       :attr:`st_dev` or :attr:`st_rdev` field from :c:type:`stat`)."""

def mkdir(path, mode=0777):
    """Create a directory named *path* with numeric mode *mode*. The default *mode* is
       ``0777`` (octal).  On some systems, *mode* is ignored.  Where it is used, the
       current umask value is first masked out.  If the directory already exists,
       :exc:`OSError` is raised."""

def mkfifo(path, mode=0666):
    """Create a FIFO (a named pipe) named *path* with numeric mode *mode*.  The default
       *mode* is ``0666`` (octal).  The current umask value is first masked out from
       the mode."""

def mknod(filename, mode=0600, device=None):
    """Create a filesystem node (file, device special file or named pipe) named
       *filename*. *mode* specifies both the permissions to use and the type of node to
       be created, being combined (bitwise OR) with one of ``stat.S_IFREG``,
       ``stat.S_IFCHR``, ``stat.S_IFBLK``,
       and ``stat.S_IFIFO`` (those constants are available in :mod:`stat`).
       For ``stat.S_IFCHR`` and
       ``stat.S_IFBLK``, *device* defines the newly created device special file (probably using
       :func:`os.makedev`), otherwise it is ignored."""

name = 'posix'

def nice(increment):
    """Add *increment* to the process's "niceness".  Return the new niceness."""
    return 0

def open(file, flags, mode=0777):
    """Open the file *file* and set various flags according to *flags* and possibly its
       mode according to *mode*. The default *mode* is ``0777`` (octal), and the
       current umask value is first masked out.  Return the file descriptor for the
       newly opened file."""
    return 0

def openpty():
    return (0,0)

pardir = '..'

def pathconf(path, name):
    """Return system configuration information relevant to a named file. *name*
       specifies the configuration value to retrieve; it may be a string which is the
       name of a defined system value; these names are specified in a number of
       standards (POSIX.1, Unix 95, Unix 98, and others).  Some platforms define
       additional names as well.  The names known to the host operating system are
       given in the ``pathconf_names`` dictionary.  For configuration variables not
       included in that mapping, passing an integer for *name* is also accepted."""

pathconf_names = {'PC_MAX_INPUT': 2, 'PC_VDISABLE': 8, 'PC_SYNC_IO': 9, 'PC_SOCK_MAXBUF': 12, 'PC_NAME_MAX': 3, 'PC_MAX_CANON': 1, 'PC_PRIO_IO': 11, 'PC_CHOWN_RESTRICTED': 6, 'PC_ASYNC_IO': 10, 'PC_NO_TRUNC': 7, 'PC_FILESIZEBITS': 13, 'PC_LINK_MAX': 0, 'PC_PIPE_BUF': 5, 'PC_PATH_MAX': 4}

pathsep = ':'

def pipe():
    """Create a pipe.  Return a pair of file descriptors ``(r, w)`` usable for reading
       and writing, respectively."""
    return (0,1)

def popen(command, mode='r', bufsize=0):
    """Open a pipe to or from *command*.  The return value is an open file object
       connected to the pipe, which can be read or written depending on whether *mode*
       is ``'r'`` (default) or ``'w'``. The *bufsize* argument has the same meaning as
       the corresponding argument to the built-in :func:`open` function.  The exit
       status of the command (encoded in the format specified for :func:`wait`) is
       available as the return value of the :meth:`~file.close` method of the file object,
       except that when the exit status is zero (termination without errors), ``None``
       is returned."""
    return __file_object

def popen2(cmd, mode='r', bufsize=0):
    """Execute *cmd* as a sub-process and return the file objects ``(child_stdin,
       child_stdout)``."""
    return (__file_object, __file_object)

def popen3(cmd, mode='r', bufsize=0):
    """Execute *cmd* as a sub-process and return the file objects ``(child_stdin,
       child_stdout, child_stderr)``."""
    return (__file_object, __file_object, __file_object)

def popen4(cmd, mode='r', bufsize=0):
    """Execute *cmd* as a sub-process and return the file objects ``(child_stdin,
       child_stdout_and_stderr)``."""
    return (__file_object, __file_object)

def putenv(varname, value):
    pass

def read(fd, n):
    """Read at most *n* bytes from file descriptor *fd*. Return a string containing the
       bytes read.  If the end of the file referred to by *fd* has been reached, an
       empty string is returned."""
    return ""

def readlink(path):
    """Return a string representing the path to which the symbolic link points.  The
       result may be either an absolute or relative pathname; if it is relative, it may
       be converted to an absolute pathname using ``os.path.join(os.path.dirname(path),
       result)``."""
    return ""

def remove(path):
    """Remove (delete) the file *path*.  If *path* is a directory, :exc:`OSError` is
       raised; see :func:`rmdir` below to remove a directory.  This is identical to
       the :func:`unlink` function documented below.  On Windows, attempting to
       remove a file that is in use causes an exception to be raised; on Unix, the
       directory entry is removed but the storage allocated to the file is not made
       available until the original file is no longer in use."""

def removedirs(path):
    pass

def rename(src, dst):
    """Rename the file or directory *src* to *dst*.  If *dst* is a directory,
       :exc:`OSError` will be raised.  On Unix, if *dst* exists and is a file, it will
       be replaced silently if the user has permission.  The operation may fail on some
       Unix flavors if *src* and *dst* are on different filesystems.  If successful,
       the renaming will be an atomic operation (this is a POSIX requirement).  On
       Windows, if *dst* already exists, :exc:`OSError` will be raised even if it is a
       file; there may be no way to implement an atomic rename when *dst* names an
       existing file."""

def renames(old, new):
    """Recursive directory or file renaming function. Works like :func:`rename`, except
       creation of any intermediate directories needed to make the new pathname good is
       attempted first. After the rename, directories corresponding to rightmost path
       segments of the old name will be pruned away using :func:`removedirs`."""

def rmdir(path):
    """Remove (delete) the directory *path*.  Only works when the directory is
       empty, otherwise, :exc:`OSError` is raised.  In order to remove whole
       directory trees, :func:`shutil.rmtree` can be used."""

sep = '/'

def setegid(egid):
    """Set the current process's effective group id."""

def seteuid(euid):
    """Set the current process's effective user id."""

def setgid(gid):
    """Set the current process' group id."""

def setgroups(groups):
    """Set the list of supplemental group ids associated with the current process to
       *groups*. *groups* must be a sequence, and each element must be an integer
       identifying a group. This operation is typically available only to the superuser."""

def setpgid(pid, pgrp):
    """Call the system call :c:func:`setpgid` to set the process group id of the
       process with id *pid* to the process group with id *pgrp*.  See the Unix manual
       for the semantics."""

def setpgrp():
    """Call the system call :c:func:`setpgrp` or :c:func:`setpgrp(0, 0)` depending on
       which version is implemented (if any).  See the Unix manual for the semantics."""

def setregid(rgid, egid):
    """Set the current process's real and effective group ids."""

def setresgid(rgid, egid, sgid):
    """Set the current process's real, effective, and saved group ids."""

def setresuid(ruid, euid, suid):
    """Set the current process's real, effective, and saved user ids."""

def setreuid(ruid, euid):
    """Set the current process's real and effective user ids."""

def setsid():
    """Call the system call :c:func:`setsid`.  See the Unix manual for the semantics."""

def setuid(uid):
    """.. index:: single: user; id, setting"""

def stat(path):
    """Perform the equivalent of a :c:func:`stat` system call on the given path.
       (This function follows symlinks; to stat a symlink use :func:`lstat`.)"""

def stat_float_times(newvalue=False):
    """Determine whether :class:`stat_result` represents time stamps as float objects.
       If *newvalue* is ``True``, future calls to :func:`~os.stat` return floats, if it is
       ``False``, future calls return ints. If *newvalue* is omitted, return the
       current setting."""
    return False

class stat_result(object):
    n_fields = 16
    n_sequence_fields = 10
    n_unnamed_fields = 3


def statvfs(path):
    """Perform a :c:func:`statvfs` system call on the given path.  The return value is
       an object whose attributes describe the filesystem on the given path, and
       correspond to the members of the :c:type:`statvfs` structure, namely:
       :attr:`f_bsize`, :attr:`f_frsize`, :attr:`f_blocks`, :attr:`f_bfree`,
       :attr:`f_bavail`, :attr:`f_files`, :attr:`f_ffree`, :attr:`f_favail`,
       :attr:`f_flag`, :attr:`f_namemax`."""

class statvfs_result(object):
    n_fields = 10
    n_sequence_fields = 10
    n_unnamed_fields = 0


def strerror(code):
    """Return the error message corresponding to the error code in *code*.
       On platforms where :c:func:`strerror` returns ``NULL`` when given an unknown
       error number, :exc:`ValueError` is raised."""
    return ""

def symlink(source, link_name):
    """Create a symbolic link pointing to *source* named *link_name*."""

def sysconf(name):
    """Return integer-valued system configuration values. If the configuration value
       specified by *name* isn't defined, ``-1`` is returned.  The comments regarding
       the *name* parameter for :func:`confstr` apply here as well; the dictionary that
       provides information on the known names is given by ``sysconf_names``."""
    return 0

sysconf_names = {'SC_REALTIME_SIGNALS': 9, 'SC_PII_OSI_COTS': 63, 'SC_PII_OSI': 57, 'SC_T_IOV_MAX': 66, 'SC_THREADS': 67, 'SC_AIO_MAX': 24, 'SC_USHRT_MAX': 118, 'SC_THREAD_KEYS_MAX': 74, 'SC_XOPEN_XPG4': 100, 'SC_SEM_VALUE_MAX': 33, 'SC_XOPEN_XPG2': 98, 'SC_XOPEN_XPG3': 99, 'SC_GETGR_R_SIZE_MAX': 69, 'SC_SEM_NSEMS_MAX': 32, 'SC_AVPHYS_PAGES': 86, 'SC_NL_NMAX': 122, 'SC_PAGESIZE': 30, 'SC_EXPR_NEST_MAX': 42, 'SC_XOPEN_LEGACY': 129, 'SC_SHRT_MAX': 113, 'SC_2_SW_DEV': 51, 'SC_SSIZE_MAX': 110, 'SC_RTSIG_MAX': 31, 'SC_THREAD_PRIO_INHERIT': 80, 'SC_EQUIV_CLASS_MAX': 41, 'SC_NL_ARGMAX': 119, 'SC_PII_OSI_CLTS': 64, 'SC_2_CHAR_TERM': 95, 'SC_THREAD_PROCESS_SHARED': 82, 'SC_VERSION': 29, 'SC_LONG_BIT': 106, 'SC_SIGQUEUE_MAX': 34, 'SC_ATEXIT_MAX': 87, 'SC_BC_BASE_MAX': 36, 'SC_SELECT': 59, 'SC_XOPEN_ENH_I18N': 93, 'SC_PAGE_SIZE': 30, 'SC_PII_XTI': 54, 'SC_MEMORY_PROTECTION': 19, 'SC_TIMER_MAX': 35, 'SC_AIO_LISTIO_MAX': 23, 'SC_UCHAR_MAX': 115, 'SC_SCHAR_MAX': 111, 'SC_2_UPE': 97, 'SC_NL_SETMAX': 123, 'SC_RE_DUP_MAX': 44, 'SC_BC_SCALE_MAX': 38, 'SC_TZNAME_MAX': 6, 'SC_LOGIN_NAME_MAX': 71, 'SC_NPROCESSORS_ONLN': 84, 'SC_SEMAPHORES': 21, 'SC_SAVED_IDS': 8, 'SC_XOPEN_SHM': 94, 'SC_2_FORT_RUN': 50, 'SC_XOPEN_VERSION': 89, 'SC_IOV_MAX': 60, 'SC_2_VERSION': 46, 'SC_THREAD_DESTRUCTOR_ITERATIONS': 73, 'SC_ASYNCHRONOUS_IO': 12, 'SC_MESSAGE_PASSING': 20, 'SC_CHILD_MAX': 1, 'SC_ULONG_MAX': 117, 'SC_2_C_VERSION': 96, 'SC_ARG_MAX': 0, 'SC_GETPW_R_SIZE_MAX': 70, 'SC_XOPEN_CRYPT': 92, 'SC_SCHAR_MIN': 112, 'SC_AIO_PRIO_DELTA_MAX': 25, 'SC_NL_LANGMAX': 120, 'SC_THREAD_STACK_MIN': 75, 'SC_CHAR_MIN': 103, 'SC_NL_TEXTMAX': 124, 'SC_STREAM_MAX': 5, 'SC_UIO_MAXIOV': 60, 'SC_MEMLOCK': 17, 'SC_NZERO': 109, 'SC_SHARED_MEMORY_OBJECTS': 22, 'SC_THREAD_THREADS_MAX': 76, 'SC_THREAD_ATTR_STACKADDR': 77, 'SC_INT_MIN': 105, 'SC_SHRT_MIN': 114, 'SC_COLL_WEIGHTS_MAX': 40, 'SC_THREAD_PRIORITY_SCHEDULING': 79, 'SC_THREAD_ATTR_STACKSIZE': 78, 'SC_PHYS_PAGES': 85, 'SC_JOB_CONTROL': 7, 'SC_FSYNC': 15, 'SC_CHARCLASS_NAME_MAX': 45, 'SC_XOPEN_UNIX': 91, 'SC_BC_DIM_MAX': 37, 'SC_PII_INTERNET_STREAM': 61, 'SC_MB_LEN_MAX': 108, 'SC_UINT_MAX': 116, 'SC_CHAR_BIT': 101, 'SC_XOPEN_REALTIME': 130, 'SC_MQ_OPEN_MAX': 27, 'SC_PII_OSI_M': 65, 'SC_PRIORITY_SCHEDULING': 10, 'SC_NGROUPS_MAX': 3, 'SC_MQ_PRIO_MAX': 28, 'SC_XBS5_LPBIG_OFFBIG': 128, 'SC_PII_SOCKET': 55, 'SC_MAPPED_FILES': 16, 'SC_PII_INTERNET_DGRAM': 62, 'SC_XBS5_LP64_OFF64': 127, 'SC_XOPEN_XCU_VERSION': 90, 'SC_OPEN_MAX': 4, 'SC_PRIORITIZED_IO': 13, 'SC_TTY_NAME_MAX': 72, 'SC_WORD_BIT': 107, 'SC_SYNCHRONIZED_IO': 14, 'SC_PASS_MAX': 88, 'SC_PII_INTERNET': 56, 'SC_LINE_MAX': 43, 'SC_XBS5_ILP32_OFF32': 125, 'SC_2_C_DEV': 48, 'SC_2_C_BIND': 47, 'SC_BC_STRING_MAX': 39, 'SC_THREAD_PRIO_PROTECT': 81, 'SC_CHAR_MAX': 102, 'SC_XBS5_ILP32_OFFBIG': 126, 'SC_2_LOCALEDEF': 52, 'SC_PII': 53, 'SC_POLL': 58, 'SC_2_FORT_DEV': 49, 'SC_INT_MAX': 104, 'SC_NPROCESSORS_CONF': 83, 'SC_DELAYTIMER_MAX': 26, 'SC_THREAD_SAFE_FUNCTIONS': 68, 'SC_MEMLOCK_RANGE': 18, 'SC_NL_MSGMAX': 121, 'SC_TIMERS': 11, 'SC_XOPEN_REALTIME_THREADS': 131, 'SC_CLK_TCK': 2}

def system(command):
    """Execute the command (a string) in a subshell.  This is implemented by calling
       the Standard C function :c:func:`system`, and has the same limitations.
       Changes to :data:`sys.stdin`, etc. are not reflected in the environment of the
       executed command."""

def tcgetpgrp(fd):
    """Return the process group associated with the terminal given by *fd* (an open
       file descriptor as returned by :func:`os.open`)."""

def tcsetpgrp(fd, pg):
    """Set the process group associated with the terminal given by *fd* (an open file
       descriptor as returned by :func:`os.open`) to *pg*."""

def tempnam(dir='', prefix=''):
    """Return a unique path name that is reasonable for creating a temporary file.
       This will be an absolute path that names a potential directory entry in the
       directory *dir* or a common location for temporary files if *dir* is omitted or
       ``None``.  If given and not ``None``, *prefix* is used to provide a short prefix
       to the filename.  Applications are responsible for properly creating and
       managing files created using paths returned by :func:`tempnam`; no automatic
       cleanup is provided. On Unix, the environment variable :envvar:`TMPDIR`
       overrides *dir*, while on Windows :envvar:`TMP` is used.  The specific
       behavior of this function depends on the C library implementation; some aspects
       are underspecified in system documentation."""
    return ''

def times():
    """Return a 5-tuple of floating point numbers indicating accumulated (processor
       or other) times, in seconds.  The items are: user time, system time,
       children's user time, children's system time, and elapsed real time since a
       fixed point in the past, in that order.  See the Unix manual page
       :manpage:`times(2)` or the corresponding Windows Platform API documentation.
       On Windows, only the first two items are filled, the others are zero."""
    return (0.0, 0.0, 0.0, 0.0, 0.0)

def tmpfile():
    """Return a new file object opened in update mode (``w+b``).  The file has no
       directory entries associated with it and will be automatically deleted once
       there are no file descriptors for the file."""
    return __file_object

def tmpnam():
    """Return a unique path name that is reasonable for creating a temporary file.
       This will be an absolute path that names a potential directory entry in a common
       location for temporary files.  Applications are responsible for properly
       creating and managing files created using paths returned by :func:`tmpnam`; no
       automatic cleanup is provided."""
    return ""

def ttyname(fd):
    """Return a string which specifies the terminal device associated with
       file descriptor *fd*.  If *fd* is not associated with a terminal device, an
       exception is raised."""
    return ""

def umask(mask):
    """Set the current numeric umask and return the previous umask."""
    return 0777

def uname():
    pass

def unlink(path):
    """Remove (delete) the file *path*.  This is the same function as
       :func:`remove`; the :func:`unlink` name is its traditional Unix
       name."""

def unsetenv(varname):
    """.. index:: single: environment variables; deleting"""

def urandom(n):
    """Return a string of *n* random bytes suitable for cryptographic use."""
    return ""

def utime(path, times):
    """Set the access and modified times of the file specified by *path*. If *times*
       is ``None``, then the file's access and modified times are set to the current
       time. (The effect is similar to running the Unix program :program:`touch` on
       the path.)  Otherwise, *times* must be a 2-tuple of numbers, of the form
       ``(atime, mtime)`` which is used to set the access and modified times,
       respectively. Whether a directory can be given for *path* depends on whether
       the operating system implements directories as files (for example, Windows
       does not).  Note that the exact times you set here may not be returned by a
       subsequent :func:`~os.stat` call, depending on the resolution with which your
       operating system records access and modification times; see :func:`~os.stat`."""

def wait():
    """Wait for completion of a child process, and return a tuple containing its pid
       and exit status indication: a 16-bit number, whose low byte is the signal number
       that killed the process, and whose high byte is the exit status (if the signal
       number is zero); the high bit of the low byte is set if a core file was
       produced."""
    return (0, 0)

def wait3(options=0):
    """Similar to :func:`waitpid`, except no process id argument is given and a
       3-element tuple containing the child's process id, exit status indication, and
       resource usage information is returned.  Refer to :mod:`resource`.\
       :func:`getrusage` for details on resource usage information.  The option
       argument is the same as that provided to :func:`waitpid` and :func:`wait4`."""
    return (0, 0, 0)

def wait4(pid, options):
    """Similar to :func:`waitpid`, except a 3-element tuple, containing the child's
       process id, exit status indication, and resource usage information is returned.
       Refer to :mod:`resource`.\ :func:`getrusage` for details on resource usage
       information.  The arguments to :func:`wait4` are the same as those provided to
       :func:`waitpid`."""
    return (0, 0, 0)

def waitpid(pid, options):
    """The details of this function differ on Unix and Windows."""

def walk(top, topdown=True , onerror=None, followlinks=False):
    pass

def write(fd, str):
    """Write the string *str* to file descriptor *fd*. Return the number of bytes
       actually written."""
    return 0

