"""
Implementation of the interpreter-level default import logic.
"""

import sys, os, stat

from pypy.interpreter.module import Module
from pypy.interpreter import gateway
from pypy.interpreter.error import OperationError
from pypy.interpreter.baseobjspace import W_Root, ObjSpace
from pypy.interpreter.eval import Code
from pypy.rlib import streamio
from pypy.rlib.streamio import StreamErrors
from pypy.rlib.rarithmetic import intmask
from pypy.rlib.objectmodel import we_are_translated

NOFILE = 0
PYFILE = 1
PYCFILE = 2

def find_modtype(space, filepart):
    """Check which kind of module to import for the given filepart,
    which is a path without extension.  Returns PYFILE, PYCFILE or
    NOFILE.
    """
    # check the .py file
    pyfile = filepart + ".py"
    if os.path.exists(pyfile):
        pyfile_ts = os.stat(pyfile)[stat.ST_MTIME]
        pyfile_exists = True
    else:
        # The .py file does not exist.  By default on PyPy, lonepycfiles
        # is False: if a .py file does not exist, we don't even try to
        # look for a lone .pyc file.
        if not space.config.objspace.lonepycfiles:
            return NOFILE
        pyfile_ts = 0
        pyfile_exists = False

    # check the .pyc file
    if space.config.objspace.usepycfiles:
        pycfile = filepart + ".pyc"    
        if check_compiled_module(space, pycfile, pyfile_ts):
            return PYCFILE     # existing and up-to-date .pyc file

    # no .pyc file, use the .py file if it exists
    if pyfile_exists:
        return PYFILE
    else:
        return NOFILE

def _prepare_module(space, w_mod, filename, pkgdir):
    w = space.wrap
    space.sys.setmodule(w_mod)
    space.setattr(w_mod, w('__file__'), space.wrap(filename))
    space.setattr(w_mod, w('__doc__'), space.w_None)
    if pkgdir is not None:
        space.setattr(w_mod, w('__path__'), space.newlist([w(pkgdir)]))    

def try_import_mod(space, w_modulename, filepart, w_parent, w_name, pkgdir=None):

    # decide what type we want (pyc/py)
    modtype = find_modtype(space, filepart)

    if modtype == NOFILE:
        return None

    w = space.wrap
    w_mod = w(Module(space, w_modulename))

    try:
        if modtype == PYFILE:
            filename = filepart + ".py"
            stream = streamio.open_file_as_stream(filename, "rU")
        else:
            assert modtype == PYCFILE
            filename = filepart + ".pyc"
            stream = streamio.open_file_as_stream(filename, "rb")

        try:
            _prepare_module(space, w_mod, filename, pkgdir)
            try:
                if modtype == PYFILE:
                    load_source_module(space, w_modulename, w_mod, filename,
                                       stream.readall())
                else:
                    magic = _r_long(stream)
                    timestamp = _r_long(stream)
                    load_compiled_module(space, w_modulename, w_mod, filename,
                                         magic, timestamp, stream.readall())

            except OperationError, e:
                w_mods = space.sys.get('modules')
                space.call_method(w_mods,'pop', w_modulename, space.w_None)
                raise
        finally:
            stream.close()

    except StreamErrors:
        return None

    w_mod = check_sys_modules(space, w_modulename)
    if w_mod is not None and w_parent is not None:
        space.setattr(w_parent, w_name, w_mod)
    return w_mod

def try_getattr(space, w_obj, w_name):
    try:
        return space.getattr(w_obj, w_name)
    except OperationError, e:
        # ugh, but blame CPython :-/ this is supposed to emulate
        # hasattr, which eats all exceptions.
        return None

def try_getitem(space, w_obj, w_key):
    try:
        return space.getitem(w_obj, w_key)
    except OperationError, e:
        if not e.match(space, space.w_KeyError):
            raise
        return None


def check_sys_modules(space, w_modulename):
    w_modules = space.sys.get('modules')
    try:
        w_mod = space.getitem(w_modules, w_modulename) 
    except OperationError, e:
        pass
    else:
        return w_mod
    if not e.match(space, space.w_KeyError):
        raise
    return None

