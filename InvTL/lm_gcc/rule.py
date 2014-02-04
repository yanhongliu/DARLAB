import re
import sys
import sha
import gc
import pickle
import pprint
import compiler
import string
import inspect
import os
import difflib
from util import *

import py
log = py.log.Producer("InvTS:rule") 
import util
py.log.setconsumer("InvTS:rule event", util.eventlog) #

HL = HugeLog()

class AIDD:
    def __init__ (self,LM,at,iff,de,do):
        #print "AAAAAAAAAAAAAAAAAAAAAA"
        #print do[1]
        self.do_before=LM.SubjectCode("")
        self.do_after=LM.SubjectCode("")
        self.do_instead=LM.SubjectCode("")
        self.at_pat=LM.SubjectCode("")
        self.orig_at=""
        self.orig_if=""
        self.orig_do_before=""
        self.orig_do_after=""
        self.orig_do_instead=""
        self.orig_de_field=""

        if do is not None:
            self.do_before=LM.SubjectCode(do[0])
            self.orig_do_before=do[0]
            try: 
                self.do_after=LM.SubjectCode(do[1])
                self.orig_do_after=do[1]
            except:
                self.do_after=LM.SubjectCode("")
                self.orig_do_after=""
            try: 
                self.do_instead=LM.SubjectCode(do[2])
                self.orig_do_instead=do[2]
            except:
                self.do_instead=LM.SubjectCode("")
        
        
        if at is not None:
            self.at_pat=LM.SubjectCode(at)
            self.orig_at=at
        self.de_class={}
        self.de_field=LM.SubjectCode("")
        if de is not None:
            for C,B in de[0]:
                codec=LM.ConditionalCode(C)
                self.de_class[codec]=set()
                for b in B:
                    self.de_class[codec].add(LM.SubjectCode(b))
            if len(de)>1:
                self.de_field=LM.SubjectCode(de[1])
                self.orig_de_field=(de[1])
        self.if_pat=LM.ConditionalCode(iff)
        self.orig_if=iff
        #print >>Debug(),  at
    def __getstate__(self):
        return self.do_before, self.do_after, self.do_instead, self.de_class, self.de_field, self.at_pat, self.if_pat

    def __setstate__(self, args):
        assert len(args) == 7
        #self.__dict__.update(args[0]) 
        self.do_before=args[0]
        self.do_after=args[1]
        self.do_instead=args[2]
        self.de_class=args[3]
        self.de_field=args[4]
        self.at_pat=args[5]
        self.if_pat=args[6]

