# This file is managed through a combination of puppet and encap.
# The source is modules/python/files/sitecustomize.py in the puppet repo.
# After changing it, run the following as root on pusher0:
#   dbops/tools/sync_puppet.sh
#   puppetd -t
#   dbops/tools/sync_pushers.sh
# This will update the encap distribution directory.  After that, run
# sync_encap.sh on each machine to update the live copy of this file.

import os, site, sys

update_sys_path = True
if hasattr(sys, 'real_prefix'):
    # we're in a virtualenv
    if os.path.exists(os.path.join(os.path.dirname(site.__file__), 'no-global-site-packages.txt')):
        # the virtualenv has --no-site-packages
        update_sys_path = False
        
if update_sys_path:
    site.addsitedir('/usr/local/lib/python%u.%u/site-packages' % sys.version_info[:2])
    site.addsitedir('/db/metaserver')
    site.addsitedir('/srv/dbops/python')

import exceptions, warnings
warnings.simplefilter('ignore', exceptions.DeprecationWarning)

# With versions of setuptools < 0.6c10, pkg_resources prints a warning
# if it is imported after certain packages (we don't use pkg_resources
# ourselves, but e.g. MySQLdb does).  Force it to be imported at startup
# so it won't complain and clutter script output in subtle and
# import-order-dependent ways.
import pkg_resources

