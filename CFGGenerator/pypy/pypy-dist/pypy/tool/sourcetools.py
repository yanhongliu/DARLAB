# a couple of support functions which
# help with generating Python source.

# XXX This module provides a similar, but subtly different, functionality
# XXX several times over, which used to be scattered over four modules.
# XXX We should try to generalize and single out one approach to dynamic
# XXX code compilation.

import sys, os, inspect, new
import autopath, py

def render_docstr(func, indent_str='', closing_str=''):
    """ Render a docstring as a string of lines.
        The argument is either a docstring or an object.
        Note that we don't use a sequence, since we want
        the docstring to line up left, regardless of
        indentation. The shorter triple quotes are
        choosen automatically.
        The result is returned as a 1-tuple."""
    if type(func) is not str:
        doc = func.__doc__
    else:
        doc = func
    if doc is None:
        return None
    doc = doc.replace('\\', r'\\')
    compare = []
    for q in '"""', "'''":
        txt = indent_str + q + doc.replace(q[0], "\\"+q[0]) + q + closing_str
        compare.append(txt)
    doc, doc2 = compare
    doc = (doc, doc2)[len(doc2) < len(doc)]
    return doc


class NiceCompile(object):
    """ Compiling parameterized strings in a way that debuggers
        are happy. We provide correct line numbers and a real
        __file__ attribute.
    """
    def __init__(self, namespace_or_filename):
        if type(namespace_or_filename) is str:
            srcname = namespace_or_filename
        else:
            srcname = namespace_or_filename.get('__file__')
        if not srcname:
            # assume the module was executed from the
            # command line.
            srcname = os.path.abspath(sys.argv[-1])
        self.srcname = srcname
        if srcname.endswith('.pyc') or srcname.endswith('.pyo'):
            srcname = srcname[:-1]
        if os.path.exists(srcname):
            self.srcname = srcname
            self.srctext = file(srcname).read()
        else:
            # missing source, what to do?
            self.srctext = None

    def __call__(self, src, args=None):
        """ instance NiceCompile (src, args) -- formats src with args
            and returns a code object ready for exec. Instead of <string>,
            the code object has correct co_filename and line numbers.
            Indentation is automatically corrected.
        """
        if self.srctext:
            try:
                p = self.srctext.index(src)
            except ValueError:
                msg = "Source text not found in %s - use a raw string" % self.srcname
                raise ValueError(msg)
            prelines = self.srctext[:p].count("\n") + 1
        else:
            prelines = 0
        # adjust indented def
        for line in src.split('\n'):
            content = line.strip()
            if content and not content.startswith('#'):
                break
        # see if first line is indented
        if line and line[0].isspace():
            # fake a block
            prelines -= 1
            src = 'if 1:\n' + src
        if args is not None:
            src = '\n' * prelines + src % args
        else:
            src = '\n' * prelines + src
        c = compile(src, self.srcname, "exec")
        # preserve the arguments of the code in an attribute
        # of the code's co_filename
        if self.srcname:
            srcname = MyStr(self.srcname)
            if args is not None:
                srcname.__sourceargs__ = args
            c = newcode_withfilename(c, srcname)
        return c

def getsource(object):
    """ similar to inspect.getsource, but trying to
    find the parameters of formatting generated methods and
    functions.
    """
    name = inspect.getfile(object)
    if hasattr(name, '__source__'):
        src = str(name.__source__)
    else:
        try:
            src = inspect.getsource(object)
        except IOError:
            return None
        except IndentationError:
            return None
    if hasattr(name, "__sourceargs__"):
        return src % name.__sourceargs__
    return src

## the following is stolen from py.code.source.py for now.
## XXX discuss whether and how to put this functionality
## into py.code.source.
#
# various helper functions
#
class MyStr(str):
    """ custom string which allows to add attributes. """

