r"""OS routines for Mac, DOS, NT, or Posix depending on what system we're on.

This exports:
  - all functions from posix, nt, os2, mac, or ce, e.g. unlink, stat, etc.
  - os.path is one of the modules posixpath, ntpath, or macpath
  - os.name is 'posix', 'nt', 'os2', 'mac', 'ce' or 'riscos'
  - os.curdir is a string representing the current directory ('.' or ':')
  - os.pardir is a string representing the parent directory ('..' or '::')
  - os.sep is the (or a most common) pathname separator ('/' or ':' or '\\')
  - os.extsep is the extension separator ('.' or '/')
  - os.altsep is the alternate pathname separator (None or '/')
  - os.pathsep is the component separator used in $PATH etc
  - os.linesep is the line separator in text files ('\r' or '\n' or '\r\n')
  - os.defpath is the default search path for executables
  - os.devnull is the file path of the null device ('/dev/null', etc.)

Programs that import and use 'os' stand a better chance of being
portable between different platforms.  Of course, they must then
only use functions that are defined by all platforms (e.g., unlink
and opendir), and leave all pathname manipulation to os.path
(e.g., split and join).
"""

#'

import sys
import posixpath as path
# Super directory utilities.
# (Inspired by Eric Raymond; the doc strings are mostly his)

def makedirs(name, mode=0777):
    pass

def listdir(dir="."):
    return list()

def removedirs(name):
    pass
def renames(old, new):
    pass

def walk(top, topdown=True, onerror=None):
    pass

# Make sure os.environ exists, at least
    environ = {}

def execl(file, *args):
    pass
def execle(file, *args):
    pass

def execlp(file, *args):
    pass
def execlpe(file, *args):
    pass

def execvp(file, args):
    pass

def execvpe(file, args, env):
    pass

def _execvpe(file, args, env=None):
    pass

def getenv(key, default=None):
    return string()

def _exists(name):
    return boolean()


def popen2(cmd, mode="t", bufsize=-1):
    """Execute the shell command 'cmd' in a sub-process.  On UNIX, 'cmd'
    may be a sequence, in which case arguments will be passed directly to
    the program without shell intervention (as with os.spawnv()).  If 'cmd'
    is a string it will be passed to the shell (as with os.system()). If
    'bufsize' is specified, it sets the buffer size for the I/O pipes.  The
    file objects (child_stdin, child_stdout) are returned."""
    return stdin, stdout

def popen3(cmd, mode="t", bufsize=-1):
    """Execute the shell command 'cmd' in a sub-process.  On UNIX, 'cmd'
    may be a sequence, in which case arguments will be passed directly to
    the program without shell intervention (as with os.spawnv()).  If 'cmd'
    is a string it will be passed to the shell (as with os.system()). If
    'bufsize' is specified, it sets the buffer size for the I/O pipes.  The
    file objects (child_stdin, child_stdout, child_stderr) are returned."""
    return stdin, stdout, stderr
def popen4(cmd, mode="t", bufsize=-1):
    return stdin, stdout

def _make_stat_result(tup, dict):
    return int()
class stat:
    def __init__(self):
        self.st_mode=int()
        self.st_rdev=int()
    def S_ISREG(self,param):
        return boolean()
    def S_ISDIR(self,param):
        return boolean()
    def S_ISFIFO(self,param):
        return boolean()
    def S_ISLNK(self,param):
        return boolean()
    def S_ISCHR(self,param):
        return boolean()
    def S_ISBLK(self,param):
        return boolean()

def lstat(file):
    return stat()
def stat(file="."):
    return stat()
def fstat(file):
    return stat()
def urandom(n):
    return string()
def readlink(name):
    return name

def major(x):
    return int()

def minor(x):
    return int()

O_RDONLY = 0
O_CREAT = 2
O_TRUNC = 4
O_WRONLY = 8


def open(file,mode):
    return open(file,mode)