class Rule:
    def __init__ (self,LM,var,pat,ai,idd):
        self.LM=LM
        self.vars={}
        self.aidd=set(ai)
        self.idd=idd
        self.pattern=LM.SubjectCode(pat)
        self.var=var
        self.last_postfix=""
        self.last_rep=""
        self.orig_pat=pat
        pass

    def __getstate__(self):
        #print self.__dict__
        return self.__dict__

    def __setstate__(self, args):
        self.__dict__.update(args) 

    def prep_vars(self,def_rep='',postfix=""):
        if def_rep=="":
            def_rep=self.last_rep
        else:
            self.last_rep=def_rep
        if postfix=="":
            postfix=self.last_postfix
        else:
            self.postfix=postfix
        R=set()
        for b in self.aidd:
            R.update(b.do_before.get_vars())
            R.update(b.do_after.get_vars())
            R.update(b.do_instead.get_vars())
            print >>Debug(),  (R)
            R.update(b.at_pat.get_vars())
            R.update(b.if_pat.get_vars())
            R.update(b.de_field.get_vars())
            for K in b.de_class.keys():
                R.update(K.get_vars())
                for body in b.de_class[K]:
                    R.update(body.get_vars())

        for b in [self.idd]:
            R.update(b.do_before.get_vars())
            R.update(b.do_after.get_vars())
            R.update(b.do_instead.get_vars())
            print >>Debug(),  (R)
            R.update(b.at_pat.get_vars())
            R.update(b.if_pat.get_vars())
            R.update(b.de_field.get_vars())
            for K in b.de_class.keys():
                R.update(K.get_vars())
                for body in b.de_class[K]:
                    R.update(body.get_vars())

        R.update(self.pattern.get_vars())    
        #R.update(self.if_pat.get_vars())    
        R.add(self.var)
        R.add("$query")
        R.add("$textquery")
        R.add("$update")
        for r in R:
            self.vars[r]=r.replace('$',def_rep)
            self.vars[r]=self.vars[r]+postfix
        #print >>Debug(),  self.pattern.gen_code(self.vars)
    def get_vars(self):
        if def_rep=="":
            def_rep=self.last_rep
        else:
            self.last_rep=def_rep
        if postfix=="":
            postfix=self.last_postfix
        else:
            self.postfix=postfix
        R=set()
        for b in self.aidd:
            R.update(b.do_before.get_vars())
            R.update(b.do_after.get_vars())
            R.update(b.do_instead.get_vars())
            print >>Debug(),  (R)
            R.update(b.at_pat.get_vars())
            R.update(b.if_pat.get_vars())
            R.update(b.de_field.get_vars())
            for K in b.de_class.keys():
                R.update(K.get_vars())
                for body in b.de_class[K]:
                    R.update(body.get_vars())
        for b in [self.idd]:
            R.update(b.do_before.get_vars())
            R.update(b.do_after.get_vars())
            R.update(b.do_instead.get_vars())
            print >>Debug(),  (R)
            R.update(b.at_pat.get_vars())
            R.update(b.if_pat.get_vars())
            R.update(b.de_field.get_vars())
            for K in b.de_class.keys():
                R.update(K.get_vars())
                for body in b.de_class[K]:
                    R.update(body.get_vars())
        R.update(self.pattern.get_vars())    
        #R.update(self.if_pat.get_vars())    
        R.add(self.var)
        R.add("$query")
        R.add("$textquery")
        R.add("$update")
        return R



def BindVars(LM,AST,vars,debug=False,lexical_way=False):
    for Var in vars.keys():
        if lexical_way :
            param=vars[Var]
            if param:
                param=LM.repr.to_string(vars[Var])
            else:
                param=LM.repr.to_string(LM.repr.bare_from_code(Var))
            ast=LM.repr.get(string.replace(LM.repr.to_string(AST),LM.repr.to_string(LM.repr.bare_from_code(Var)),param))
                
            if (debug): print >>Debug(), (LM.repr.to_string(LM.repr.bare_from_code(Var)))
            if (debug): print >>Debug(), (ast)
            if (debug): print >>Debug(), (AST)
            AST=ast
        else:
            locs=LM.repr.find_locs(LM.repr.bare_from_code(Var),AST,False,vars,False,False)
            if (debug): print >>Debug(), (LM.repr.to_string(LM.repr.bare_from_code(Var)),LM.repr.to_string(vars[Var]))
            if len(locs)>0:
                #ast_compare_result_print(locs)
                for L in locs:
                    #print >>Debug(), (AST)
                    #print >>Debug(),  (L[0])
                    #print >>Debug(),  (L[2])
                    #print >>Debug(),  (vars[Var])
                    LM.repr.replace(LM.repr.get_parent(L),L[0],vars[Var])
    return AST
def CodeToAst(LM,code,lexical_repl,bindings,strip,Lexical):
    cd=code.gen_code(lexical_repl)
    print >>Debug(), (code.gen_code({}))
    print >>Debug(), (cd)
    ast_cd=LM.repr.get(cd)
    #print >>Debug(), (ast_cd)
    ast_bound=BindVars(LM,ast_cd,bindings,False,Lexical)
    #print >>Debug(), (ast_bound)
    if strip:
        ast_cd=LM.repr.get_bare(ast_bound)
    return ast_cd

