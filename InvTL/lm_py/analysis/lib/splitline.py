#!/usr/bin/env python
"""
Defines LineSplitter and helper functions.

-----
Permission to use, modify, and distribute this software is given under the
terms of the NumPy License. See http://scipy.org.

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
Author: Pearu Peterson <pearu@cens.ioc.ee>
Created: May 2006
-----
"""

__all__ = ['String','string_replace_map','splitquote','splitparen']

import re

class String(string): 
    def __init__(self,val=""):
        return string.__init__(val)
class ParenString(string): 
    def __init__(self,val=""):
        return string.__init__(val)

def split2(line, lower=False):
    """
    Split line into non-string part and into a start of a string part.
    Returns 2-tuple. The second item either is empty string or start
    of a string part.
    """
    return LineSplitter(line,lower=lower).split2()

class string_replace_dict(dict):
    """
    Dictionary object that is callable for applying map returned
    by string_replace_map() function.
    """
    def __call__(self, line):
        for k in _f2py_findall(line):
            line = line.replace(k, self[k])
        return line

def string_replace_map(line, lower=False,
                       _cache={'index':0,'pindex':0}):
    """
    1) Replaces string constants with symbol `'_F2PY_STRING_CONSTANT_<index>_'`
    2) Replaces (expression) with symbol `(F2PY_EXPR_TUPLE_<index>)`
    Returns a new line and the replacement map.
    """
    string_map = string_replace_dict()
    return line,string_map
       

def splitquote(line, stopchar=None, lower=False, quotechars = '"\''):
    """
    Fast LineSplitter
    """
    items = []
    return items, stopchar

class LineSplitterBase:

    def __iter__(self):
        return self

    def next(self):
        item = ''
        return item

class LineSplitter(LineSplitterBase):
    """ Splits a line into non strings and strings. E.g.
    abc=\"123\" -> ['abc=','\"123\"']
    Handles splitting lines with incomplete string blocks.
    """
    def __init__(self, line,
                 quotechar = None,
                 lower=False,
                 ):
        self.fifo_line = [c for c in line]
        pass
        self.quotechar = quotechar
        self.lower = lower

    def split2(self):
        """
        Split line until the first start of a string.
        """
        return string(),string()

    def get_item(self):
        return String()

def splitparen(line,paren='()'):
    """
    Fast LineSplitterParen.
    """
    items = []
    return items

class LineSplitterParen(LineSplitterBase):
    """ Splits a line into strings and strings with parenthesis. E.g.
    a(x) = b(c,d) -> ['a','(x)',' = b','(c,d)']
    """
    def __init__(self, line, paren = '()'):
        pass

    def get_item(self):
        return ParenString('')

