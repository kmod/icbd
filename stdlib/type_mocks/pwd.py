# generated with make_mock.py

def getpwall():
    """Return a list of all available password database entries, in arbitrary order."""
    return struct_passwd()

def getpwnam(name):
    """Return the password database entry for the given user name."""
    return struct_passwd()

def getpwuid(uid):
    """Return the password database entry for the given numeric user ID."""
    return struct_passwd(pw_name='root', pw_passwd='x', pw_uid=0, pw_gid=0, pw_gecos='root', pw_dir='/root', pw_shell='/bin/bash')

class struct_passwd(object):

    n_fields = 7
    n_sequence_fields = 7
    n_unnamed_fields = 0


class struct_pwent(object):

    n_fields = 7
    n_sequence_fields = 7
    n_unnamed_fields = 0


