#
# Secret Labs' Regular Expression Engine
#
# convert template to internal format
#
# Copyright (c) 1997-2001 by Secret Labs AB.  All rights reserved.
#
# See the sre.py file for information on usage and redistribution.
#

"""Internal support module for sre"""

from sre_constants import *

def _identityfunction(x):
    return x

class match:
    pass

class compiledre:
    pass
    def findall(args):
        return []
    def match(s):
        return match()
    def search(s):
        return match()

def _compile(code, pattern, flags=0):
    return compiledre()

def compile(p, flags=0):
    return compiledre()