def importhook(space, modulename, w_globals=None,
               w_locals=None, w_fromlist=None):
    timername = "importhook " + modulename
    space.timer.start(timername)
    if not modulename:
        raise OperationError(
            space.w_ValueError,
            space.wrap("Empty module name"))
    w = space.wrap

    ctxt_name = None
    if w_globals is not None and not space.is_w(w_globals, space.w_None):
        ctxt_w_name = try_getitem(space, w_globals, w('__name__'))
        ctxt_w_path = try_getitem(space, w_globals, w('__path__'))
        if ctxt_w_name is not None:
            try:
                ctxt_name = space.str_w(ctxt_w_name)
            except OperationError, e:
                if not e.match(space, space.w_TypeError):
                    raise
    else:
        ctxt_w_path = None

    rel_modulename = None
    if ctxt_name is not None:

        ctxt_name_prefix_parts = ctxt_name.split('.')
        if ctxt_w_path is None: # context is a plain module
            ctxt_name_prefix_parts = ctxt_name_prefix_parts[:-1]
            if ctxt_name_prefix_parts:
                rel_modulename = '.'.join(ctxt_name_prefix_parts+[modulename])
        else: # context is a package module
            rel_modulename = ctxt_name+'.'+modulename
        if rel_modulename is not None:
            w_mod = check_sys_modules(space, w(rel_modulename))
            if (w_mod is None or
                not space.is_w(w_mod, space.w_None)):
                
                w_mod = absolute_import(space, rel_modulename,
                                        len(ctxt_name_prefix_parts),
                                        w_fromlist, tentative=1)
                if w_mod is not None:
                    space.timer.stop(timername)
                    return w_mod
            else:
                rel_modulename = None

    w_mod = absolute_import(space, modulename, 0, w_fromlist, tentative=0)
    if rel_modulename is not None:
        space.setitem(space.sys.get('modules'), w(rel_modulename),space.w_None)
    space.timer.stop(timername)
    return w_mod
#
importhook.unwrap_spec = [ObjSpace,str,W_Root,W_Root,W_Root]

def absolute_import(space, modulename, baselevel, w_fromlist, tentative):
    lock = getimportlock(space)
    lock.acquire_lock()
    try:
        return _absolute_import(space, modulename, baselevel,
                                w_fromlist, tentative)
    finally:
        lock.release_lock()

def _absolute_import(space, modulename, baselevel, w_fromlist, tentative):
    w = space.wrap
    
    w_mod = None
    parts = modulename.split('.')
    prefix = []
    # it would be nice if we could do here: w_path = space.sys.w_path
    # instead:
    w_path = space.sys.get('path') 

    first = None
    level = 0

    for part in parts:
        w_mod = load_part(space, w_path, prefix, part, w_mod,
                          tentative=tentative)
        if w_mod is None:
            return None

        if baselevel == level:
            first = w_mod
            tentative = 0
        prefix.append(part)
        w_path = try_getattr(space, w_mod, w('__path__'))
        level += 1

    if w_fromlist is not None and space.is_true(w_fromlist):
        if w_path is not None:
            fromlist_w = space.unpackiterable(w_fromlist)
            if len(fromlist_w) == 1 and space.eq_w(fromlist_w[0],w('*')):
                w_all = try_getattr(space, w_mod, w('__all__'))
                if w_all is not None:
                    fromlist_w = space.unpackiterable(w_all)
            for w_name in fromlist_w:
                if try_getattr(space, w_mod, w_name) is None:
                    load_part(space, w_path, prefix, space.str_w(w_name), w_mod,
                              tentative=1)
        return w_mod
    else:
        return first

def load_part(space, w_path, prefix, partname, w_parent, tentative):
    w = space.wrap
    modulename = '.'.join(prefix + [partname])
    w_modulename = w(modulename)
    w_mod = check_sys_modules(space, w_modulename)
    if w_mod is not None:
        if not space.is_w(w_mod, space.w_None):
            return w_mod
    else:
        # Examin importhooks (PEP302) before doing the import
        if w_path is not None:
            w_loader  = find_module(space, w_modulename, w_path) 
        else:
            w_loader  = find_module(space, w_modulename, space.w_None)
        if not space.is_w(w_loader, space.w_None):
            w_mod = space.call_method(w_loader, "load_module", w_modulename)
            #w_mod_ = check_sys_modules(space, w_modulename)
            if w_mod is not None and w_parent is not None:
                space.setattr(w_parent, w(partname), w_mod)

            return w_mod


        if w_path is not None:
            for path in space.unpackiterable(w_path):
                dir = os.path.join(space.str_w(path), partname)
                if os.path.isdir(dir):
                    fn = os.path.join(dir, '__init__')
                    w_mod = try_import_mod(space, w_modulename, fn,
                                           w_parent, w(partname),
                                           pkgdir=dir)
                    if w_mod is not None:
                        return w_mod
                fn = os.path.join(space.str_w(path), partname)
                w_mod = try_import_mod(space, w_modulename, fn, w_parent,
                                       w(partname))
                if w_mod is not None:
                    return w_mod

    if tentative:
        return None
    else:
        # ImportError
        msg = "No module named %s" % modulename
        raise OperationError(space.w_ImportError, w(msg))