def CodeToAstWithRepl(LM,code,lexical_repl,bindings,Lexical=False):
    code=code.gen_code({})
    #print >>Debug(), (code)
    res=re.findall(r'(\$[_a-zA-Z][_a-zA-Z0-9]*\{[^}]+\})',code)
    repl={}
    print >>Debug(),  (res)
    local_bindings={}
    local_bindings.update(bindings)
    print >>Debug(), (local_bindings)
    for (k,v) in lexical_repl.items():
        if v not in local_bindings:
            local_bindings[v]=LM.repr.bare_from_code(v)
            #ast_strip(ast_from_code(v))#CodeToAst(LM.ConditionalCode(v),lexical_repl,bindings,True,Lexical)
            #print >>Debug(), (k,v,ast_strip(ast_from_code(v)))
    print >>Debug(), (local_bindings)
    for r in res:

        res=re.match(r'((\$[_a-zA-Z][_a-zA-Z0-9]*)(\{[^}]+\}))',r)
        var=res.group(2)
        v_dict=res.group(3)
        print >>Debug(),  (var,v_dict)
        lhs=CodeToAst(LM,LM.SubjectCode(var),lexical_repl,local_bindings,True,False)
        print >>Debug(),  (lhs)
        print >>Debug(),  (LM.SubjectCode(v_dict,False).gen_code(lexical_repl))
        print LM.SubjectCode(v_dict,False).gen_code(lexical_repl)
        rhs_dict=LM.EvalMetaExpression(LM.ConditionalCode(v_dict,False).gen_code(lexical_repl),local_bindings)
        ast_res=LM.repr.get_bare(LM.repr.replace_all(lhs,rhs_dict))
        repl[r]=(ast_res,var)
    for k in repl.keys():
        var_add=""#str(abs(hash(repl[k])))
        code=code.replace(k,lexical_repl[repl[k][1]]+var_add)
        local_bindings[lexical_repl[repl[k][1]]+var_add]=repl[k][0]
    #print >>Debug(), (code)
    return CodeToAst(LM,LM.SubjectCode(code),lexical_repl,local_bindings,True,Lexical)

def ApplyAIDD(LM,A,vars,AST,rule,anngraph):
    #locate, confirm, apply de transforms, replace by do
    #ast_strip(ast_from_code(A.at_pat.gen_code(rule.vars)))
    #at_ast=BindVars(at_ast,vars)
    at_ast=CodeToAstWithRepl(LM,A.at_pat,rule.vars,vars,True)
    #print "ZZZZZZZZZZZZZZZZZZZZZ"
    #print at_ast
    #print(A.at_pat.gen_code(),'=>',`LM.repr.to_string(at_ast)`)
    locs=LM.repr.find_locs(at_ast,AST,True,vars,False,False)
    #print(vars)
    #ast_compare_result_print(locs)
    #print len(locs)
    for L in locs:
        bvars={}
        bvars.update(vars)
        bvars.update(L[1])
        hold=True
        if len(A.if_pat.gen_code(rule.vars))>0:
            bvars[rule.vars["$update"]]=L[0]  #update the $update metavar
            hold=LM.EvalMetaExpression(A.if_pat.gen_code(rule.vars),bvars) #does the rule if condition hold?
            #print >>Debug(),  ifcode

            #print >>Debug(),  hold
