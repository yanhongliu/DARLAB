#import needed python modules
from path import path as Path
import pdb
import __builtin__
import traceback
import pickleshare
import pprint
import lm_py.py as py
import re
import rule
import ruleparser
import sys,os
import traceback 
import util 

log = None

def init_main(argv):
    global log
    log = py.log.Producer("InvTS:main") 
    #import util
    #py.log.setconsumer("InvTS:main event", util.eventlog) #

    #define local functions for path manipulations, etc...

    if len(argv)<2 or argv[1]=='--help':
        print r"""
    InvTS (c) Michael Gorbovitski 2005-2010
    The Invariant-Driven Transformation System
    Standard Usage:
      python InvTS.py [OPTIONS] Language_Module rules_db rules input driverfile output
      Transforms input into output using all rules in rules.invtl.
      This has the sideeffect of creating or updating the database in 
      rulefile.invtl.invts_db, the cache for InvTS.

      OPTIONS:
          --clean    Forces a flush of the cache DB, as well as wiping the output.
          --verbose  Output more information during the transformation.
          --force    Forces output to appear even if it does not pass testing.
          --view     Visualizes the transformation. Activates --clean.
      For an example, see rule.invtl in sample/rbac/
      To run the example, run:
      python InvTS.py lm_py sample/rbac/rule\_db.invt  sample/rbac/rule.invtl 
        sample/rbac/RBAC.py sample/rbac/driver.py sample/rbac/RBACOPT.py

    Custom Usage:
      python InvTS.py --view-CFG Language_Module input driverfile
      This analyzes input, and displays an interactive graph with the results.
    """
        sys.exit()
    class Flags:
        pass
    flags=Flags()
    flags.offset=1
    flags.clean=False
    flags.verbose=False
    flags.force=False
    flags.check_only=False
    flags.view=False
    while argv[flags.offset][:2]=="--":
        flag=argv[flags.offset]
        if flag=="--clean":
            flags.clean=True
        if flag=="--clean":
            flags.clean=True
        if flag=="--verbose":
            flags.verbose=True
        if flag=="--force":
            flags.force=True
        if flag=="--view":
            flags.view=True
            flags.clean=True
        if flag=="--view-CFG":
            flags.check_only=True
        flags.offset+=1
    lm=argv[flags.offset+0]

    i=2
    if not flags.check_only:
        ruledb=argv[flags.offset+1]
        i=0
    if len(argv)>flags.offset+6:
        object=argv[-1]
    else:
        object=None
    res=init_invts(lm,ruledb,flags,object)
    return res

def main(argv):
    res = init_main(argv+[None])
    res = do_rules(*res)
    print res

def init_invts(lm,ruledb,flags,lm_object):
    """Processes the ruleset. Return values:
        0  :  Ok
        1  :  General Error
        2  :  Could not initialize Language Module 
    """
    global log
    log.Warning("lm_object: %s"%lm_object)
    try:
        langmodule=__builtin__.__import__(lm.split(":")[0],None,None,['LanguageModule'])
    except Exception, inst:
        log.ERROR("Cannot load Language Module: %s"%lm.split(":")[0])
        log.ERROR(str(inst))
        return 2
    LM=langmodule.LanguageModule(lm.split(":")[1:]+[lm_object])
    if LM is None:
        log.ERROR("Cannot initialize Language Module: %s with parameters: %s"%(lm,lm.split(":")[1:]))
        return 2;
    if flags.verbose:
        log.event("Switching verbose mode on")
        util.printer=LM.verbose_logger
        LM.set_log_output(util.printer)
    db=None
    rules=ruleparser.ParseFile(ruledb,LM,db)
    #if len(argv)>5:
    #    rules=[rules[int(argv[5])]]
    return (db,LM,flags,rules,lm_object)
#    except Exception, inst:
#        raise inst
    
 
def transform(LM,code,newrule,bindings):
    AST=LM.repr.get(code)
    #pdb.set_trace()
    rule.ApplyRule(LM,newrule,AST,refactor=True,overrideBind=bindings)
    return AST
def invert(s):
    res=re.sub(r'([_a-zA-Z][_a-zA-Z0-9]*)__\d__EXPR__',r'$\1',s)
    return res