def newcode(fromcode, **kwargs):
    names = [x for x in dir(fromcode) if x[:3] == 'co_']
    for name in names:
        if name not in kwargs:
            kwargs[name] = getattr(fromcode, name)
    import new
    return new.code(
             kwargs['co_argcount'],
             kwargs['co_nlocals'],
             kwargs['co_stacksize'],
             kwargs['co_flags'],
             kwargs['co_code'],
             kwargs['co_consts'],
             kwargs['co_names'],
             kwargs['co_varnames'],
             kwargs['co_filename'],
             kwargs['co_name'],
             kwargs['co_firstlineno'],
             kwargs['co_lnotab'],
             kwargs['co_freevars'],
             kwargs['co_cellvars'],
    )

def newcode_withfilename(co, co_filename):
    newconstlist = []
    cotype = type(co)
    for c in co.co_consts:
        if isinstance(c, cotype):
            c = newcode_withfilename(c, co_filename)
        newconstlist.append(c)
    return newcode(co, co_consts = tuple(newconstlist),
                       co_filename = co_filename)

# ____________________________________________________________

import __future__

def compile2(source, filename='', mode='exec', flags=
             __future__.generators.compiler_flag, dont_inherit=0):
    """
    A version of compile() that caches the code objects it returns.
    It uses py.code.compile() to allow the source to be displayed in tracebacks.
    """
    key = (source, filename, mode, flags)
    try:
        co = compile2_cache[key]
        #print "***** duplicate code ******* "
        #print source 
    except KeyError: 
        #if DEBUG: 
        co = py.code.compile(source, filename, mode, flags) 
        #else: 
        #    co = compile(source, filename, mode, flags) 
        compile2_cache[key] = co 
    return co 

compile2_cache = {}

# ____________________________________________________________

def compile_template(source, resultname):
    """Compiles the source code (a string or a list/generator of lines)
    which should be a definition for a function named 'resultname'.
    The caller's global dict and local variable bindings are captured.
    """
    if not isinstance(source, py.code.Source):
        if isinstance(source, str):
            lines = [source]
        else:
            lines = list(source)
        lines.append('')
        source = py.code.Source('\n'.join(lines))

    caller = sys._getframe(1)
    locals = caller.f_locals
    if locals is caller.f_globals:
        localnames = []
    else:
        localnames = locals.keys()
        localnames.sort()
    values = [locals[key] for key in localnames]
    
    source = source.putaround(
        before = "def container(%s):" % (', '.join(localnames),),
        after  = "# no unindent\n    return %s" % resultname)

    d = {}
    exec source.compile() in caller.f_globals, d
    container = d['container']
    return container(*values)

# ____________________________________________________________

if sys.version_info >= (2, 3):
    def func_with_new_name(func, newname):
        """Make a renamed copy of a function."""
        f = new.function(func.func_code, func.func_globals,
                            newname, func.func_defaults,
                            func.func_closure)
        if func.func_dict: 
            f.func_dict = {}
            f.func_dict.update(func.func_dict) 
        return f 
else:
    raise Exception("sorry, Python 2.2 not supported")
    # because we need to return a new function object -- impossible in 2.2,
    # cannot create functions with closures without using veeeery strange code

PY_IDENTIFIER = ''.join([(('0' <= chr(i) <= '9' or
                           'a' <= chr(i) <= 'z' or
                           'A' <= chr(i) <= 'Z') and chr(i) or '_')
                         for i in range(256)])

def valid_identifier(stuff):
    stuff = str(stuff).translate(PY_IDENTIFIER)
    if not stuff or ('0' <= stuff[0] <= '9'):
        stuff = '_' + stuff
    return stuff

CO_VARARGS      = 0x0004
CO_VARKEYWORDS  = 0x0008

def has_varargs(func):
    func = getattr(func, 'func_code', func)
    return (func.co_flags & CO_VARARGS) != 0

def has_varkeywords(func):
    func = getattr(func, 'func_code', func)
    return (func.co_flags & CO_VARKEYWORDS) != 0

def nice_repr_for_func(fn, name=None):
    mod = getattr(fn, '__module__', None)
    if name is None:
        name = getattr(fn, '__name__', None)
        cls = getattr(fn, 'class_', None)
        if name is not None and cls is not None:
            name = "%s.%s" % (cls.__name__, name)
    try:
        firstlineno = fn.func_code.co_firstlineno
    except AttributeError:
        firstlineno = -1
    return "(%s:%d)%s" % (mod or '?', firstlineno, name or 'UNKNOWN')