#            if_ast=ast_strip(ast_from_code(if_code))
        if hold:
            #do_ast=CodeToAstWithRepl(A.do_after,rule.vars,bvars)
            #ast_replace(L[2],L[0],do_ast)
            log.event("De,Do Before, Do After")
            #print "ZZZZZZZZZZZZSDDDDDDDDDDDDD"
            #print A.at_pat.gen_code(rule.vars)
            #print >>Debug(),  (do_ast)
            #@Todo need to do DE
            for (k,v) in A.de_class.items():
                #@todo: Unclean LM separation. Fix this.
                class_ast= LM.EvalMetaExpression(("ast_of_type(%s,compiler.ast.Class)"%k.gen_code(rule.vars)),bvars)
                print "ZZZZZZZZZZZZ"
                print class_ast
                if class_ast==None: continue
                for i in v:
                    code_v=(CodeToAst(i,rule.vars,bvars,True,False))
                    #print (code_v)
                    if isinstance(code_v,compiler.ast.Function):
                        #print "TRUE"
                        if (isinstance(class_ast.code,compiler.ast.Stmt)):
                            ast_prepend(class_ast.code.nodes[0],code_v)
                    else:
                        funs=(ast_find_function(class_ast,"__init__"))
                        if (len(funs)>0):
                            fun=funs[0]
                            if (isinstance(fun.code,compiler.ast.Stmt)):
                                ast_postpend(fun.code.nodes[-1],code_v)
                    #print >>Debug(),  (res)
            #print A.do_instead.gen_code()
            if A.do_before.code!="":
                do_before=CodeToAstWithRepl(LM,A.do_before,rule.vars,bvars,True)
                print >>Debug(), ("1")
                LM.repr.prepend(L[0],do_before)
            if A.do_after.code!="":
                do_after=CodeToAstWithRepl(LM,A.do_after,rule.vars,bvars,True)
                print >>Debug(), ("2")
                print >>Debug(), (L[0])
                print >>Debug(), (do_after)
                LM.repr.postpend(L[0],do_after)
            #print A.__dict__
            if A.do_instead.code!="":
                do_instead=CodeToAstWithRepl(LM,A.do_instead,rule.vars,bvars,True)
                #print do_instead
                #print("3")
                LM.repr.replace(LM.repr.get_parent(L),L[0],do_instead)

            #bvars[rule.vars["$update"]]=do_ast   #update the $update metavar
            
        pass
    pass

def ApplyIDD(LM,loc,A,vars,AST,rule):
    #locate, confirm, apply de transforms, replace by do
    #ast_strip(ast_from_code(A.at_pat.gen_code(rule.vars)))
    #at_ast=BindVars(at_ast,vars)
    #at_ast=CodeToAstWithRepl(LM,A.at_pat,rule.vars,vars,True)
    #print "ZZZZZZZZZZZZZZZZZZZZZ"
    #print at_ast
    #print(A.at_pat.gen_code(),'=>',`LM.repr.to_string(at_ast)`)
    #locs=LM.repr.find_locs(at_ast,AST,True,vars,False,False)
    #print(vars)
    #ast_compare_result_print(locs)
    #print len(locs)
    for L in [loc]:
        bvars={}
        bvars.update(vars)
        bvars.update(L[1])
        hold=True
        if hold:
            #do_ast=CodeToAstWithRepl(A.do_after,rule.vars,bvars)
            #ast_replace(L[2],L[0],do_ast)
            log.event("De,Do Before, Do After")
            #print "ZZZZZZZZZZZZSDDDDDDDDDDDDD"
            #print >>Debug(),  (do_ast)
            #@Todo need to do DE

            for (k,v) in A.de_class.items():
                #@todo: Unclean LM separation. Fix this.
                class_ast= LM.EvalMetaExpression(("ast_of_type(%s,compiler.ast.Class)"%k.gen_code(rule.vars)),bvars)
                #print "ZZZZZZZZZZZZ"
                #print class_ast
                #print ("ast_of_type2(%s,compiler.ast.Class)"%k.gen_code(rule.vars))
                
                if class_ast==None: continue
                for i in v:
                    code_v=(CodeToAst(LM,i,rule.vars,bvars,True,False))
                    #print (code_v)
                    if isinstance(code_v,compiler.ast.Function):
                        #print "TRUE"
                        if (isinstance(class_ast.code,compiler.ast.Stmt)):
                            LM.repr.prepend(class_ast.code.nodes[0],code_v)
                    else:
                        funs=(LM.repr.find_function(class_ast,"__init__"))
                        if (len(funs)>0):
                            fun=funs[0]
                            if (isinstance(fun.code,compiler.ast.Stmt)):
                                LM.repr.postpend(fun.code.nodes[-1],code_v)
                    #print >>Debug(),  (res)
            #print A.do_instead.gen_code()
            if A.do_before.code!="":
                do_before=CodeToAstWithRepl(LM,A.do_before,rule.vars,bvars,True)
                print >>Debug(), ("1")
                LM.repr.prepend(L[0],do_before)
            if A.do_after.code!="":
                do_after=CodeToAstWithRepl(LM,A.do_after,rule.vars,bvars,True)
                print >>Debug(), ("2")
                print >>Debug(), (L[0])
                print >>Debug(), (do_after)
                LM.repr.postpend(L[0],do_after)
            #print A.__dict__
            if A.do_instead.code!="":
                do_instead=CodeToAstWithRepl(LM,A.do_instead,rule.vars,bvars,True)
                #print do_instead
                print >>Debug(), ("3")
                LM.repr.replace(LM.repr.get_parent(L),L[0],do_instead)

            #bvars[rule.vars["$update"]]=do_ast   #update the $update metavar
            
        pass
    pass

