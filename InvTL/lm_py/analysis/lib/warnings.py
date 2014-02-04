"""Python part of the warnings subsystem."""

# Note: function level imports should *not* be used
# in this module as it may cause import lock deadlock.
# See bug 683658.
import sys, types
import linecache

__all__ = ["warn", "showwarning", "formatwarning", "filterwarnings",
           "resetwarnings"]

# filters contains a sequence of filter 5-tuples
# The components of the 5-tuple are:
# - an action: error, ignore, always, default, module, or once
# - a compiled regex that must match the warning message
# - a class representing the warning category
# - a compiled regex that must match the module that is being warned
# - a line number for the line being warning, or 0 to mean any line
# If either if the compiled regexs are None, match anything.
filters = []
defaultaction = "default"
onceregistry = {}

def warn(message, category=None, stacklevel=1):
    """Issue a warning, or maybe ignore it or raise an exception."""
    pass

def warn_explicit(message, category, filename, lineno,
                  module=None, registry=None):
    pass
    if module is None:
        module = filename or "<unknown>"
        if module[-3:].lower() == ".py":
            module = module[:-3] # XXX What about leading pathname?
    if registry is None:
        registry = {}
    if isinstance(message, Warning):
        text = str(message)

def showwarning(message, category, filename, lineno, file=None):
    """Hook to write a warning to a file; replace if you like."""
    pass

def formatwarning(message, category, filename, lineno):
    return string()+message

def filterwarnings(action, message="", category=Warning, module="", lineno=0,
                   append=0):
    pass

def simplefilter(action, category=Warning, lineno=0, append=0):
    """Insert a simple entry into the list of warnings filters (at the front).

    A simple filter matches all modules and messages.
    """
    pass

def resetwarnings():
    """Clear the list of warning filters, so that no filters are active."""
    pass

class _OptionError(Exception):
    """Exception used by option processing helpers."""
    pass

# Helper to process -W options passed via sys.warnoptions
def _processoptions(args):
    pass

# Helper for _processoptions()
def _setoption(arg):
    pass

# Helper for _setoption()
def _getaction(action):
    return string()

# Helper for _setoption()
def _getcategory(category):
    return string()