def do2rules(db,LM,R1,R2,flags,lm_object):
    RES=""
    R1.prep_vars('','_%s_%d__EXPR__'%("",0))
    
    RES+= "inv py{%s} = py{%s}\n"%(invert(R1.var.gen_code(R1.vars)),invert(R1.pattern.gen_code(R1.vars)))
    if R1.idd.orig_if:
        RES+= "if (%s)\n"%R1.idd.orig_if
    if R1.idd.orig_do_before:            
        AST=transform(LM,R1.idd.do_before.gen_code(R1.vars),R2,R1.vars)
        RES+= "do before py{\n"
        RES+= invert(LM.repr.to_string(AST))
        RES+= "}\n"

    if R1.idd.orig_do_instead:            
        AST=transform(LM,R1.idd.do_instead.gen_code(R1.vars),R2,R1.vars)
        RES+= "do instead py{\n"
        RES+= invert(LM.repr.to_string(AST))
        RES+= "}\n"

    if R1.idd.orig_do_instead:            
        AST=transform(LM,R1.idd.do_after.gen_code(R1.vars),R2,R1.vars)
        RES+= "do instead py{\n"
        RES+= invert(LM.repr.to_string(AST))
        RES+= "}\n"
    if R1.idd.orig_de:
        for D in R1.idd.orig_de:
            if D['code']:
                RES+="de "
                if D['once']:         RES+=" once "
                if D['at']:         RES+=" at "
                if D['in']:         RES+=" in "
                if D['beginning']:         RES+=" beginning "
                if D['end']:         RES+=" end "
                if D['location']:         RES+=" (%s) "%D['location']
                RES+="py%s\n"%D['code']
    if R2.idd.orig_de:
        for D in R2.idd.orig_de:
            if D['code']:
                RES+="de "
                if D['once']:         RES+=" once "
                if D['at']:         RES+=" at "
                if D['in']:         RES+=" in "
                if D['beginning']:         RES+=" beginning "
                if D['end']:         RES+=" end "
                if D['location']:         RES+=" (%s) "%D['location']
                RES+="py%s\n"%D['code']
    for AIDD in R1.aidd:
        RES+= "at py%s\n"%AIDD.orig_at
        if AIDD.orig_if:
            RES+= "if (%s)\n"%AIDD.orig_if
        if AIDD.orig_de:
            for D in AIDD.orig_de:
                if D['code']:
                    RES+="de "
                    if D['once']:         RES+=" once "
                    if D['at']:         RES+=" at "
                    if D['in']:         RES+=" in "
                    if D['beginning']:         RES+=" beginning "
                    if D['end']:         RES+=" end "
                    if D['location']:         RES+=" (%s) "%D['location']
                    RES+="py%s\n"%D['code']
                   
        if AIDD.orig_do_before:            
            AST=transform(LM,AIDD.do_before.gen_code(R1.vars),R2,R1.vars)
            RES+= "do before py{\n"
            RES+= invert(LM.repr.to_string(AST))
            RES+= "}\n"

        if AIDD.orig_do_instead:            
            AST=transform(LM,AIDD.do_instead.gen_code(R1.vars),R2,R1.vars)
            RES+= "do instead py{\n"
            RES+= invert(LM.repr.to_string(AST))
            RES+= "}\n"

        if AIDD.orig_do_instead:            
            AST=transform(LM,AIDD.do_after.gen_code(R1.vars),R2,R1.vars)
            RES+= "do instead py{\n"
            RES+= invert(LM.repr.to_string(AST))
            RES+= "}\n"
    return RES

def do_rules(db,LM,flags,rules,lm_object):    
    RES=""
    #pdb.set_trace()
    while len(rules)>1:
        R1=rules[0]
        R2=rules[1]
        RES=do2rules(db,LM,R1,R2,flags,lm_object)
        F=open("rules.combined","w")
        F.write(RES)
        F.close()    
        rules2=ruleparser.ParseFile("rules.combined",LM,db)
        if len(rules)>2:
            rules=rules2+rules[2:]
        else:
            F=open("rules.combined.invtl","w")
            F.write(RES)
            F.close()    
            return RES


    #tr=Rule(

    #applied=rule.ComposeRule(LM,rules[XY],repr,"%s_%s"%(str(XY),str(index)),db,(infile,driverfile),l)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
#test2(rulefile,infile,driverfile,outfile)
