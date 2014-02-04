import __builtin__
import pickle
import sha
import optparse
import re
import sys
import gc
import pprint
import compiler
import string
import inspect
import os

import LM
import analysis.utils
import analysis.source 
import analysis.output.utils
from analysis.source import AnalysisSession as Analyzer
import ast

import py
log = py.log.Producer("LM_PY:util") 
py.log.setconsumer("LM_PY:util", LM.eventlog) #


def getHash(S):
    return sha.new(S).hexdigest()


#Set up import environment for local large libs
#sys.path.append(os.path.realpath(os.path.split(os.path.split(os.path.realpath(os.path.dirname(__file__)))[0])[0]+"/pypy-dist/pypy"))
#sys.path.append((os.path.dirname(__file__)+"/lm_py"))
#import pypy things, including type annotation, alias analysis, etc... 
#from pypy.annotation import model as annmodel
#from pypy.translator.translator import TranslationContext




#from pypy.rpython.rtyper import *
#from pypy.rpython.rarithmetic import *

from RollbackImporter import RollbackImporter

def iprint(args):
    import sys
    for i in args:
        sys.stdout.write( str(i)+" ")
    sys.stdout.write('\n')
def dprint (*args):
    test=not not False
    if test:
        s=inspect.stack()[1]
        #for k,v in s[0].__dict__.items():
        #    print k , ": ",v
        #print (inspect.getargvalues(s[0]))
        iprint(("#","%s:%d"%(os.path.basename(s[1]),s[2]),"@",s[3]," : ")+args)
def order_substring_tuple(s1,s2):
    if string.find(s1[0],s2[0])!=-1: #s2 elem s1, s1>s2
        return -1
    if string.find(s2[0],s1[0])!=-1: #s1 elem s2, s2>s1
        return +1
    return 0
def getfname (file):
    return os.path.splitext(os.path.split(os.path.realpath(file))[1])[0]

def load_and_wrap(filename,replacement=None):
    f=open(filename,'r')
    if replacement:
        fr=r"(.*)from\s+%s\s+(.+)"%getfname(replacement[0])
        to=r"\1from %s \2"%getfname(replacement[1])
    sys.path.append(os.path.realpath(os.path.split(os.path.realpath(filename))[0]))
    lines=f.readlines()
    #print fr
    #print to
    #if replacement:
    #    for i in lines:
    #        re.sub(fr,to,i)
    lines=[" "+i for i in lines]
    lines="def driver():\n%s\n"%"".join(lines)
    #print lines
    #name="driver_%s.py"%getfname(filename)
    #f=open(name,'w')
    #f.write(lines)
    #f.close()
    #from_file="driver_%s"%getfname(filename)
    #print from_file
    #__builtin__.__import__(from_file, globals(), locals(), ['driver'])
    #from driver_driver  import driver
    #getfname(replacement[0])
    exec lines
    return driver

try:
    loaded_rollbackImporter["\\\\"]=None
except:
    loaded_rollbackImporter={}


def do_annotations(infile,contents,driver,DB=None,error=False):
    #hash_contents=getHash(contents)
    if DB is None: 
        log.Warning("Cache is disabled!")
    else:
        try:
            log.event( "  loading pypy analysis results from DB...")
            return DB.load(contents)
        except:
            log.Warning("   Cannot load object from DB")
    try:
        ifile=open(infile,'wb')
        ifile.write(contents)
        ifile.close()    
    except Exception, inst:
        log.ERROR("Cannot write to %s. Required for analysis"%infile)
        log.ERROR("  %s."%str(inst))
    if driver in loaded_rollbackImporter:
        loaded_rollbackImporter[driver].uninstall()
    loaded_rollbackImporter[driver] = RollbackImporter()
    driver_func=load_and_wrap(driver)
    t=Translator(driver_func)
    #annmodel.DEBUG=False
    t.simplify()
    if error:
        py.log.setconsumer("annrpython", py.log.STDERR) #
    else:
        py.log.setconsumer("annrpython", None) #
    t.annotate([])
    t.simplify()
    loaded_rollbackImporter[driver].stop()
    #t.view()
    try:
        log.event("  storing in DB...")
        DB.save(t,contents)
    except:
        log.Warning("   Cannot store object in DB")
    return t

def ast_from_code (code,mode="exec",analyze=False):
    res=compiler.parse(code,mode)
    #as=Analyzer()
    #res=as.process(code,mode,False,analyze) 
    ast.ast_make_full(res)
    return res

def ast_from_file(filename):
    as1=Analyzer()
    m=as1.process_file(filename) 
    return m