def ApplyOneRule(LM,rule,AST,L,i,anngraph):
    #L is the locus to update the rule
    pass

    #create the cached variable AST
    var=LM.repr.get_bare(LM.repr.get(LM.SubjectCode(rule.var).gen_code(rule.vars)))

    #replace the invariant by the cached copy

    L[1][rule.vars["$query"]]=var #Rebind the $query variable
    L[1][rule.vars[rule.var]]=var

    #print >>Debug(),  ast2string(AST)
    pre=LM.repr.to_string(AST)
    ApplyIDD(LM,L,rule.idd,L[1],AST,rule)
    if (rule.idd.do_instead.code!=""):
        LM.repr.replace(LM.repr.get_parent(L),L[0],var)
    HL.last().apps.append( (rule.idd, pre,LM.repr.to_string(AST)) )

    pre=LM.repr.to_string(AST)
    for A in rule.aidd: #Apply all aidd tuples to locus
        preAIDD=LM.repr.to_string(AST)
        ApplyAIDD(LM,A,L[1],AST,rule,anngraph)
        HL.last().apps.append( (A, preAIDD,LM.repr.to_string(AST)) )

    HL.last().apps.append( (rule.idd, pre,LM.repr.to_string(AST)) )
    #
    #
    #r1,r2=get_blocks_diff(str_begin,str_end)
    #for i in r2:
    #    if hasattr(i,'added'):
    #        print "@@@@@@"
    #        print '\n'.join(i)
    #assert False
    
    #print >>Debug(),  var
    #print >>Debug(),  rule.vars

def ApplyRule(LM,rule,AST,rid="",DB=None,(infile,driverfile)=(None,None),search_ast=None):
    global HL
    if DB is None: log.Warning("Cache is disabled!")
    if search_ast is None:
        search_ast=AST
    #Locate the rule pattern
    origASTHash=getHash(LM.repr.to_string(AST))
    origRuleHash=getHash(pickle.dumps(rule))
    anngraph=None
    log.event ("Processing rule:")
    log.event ("%s"%    rule.pattern.gen_code())
    log.event( "  inv_hash = %s"%origRuleHash)
    log.event( "  arg_hash = %s"%origASTHash)
    log.event( "  id = %s"%rid)
    #log.status ("Trying rule: %s"%rule.pattern.gen_code())
    LM.repr.prepare(AST)
    try:
        res= DB.load(origRuleHash,origASTHash,rid),True
        #print "!!!!!!!!!1"
        #print HL    
        #print "@@@@@@@@@2"
        #HL=DB.load("HL",origRuleHash,origASTHash,rid)
        #print "@@@@@@@@@3"
        #print HL
        #print "@@@@@@@@@4"
        return res
    except:
        pass
    goon=True
    i=0
    ol=0
    log.event("    failed loading from cache.")
    log.event("  applying rule...")
    applied=False
    while goon:
        i+=1
        rule.prep_vars('','_%s_%d__EXPR__'%(rid,i))
        if rule.var=="$refactor":
            lst=[AST,{rule.vars["$query"]:AST},None]
            for A in rule.aidd: #Apply all aidd tuples to locus
                ApplyAIDD(LM,A,lst[1],AST,rule,None)
            goon=False
        else:
            old_graph=anngraph
            try:
                anngraph=LM.annotate(infile,LM.repr.to_string(AST),driverfile,DB)
            except:
                #If we cannot apply analysis right now, lets reuse old one
                log.event("  Could not annotate at rule %d"%(i-1))
                anngraph=old_graph

            pat_code=rule.pattern.gen_code(rule.vars)
            pat_ast=LM.repr.get_bare(LM.repr.get(pat_code))
            if_code=rule.idd.if_pat.gen_code(rule.vars)
    
            locs=LM.repr.find_locs(pat_ast,search_ast,True,{},False,False,anngraph)
            ln=len(locs)
            #print "ZZZZZZZZZZZZZZZZZZZZ"
            #print len(locs)
            #print if_code
    
            if ol==ln:
                goon=False
                break
            ol=ln
    
            canapply=False
            for L in locs:
                #try to apply the update to the found location
                L[1][rule.vars["$query"]]=L[0] #Bind the $query variable
                L[1][rule.vars["$textquery"]]=L[0] #Bind the $query variable
                #print (pat_code)
                #print (if_code)
                print(LM.repr.to_string(L[0]))
                if_condition_holds = LM.EvalMetaExpression(if_code,L[1])
                #print "AAAAAAAAAAAAA"
                #print hold
                if if_condition_holds:
                    print >>Debug(), (LM.repr.to_string(L[0]))
                    dumpVars (LM,L[1])
                    #print >>Debug(), (L[1])
                    #print >>Debug(), (ast2string(pat_ast))

                    #Condition was valid, applying rule
                    #Do rule application
                    #ast_compare_result_print(locs)
                    HL.new()
                    HL.last().rule=rule
                    HL.last().pre=LM.repr.to_string(AST)
                    ApplyOneRule(LM,rule,AST,L,i,anngraph)
                    HL.last().post=LM.repr.to_string(AST)
                    applied=True
                    #goon=False #Should be gone for multiple rules to apply
                    canapply=canapply or True
                    goon=False
                    break
            goon=canapply
    log.event("    applied.")
    try :
        log.event("  storing in DB...")
        DB.save(AST,origRuleHash,origASTHash,rid)
        #if applied: DB.save(HL,"HL",origRuleHash,origASTHash,rid)
    except:
        pass
    return AST,applied