# __________________________________________________________________
#
# import lock, to prevent two threads from running module-level code in
# parallel.  This behavior is more or less part of the language specs,
# as an attempt to avoid failure of 'from x import y' if module x is
# still being executed in another thread.

# This logic is tested in pypy.module.thread.test.test_import_lock.

class ImportRLock:

    def __init__(self, space):
        self.space = space
        self.lock = None
        self.lockowner = None
        self.lockcounter = 0

    def lock_held(self):
        me = self.space.getexecutioncontext()   # used as thread ident
        return self.lockowner is me

    def _can_have_lock(self):
        # hack: we can't have self.lock != None during translation,
        # because prebuilt lock objects are not allowed.  In this
        # special situation we just don't lock at all (translation is
        # not multithreaded anyway).
        if we_are_translated():
            return True     # we need a lock at run-time
        elif self.space.config.translating:
            assert self.lock is None
            return False
        else:
            return True     # in py.py

    def acquire_lock(self):
        # this function runs with the GIL acquired so there is no race
        # condition in the creation of the lock
        if self.lock is None:
            if not self._can_have_lock():
                return
            self.lock = self.space.allocate_lock()
        me = self.space.getexecutioncontext()   # used as thread ident
        if self.lockowner is me:
            pass    # already acquired by the current thread
        else:
            self.lock.acquire(True)
            assert self.lockowner is None
            assert self.lockcounter == 0
            self.lockowner = me
        self.lockcounter += 1

    def release_lock(self):
        me = self.space.getexecutioncontext()   # used as thread ident
        if self.lockowner is not me:
            if not self._can_have_lock():
                return
            space = self.space
            raise OperationError(space.w_RuntimeError,
                                 space.wrap("not holding the import lock"))
        assert self.lockcounter > 0
        self.lockcounter -= 1
        if self.lockcounter == 0:
            self.lockowner = None
            self.lock.release()

def getimportlock(space):
    return space.fromcache(ImportRLock)

# __________________________________________________________________
#
# .pyc file support

"""
   Magic word to reject .pyc files generated by other Python versions.
   It should change for each incompatible change to the bytecode.

   The value of CR and LF is incorporated so if you ever read or write
   a .pyc file in text mode the magic number will be wrong; also, the
   Apple MPW compiler swaps their values, botching string constants.

   CPython uses values between 20121 - 62xxx

"""

# we decided to use our own magic number starting from 1024
# and we have 10 potential bits for different opcodes free.
#
# The presence of special bytecodes bumps the
# magic number:
#
#  * CALL_LIKELY_BUILTIN    +2
#  * CALL_METHOD            +4
#
#
MAGIC = 1024 | (ord('\r')<<16) | (ord('\n')<<24)
MARSHAL_VERSION_FOR_PYC = 2

def get_pyc_magic(space):
    result = MAGIC
    if space.config.objspace.opcodes.CALL_LIKELY_BUILTIN:
        result += 2
    if space.config.objspace.opcodes.CALL_METHOD:
        result += 4
    return result


def parse_source_module(space, pathname, source):
    """ Parse a source file and return the corresponding code object """
    ec = space.getexecutioncontext()
    pycode = ec.compiler.compile(source, pathname, 'exec', 0)
    return pycode

def load_source_module(space, w_modulename, w_mod, pathname, source,
                       write_pyc=True):
    """
    Load a source module from a given file and return its module
    object.
    """
    pycode = parse_source_module(space, pathname, source)

    if space.config.objspace.usepycfiles and write_pyc:
        mtime = os.stat(pathname)[stat.ST_MTIME]
        cpathname = pathname + 'c'
        write_compiled_module(space, pycode, cpathname, mtime)

    w = space.wrap
    w_dict = space.getattr(w_mod, w('__dict__'))
    space.call_method(w_dict, 'setdefault',
                      w('__builtins__'),
                      w(space.builtin))
    pycode.exec_code(space, w_dict, w_dict)

    return w_mod

def _get_long(s):
    a = ord(s[0])
    b = ord(s[1])
    c = ord(s[2])
    d = ord(s[3])
    if d >= 0x80:
        d -= 0x100
    return a | (b<<8) | (c<<16) | (d<<24)

def _read_n(stream, n):
    buf = ''
    while len(buf) < n:
        data = stream.read(n - len(buf))
        if not data:
            raise streamio.StreamError("end of file")
        buf += data
    return buf

