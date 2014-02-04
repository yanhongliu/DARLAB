"""
Version numbers exposed by PyPy through the 'sys' module.
"""
import os


CPYTHON_VERSION            = (2, 4, 1, "alpha", 42)
CPYTHON_API_VERSION        = 1012

PYPY_VERSION               = (1, 0, 0, "alpha", '?')
# the last item is replaced by the svn revision ^^^

SVN_URL = "$HeadURL: http://codespeak.net/svn/pypy/dist/pypy/module/sys/version.py $"[10:-28]

REV = "$LastChangedRevision: 55235 $"[22:-2]


import pypy
pypydir = os.path.dirname(os.path.abspath(pypy.__file__))
del pypy

# ____________________________________________________________

def get_api_version(space):
    return space.wrap(CPYTHON_API_VERSION)

def get_version_info(space):
    return space.wrap(CPYTHON_VERSION)

def get_version(space):
    return space.wrap("%d.%d.%d (pypy %d.%d.%d build %d)" % (
        CPYTHON_VERSION[0],
        CPYTHON_VERSION[1],
        CPYTHON_VERSION[2],
        PYPY_VERSION[0],
        PYPY_VERSION[1],
        PYPY_VERSION[2],
        svn_revision()))

def get_hexversion(space):
    return space.wrap(tuple2hex(CPYTHON_VERSION))

def get_pypy_version_info(space):
    ver = PYPY_VERSION
    ver = ver[:-1] + (svn_revision(),)
    return space.wrap(ver)

def get_svn_url(space):
    return space.wrap((SVN_URL, svn_revision()))

def tuple2hex(ver):
    d = {'alpha':     0xA,
         'beta':      0xB,
         'candidate': 0xC,
         'final':     0xF,
         }
    subver = ver[4]
    if not (0 <= subver <= 9):
        subver = 0
    return (ver[0] << 24   |
            ver[1] << 16   |
            ver[2] << 8    |
            d[ver[3]] << 4 |
            subver)

def _magic(space):
    from pypy.module.__builtin__.importing import get_pyc_magic
    return space.wrap(get_pyc_magic(space))

def svn_revision():
    "Return the last-changed svn revision number."
    # NB. we hack the number directly out of the .svn directory to avoid
    # to depend on an external 'svn' executable in the path.
    rev = int(REV)
    try:
        f = open(os.path.join(pypydir, '.svn', 'format'), 'r')
        format = int(f.readline().strip())
        f.close()
        if format <= 6: # Old XML-format
            f = open(os.path.join(pypydir, '.svn', 'entries'), 'r')
            for line in f:
                line = line.strip()
                if line.startswith('committed-rev="') and line.endswith('"'):
                    rev = int(line[15:-1])
                    break
            f.close()
        else: # New format
            f = open(os.path.join(pypydir, '.svn', 'entries'), 'r')
            format = int(f.readline().strip())
            for entry in f.read().split('\f'):
                lines = entry.split('\n')
                name, kind, revstr = lines[:3]
                if name == '' and kind == 'dir': # The current directory
                    rev = int(revstr)
                    break
            f.close()
    except (IOError, OSError):
        pass
    return rev
