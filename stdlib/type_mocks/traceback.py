# generated with make_mock.py

def extract_stack(f=None, limit=0):
    """Extract the raw traceback from the current stack frame.  The return value has
       the same format as for :func:`extract_tb`.  The optional *f* and *limit*
       arguments have the same meaning as for :func:`print_stack`."""
    return [('make_mock.py', 211, '<module>', 'globals().get("handle_%s" % n, _handle_unknown)(k, v)'), ('make_mock.py', 54, 'handle_method_descriptor', 'r = v(*[a] * i)')]

def extract_tb(traceback, limit=0):
    """Return a list of up to *limit* "pre-processed" stack trace entries extracted
       from the traceback object *traceback*.  It is useful for alternate formatting of
       stack traces.  If *limit* is omitted or ``None``, all entries are extracted.  A
       "pre-processed" stack trace entry is a quadruple (*filename*, *line number*,
       *function name*, *text*) representing the information that is usually printed
       for a stack trace.  The *text* is a string with leading and trailing whitespace
       stripped; if the source is not available it is ``None``."""
    return [('make_mock.py', 211, '<module>', 'globals().get("handle_%s" % n, _handle_unknown)(k, v)'), ('make_mock.py', 54, 'handle_method_descriptor', 'r = v(*[a] * i)')]

def format_exc(limit=0):
    """This is like ``print_exc(limit)`` but returns a string instead of printing to a
       file."""
    return ''

def format_exception(type, value, tb, limit=0):
    """Format a stack trace and the exception information.  The arguments  have the
       same meaning as the corresponding arguments to :func:`print_exception`.  The
       return value is a list of strings, each ending in a newline and some containing
       internal newlines.  When these lines are concatenated and printed, exactly the
       same text is printed as does :func:`print_exception`."""
    return ['']

def format_exception_only(type, value):
    """Format the exception part of a traceback.  The arguments are the exception type
       and value such as given by ``sys.last_type`` and ``sys.last_value``.  The return
       value is a list of strings, each ending in a newline.  Normally, the list
       contains a single string; however, for :exc:`SyntaxError` exceptions, it
       contains several lines that (when printed) display detailed information about
       where the syntax error occurred.  The message indicating which exception
       occurred is the always last string in the list."""
    return ['']

def format_list(list):
    """Given a list of tuples as returned by :func:`extract_tb` or
       :func:`extract_stack`, return a list of strings ready for printing.  Each string
       in the resulting list corresponds to the item with the same index in the
       argument list.  Each string ends in a newline; the strings may contain internal
       newlines as well, for those items whose source text line is not ``None``."""
    return ['']

def format_stack(f=None, limit=0):
    """A shorthand for ``format_list(extract_stack(f, limit))``."""
    return ['  File "make_mock.py", line 211, in <module>\n    globals().get("handle_%s" % n, _handle_unknown)(k, v)\n', '  File "make_mock.py", line 54, in handle_method_descriptor\n    r = v(*[a] * i)\n']

def format_tb(tb, limit=0):
    """A shorthand for ``format_list(extract_tb(tb, limit))``."""
    return ['  File "make_mock.py", line 211, in <module>\n    globals().get("handle_%s" % n, _handle_unknown)(k, v)\n', '  File "make_mock.py", line 54, in handle_method_descriptor\n    r = v(*[a] * i)\n']

def print_exc(limit=0, file=None):
    """This is a shorthand for ``print_exception(sys.exc_type, sys.exc_value,
       sys.exc_traceback, limit, file)``.  (In fact, it uses :func:`sys.exc_info` to
       retrieve the same information in a thread-safe way instead of using the
       deprecated variables.)"""
    return None

def print_exception(type, value, traceback, limit=0, file=None):
    """Print exception information and up to *limit* stack trace entries from
       *traceback* to *file*. This differs from :func:`print_tb` in the following ways:
       (1) if *traceback* is not ``None``, it prints a header ``Traceback (most recent
       call last):``; (2) it prints the exception *type* and *value* after the stack
       trace; (3) if *type* is :exc:`SyntaxError` and *value* has the appropriate
       format, it prints the line where the syntax error occurred with a caret
       indicating the approximate position of the error."""
    return None

def print_last(limit=0, file=None):
    """This is a shorthand for ``print_exception(sys.last_type, sys.last_value,
       sys.last_traceback, limit, file)``.  In general it will work only after
       an exception has reached an interactive prompt (see :data:`sys.last_type`)."""

def print_stack(f=None, limit=0, file=None):
    """This function prints a stack trace from its invocation point.  The optional *f*
       argument can be used to specify an alternate stack frame to start.  The optional
       *limit* and *file* arguments have the same meaning as for
       :func:`print_exception`."""
    return None

def print_tb(traceback, limit=0, file=None):
    """Print up to *limit* stack trace entries from *traceback*.  If *limit* is omitted
       or ``None``, all entries are printed. If *file* is omitted or ``None``, the
       output goes to ``sys.stderr``; otherwise it should be an open file or file-like
       object to receive the output."""
    return None

def tb_lineno(tb):
    """This function returns the current line number set in the traceback object.  This
       function was necessary because in versions of Python prior to 2.3 when the
       :option:`-O` flag was passed to Python the ``tb.tb_lineno`` was not updated
       correctly.  This function has no use in versions past 2.3."""
    return 0

