# generated with make_mock.py

ITIMER_PROF = 2L
ITIMER_REAL = 0L
ITIMER_VIRTUAL = 1L
class ItimerError(IOError):
    pass

NSIG = 65
SIGABRT = 6
SIGALRM = 14
SIGBUS = 7
SIGCHLD = 17
SIGCLD = 17
SIGCONT = 18
SIGFPE = 8
SIGHUP = 1
SIGILL = 4
SIGINT = 2
SIGIO = 29
SIGIOT = 6
SIGKILL = 9
SIGPIPE = 13
SIGPOLL = 29
SIGPROF = 27
SIGPWR = 30
SIGQUIT = 3
SIGRTMAX = 64
SIGRTMIN = 34
SIGSEGV = 11
SIGSTOP = 19
SIGSYS = 31
SIGTERM = 15
SIGTRAP = 5
SIGTSTP = 20
SIGTTIN = 21
SIGTTOU = 22
SIGURG = 23
SIGUSR1 = 10
SIGUSR2 = 12
SIGVTALRM = 26
SIGWINCH = 28
SIGXCPU = 24
SIGXFSZ = 25
SIG_DFL = 0
SIG_IGN = 1

def alarm(time):
    """If *time* is non-zero, this function requests that a :const:`SIGALRM` signal be
       sent to the process in *time* seconds. Any previously scheduled alarm is
       canceled (only one alarm can be scheduled at any time).  The returned value is
       then the number of seconds before any previously set alarm was to have been
       delivered. If *time* is zero, no alarm is scheduled, and any scheduled alarm is
       canceled.  If the return value is zero, no alarm is currently scheduled.  (See
       the Unix man page :manpage:`alarm(2)`.) Availability: Unix."""
    return 0

def default_int_handler(*args, **kw):
    pass

def getitimer(which):
    """Returns current value of a given interval timer specified by *which*.
       Availability: Unix."""
    return (0.0, 0.0)

def getsignal(signalnum):
    """Return the current signal handler for the signal *signalnum*. The returned value
       may be a callable Python object, or one of the special values
       :const:`signal.SIG_IGN`, :const:`signal.SIG_DFL` or :const:`None`.  Here,
       :const:`signal.SIG_IGN` means that the signal was previously ignored,
       :const:`signal.SIG_DFL` means that the default way of handling the signal was
       previously in use, and ``None`` means that the previous signal handler was not
       installed from Python."""
    return 0

def pause():
    """Cause the process to sleep until a signal is received; the appropriate handler
       will then be called.  Returns nothing.  Not on Windows. (See the Unix man page
       :manpage:`signal(2)`.)"""
    return None

def set_wakeup_fd(fd):
    """Set the wakeup fd to *fd*.  When a signal is received, a ``'\0'`` byte is
       written to the fd.  This can be used by a library to wakeup a poll or select
       call, allowing the signal to be fully processed."""
    return -1L

def setitimer(which, seconds, interval=0):
    """Sets given interval timer (one of :const:`signal.ITIMER_REAL`,
       :const:`signal.ITIMER_VIRTUAL` or :const:`signal.ITIMER_PROF`) specified
       by *which* to fire after *seconds* (float is accepted, different from
       :func:`alarm`) and after that every *interval* seconds. The interval
       timer specified by *which* can be cleared by setting seconds to zero."""
    return (0.0, 0.0)

def siginterrupt(signalnum, flag):
    """Change system call restart behaviour: if *flag* is :const:`False`, system
       calls will be restarted when interrupted by signal *signalnum*, otherwise
       system calls will be interrupted.  Returns nothing.  Availability: Unix (see
       the man page :manpage:`siginterrupt(3)` for further information)."""
    return None

def signal(signalnum, handler):
    """Set the handler for signal *signalnum* to the function *handler*.  *handler* can
       be a callable Python object taking two arguments (see below), or one of the
       special values :const:`signal.SIG_IGN` or :const:`signal.SIG_DFL`.  The previous
       signal handler will be returned (see the description of :func:`getsignal`
       above).  (See the Unix man page :manpage:`signal(2)`.)"""
    return 0