def GetLocs(LM,rule,AST,rid="",DB=None,(infile,driverfile)=(None,None)):
    if DB is None: log.Warning("Cache is disabled!")

    #Locate the rule pattern
    origASTHash=getHash(LM.repr.to_string(AST))
    origRuleHash=getHash(pickle.dumps(rule))
    log.event ("Processing rule:")
    log.event ("%s"%    rule.pattern.gen_code())
    log.event( "  inv_hash = %s"%origRuleHash)
    log.event( "  arg_hash = %s"%origASTHash)
    log.event( "  id = %s"%rid)
    log.status ("Finding matches for : %s"%rule.pattern.gen_code())
    LM.repr.prepare(AST)
    try:
        return DB.load(origRuleHash,origASTHash,rid)
    except:
        pass

    listlocs=[]

    log.event("    failed loading from cache.")
    log.event("  applying rule...")
    rule.prep_vars('','_%s_%d__EXPR__'%(rid,0))
    if rule.var=="$refactor":
        pass
    else:
        pat_code=rule.pattern.gen_code(rule.vars)
        pat_ast=LM.repr.get_bare(LM.repr.get(pat_code))
        if_code=rule.idd.if_pat.gen_code(rule.vars)

        locs=LM.repr.find_locs(pat_ast,AST,True,{},False,False)

        canapply=False
        #print "ZZZZZZZZZZZZZZZZZZZZ"
        #print len(locs)
        for L in locs:
            #try to apply the update to the found location
            L[1][rule.vars["$query"]]=L[0] #Bind the $query variable
            L[1][rule.vars["$textquery"]]=L[0] #Bind the $query variable
            hold = LM.EvalMetaExpression(if_code,L[1])
            if hold:
                listlocs.append(LM.repr.get_parent(L))
    log.event("    applied.")
    try :
        log.event("  storing in DB...")
        DB.save(listlocs,origRuleHash,origASTHash,rid)
    except:
        pass
    return listlocs    


def dumpVars (LM,vars):
    for (k,v) in vars.items():
        print >>Debug(), ("%s -> %s"%(k,LM.repr.to_string(v)))

