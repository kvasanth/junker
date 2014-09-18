mega Inc license
# Copyright (c) 2003-2014 ZeOmega Inc
# http://www.zeomega.com
# All rights reserved.
#
# ZeOmega software [both binary and source (if released)] (hereafter,
# Software) is intellectual property owned by ZeOmega Inc is copyright
# of ZeOmega Inc in all countries in the world, and ownership remains
# with ZeOmega Inc The Software is protected by the copyright laws of
# the United States and international copyright treaties.  Licensee is
# not allowed to distribute the binary and source code (if released) to
# third parties.  Licensee is not allowed to reverse engineer,
# disassemble or decompile code, or make any modifications of the binary
# or source code, remove or alter any trademark, logo, copyright or
# other proprietary notices, legends, symbols, or labels in the
# Software.  Licensee is not allowed to sub-license the Software or any
# derivative work based on or derived from the Software.  Neither the
# names of ZeOmega Inc , nor the names of its contributors may be used
# to endorse or promote products derived from this Software without
# specific prior written permission.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE.
#
#########################################################################
##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Bootstrap a buildout-based project

Simply run this script in a directory containing a buildout.cfg.
The script accepts buildout command-line options, so you can
use the -c option to specify an alternate configuration file.

$Id$
"""

bzip_error_statement = """

Python is compiled without Bzip2 support.
Install Bzip2 development libraries and install Python again.
Note: For Fedora/RHEL/CentOS install 'bzip2-devel' package.
Note: For Debian/Ubuntu install 'libbz2-dev' package.
               OR
Install python by source
command : ./isnallpy26.sh -s

"""

ssl_error_statement = """

Python is compiled without SSL support.
Install SSL development libraries and install Python again.
Note: For Fedora/RHEL/CentOS install 'openssl-devel' package.
Note: For Debian/Ubuntu install 'libssl-dev' package.
              OR
Install python by source
command : ./installpy26.sh -s

"""

import os, shutil, sys, tempfile, urllib2
from optparse import OptionParser
import socket
if not hasattr(socket, 'ssl'):
    print ssl_error_statement
    sys.exit(1)

try:
    import bz2
except ImportError:
    print bzip_error_statement
    sys.exit(1)

if sys.platform == 'linux2':
    if os.geteuid() == 0:
        print "Jiva should be installed as a normal user."
        sys.exit(1)

#tmpeggs = tempfile.mkdtemp()
if not os.path.exists(os.path.join(os.getcwd(), 'tmp')):
   os.makedirs((os.path.join(os.getcwd(), 'tmp')))
tmpeggs = tempfile.mkdtemp(dir=os.path.join(os.getcwd(), 'tmp'))

is_jython = sys.platform.startswith('java')

# parsing arguments
parser = OptionParser()
parser.add_option("-v", "--version", dest="version",
                          help="use a specific zc.buildout version")

parser.add_option("-d", "--distribute",
                   action="store_true", dest="distribute", default=False,
                   help="Use Disribute rather than Setuptools.")

options, args = parser.parse_args()

if options.version is not None:
    VERSION = '==%s' % options.version
else:
    VERSION = '==1.7.1'

#USE_DISTRIBUTE = options.distribute
USE_DISTRIBUTE = 1
args = args + ['bootstrap']

to_reload = False

realm = 'ZeOmega Packages Site , Access Password Required'
uri = 'packages.zeomega.org'
user = 'pkgadmin'
passwd = 'pypize'
authinfo = urllib2.HTTPBasicAuthHandler()
authinfo.add_password(realm,
                      uri,
                      user,
                      passwd)
opener = urllib2.build_opener(authinfo)
urllib2.install_opener(opener)
try:
    import pkg_resources
    if not hasattr(pkg_resources, '_distribute'):
        to_reload = True
        raise ImportError
except ImportError:
    ez = {}
    if USE_DISTRIBUTE:
        exec urllib2.urlopen('https://packages.zeomega.org/zepackages/distribute_setup.py'
                         ).read() in ez
        ez['use_setuptools'](to_dir=tmpeggs, download_delay=0, no_fake=True)
    else:
        exec urllib2.urlopen('https://packages.zeomega.org/zepackages/ez_setup.py'
                             ).read() in ez
        ez['use_setuptools'](to_dir=tmpeggs, download_delay=0)

    if to_reload:
        reload(pkg_resources)
    else:
        import pkg_resources

if sys.platform == 'win32':
    def quote(c):
        if ' ' in c:
            return '"%s"' % c # work around spawn lamosity on windows
        else:
            return c
else:
    def quote (c):
        return c

cmd = 'from setuptools.command.easy_install import main; main()'
ws  = pkg_resources.working_set

if USE_DISTRIBUTE:
    requirement = 'distribute'
else:
    requirement = 'setuptools'

if is_jython:
    import subprocess

    assert subprocess.Popen([sys.executable] + ['-c', quote(cmd), '-mqNxd',
           quote(tmpeggs), 'zc.buildout' + VERSION],
           env=dict(os.environ,
               PYTHONPATH=
               ws.find(pkg_resources.Requirement.parse(requirement)).location
               ),
           ).wait() == 0

else:
    assert os.spawnle(
        os.P_WAIT, sys.executable, quote (sys.executable),
        '-c', quote (cmd), '-mqNxd', quote (tmpeggs), 'zc.buildout' + VERSION,
        dict(os.environ,
            PYTHONPATH=
            ws.find(pkg_resources.Requirement.parse(requirement)).location
            ),
        ) == 0

ws.add_entry(tmpeggs)
ws.require('zc.buildout' + VERSION)
import zc.buildout.buildout
zc.buildout.buildout.main(args)
shutil.rmtree(tmpeggs)