def _r_long(stream):
    s = _read_n(stream, 4)
    return _get_long(s)

def _w_long(stream, x):
    a = x & 0xff
    x >>= 8
    b = x & 0xff
    x >>= 8
    c = x & 0xff
    x >>= 8
    d = x & 0xff
    stream.write(chr(a) + chr(b) + chr(c) + chr(d))

def check_compiled_module(space, pycfilename, expected_mtime=0):
    """
    Check if a pyc file's magic number and (optionally) mtime match.
    """
    try:
        stream = streamio.open_file_as_stream(pycfilename, "rb")
        try:
            magic = _r_long(stream)
            if magic != get_pyc_magic(space):
                return False
            if expected_mtime != 0:
                pyc_mtime = _r_long(stream)
                if pyc_mtime != expected_mtime:
                    return False
        finally:
            stream.close()
    except StreamErrors:
        return False
    return True

def read_compiled_module(space, cpathname, strbuf):
    """ Read a code object from a file and check it for validity """
    
    w_marshal = space.getbuiltinmodule('marshal')
    w_code = space.call_method(w_marshal, 'loads', space.wrap(strbuf))
    pycode = space.interpclass_w(w_code)
    if pycode is None or not isinstance(pycode, Code):
        raise OperationError(space.w_ImportError, space.wrap(
            "Non-code object in %s" % cpathname))
    return pycode

def load_compiled_module(space, w_modulename, w_mod, cpathname, magic,
                         timestamp, source):
    """
    Load a module from a compiled file, execute it, and return its
    module object.
    """
    w = space.wrap
    if magic != get_pyc_magic(space):
        raise OperationError(space.w_ImportError, w(
            "Bad magic number in %s" % cpathname))
    #print "loading pyc file:", cpathname
    code_w = read_compiled_module(space, cpathname, source)
    #if (Py_VerboseFlag)
    #    PySys_WriteStderr("import %s # precompiled from %s\n",
    #        name, cpathname);
    w_dic = space.getattr(w_mod, w('__dict__'))
    space.call_method(w_dic, 'setdefault', 
                      w('__builtins__'), 
                      w(space.builtin))
    code_w.exec_code(space, w_dic, w_dic)
    return w_mod


def write_compiled_module(space, co, cpathname, mtime):
    """
    Write a compiled module to a file, placing the time of last
    modification of its source into the header.
    Errors are ignored, if a write error occurs an attempt is made to
    remove the file.
    """
    w_marshal = space.getbuiltinmodule('marshal')
    try:
        w_str = space.call_method(w_marshal, 'dumps', space.wrap(co),
                                  space.wrap(MARSHAL_VERSION_FOR_PYC))
        strbuf = space.str_w(w_str)
    except OperationError, e:
        if e.async(space):
            raise
        #print "Problem while marshalling %s, skipping" % cpathname
        return
    #
    # Careful here: we must not crash nor leave behind something that looks
    # too much like a valid pyc file but really isn't one.
    #
    try:
        stream = streamio.open_file_as_stream(cpathname, "wb")
    except StreamErrors:
        return    # cannot create file
    try:
        try:
            # will patch the header later; write zeroes until we are sure that
            # the rest of the file is valid
            _w_long(stream, 0)   # pyc_magic
            _w_long(stream, 0)   # mtime
            stream.write(strbuf)

            # should be ok (XXX or should call os.fsync() to be sure?)
            stream.seek(0, 0)
            _w_long(stream, get_pyc_magic(space))
            _w_long(stream, mtime)
        finally:
            stream.close()
    except StreamErrors:
        try:
            os.unlink(cpathname)
        except OSError:
            pass


app = gateway.applevel(
r"""    
# Implement pep302

IMP_HOOK = 9

def find_module(fullname,  path):
    import sys
    meta_path = sys.meta_path
    for hook in meta_path:
        loader = hook.find_module(fullname,  path)
        if loader:
            return loader
    if path != None and type(path) == str:
        pass
        # XXX Check for frozen modules ?
    if path == None:
        # XXX Check frozen
        path = sys.path
    path_hooks = sys.path_hooks
    importer_cache = sys.path_importer_cache 
    importer = None
    for p in path:
        if importer_cache.get(p,None):
            importer = importer_cache.get(p)
        else:
            importer_cache[p] = None
            importer = None
            for hook in path_hooks:
                try:
                    importer = hook(p)
                except ImportError:
                    pass
                else:
                    break
            if importer:
                importer_cache[p] = importer
        if importer:
            loader = importer.find_module(fullname)
            if loader:
                return loader
     #no hooks match - do normal import
    """) 

find_module = app.interphook('find_module')

