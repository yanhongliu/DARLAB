"""Cache lines from files.

This is intended to read lines from modules imported -- hence if a filename
is not found, it will look down the module search path for a file by
that name.
"""

import sys
import os

__all__ = ["getline", "clearcache", "checkcache"]

def getline(filename, lineno):
    return string()

# The cache

cache = {} # The cache


def clearcache():
    pass

def getlines(filename):
    return [string()]

def checkcache(filename=None):
    pass

def updatecache(filename):
    return [string()]
