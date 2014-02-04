#Set up import environment for local large libs
#import local things
import inspect
import re
import subprocess
import tempfile
from path import path as Path
#import gcc
import os


#define log
def LOG(message):
    if printer==None:
        pass
    else:
        printer(message)

import sys 
import os
import inspect


FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
def dump(src, length=8):
    N=0; result=''
    while src:
       s,src = src[:length],src[length:]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       s = s.translate(FILTER)
       result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
       N+=length
       sys.
    return result

class Debug:
    def __init__(self,stream=sys.stdout):
        self.stream=stream
        self.separator=""
        self.incheck=True
        print >>self
        self.incheck=False
        self.last_separator=True
    def write(self, text,s=None):
         # switch to logging here, or something
         if self.incheck:
             self.separator=text
             return
         if s==None:
             s=inspect.stack()[1]
         if (self.separator in text) and not text==self.separator:
             l = text.split(self.separator)
             for i in range(len(l)):
                 self.write(l[i],s)
                 if i!=len(l)-1:
                     self.write(self.separator,s)
             return
         if (self.last_separator):
             self.stream.write("[#DEBUG] %s:%d @ %s # %s"%(os.path.basename(s[1]),s[2],s[3],text))
         else:
             self.stream.write(text)
         self.last_separator=(text==self.separator)
 


class AST:
    def __init__(self,dct):
        self.dct=dct

class dict2(dict):
    def __init__(self):
        dict.__init__(self)
        self.d={}
    def __setitem__(self,k,v):
        dict.__setitem__(self,k,v)
        self.d[v]=k
    def get_key(self,v):
        return self.d[v]
    def rev_in(self,v):
        return v in self.d

eventlog=LOG
printer=None

GimpleObject=dict2()
CObject=dict2()
from pypy.tool.ansi_print import ansi_log 

##IMPORTANT
#This imports all availible functions that may be called
#from rule_func import *

def call_elsa(string,retry=True):
    string=re.sub(r"$([a-zA-Z]\s*)",r"\1___EXPR_",string)
    (osid,fname)=tempfile.mkstemp(".c")
    (x,tempname)=tempfile.mkstemp(".tmp")
    os.close(osid)
    f=open(fname,'wb')
    f.write(string)
    f.close()
    retstring=""
    #ccparse -tr c_lang,printAST,stopAfterParse a.c 
    f=open(tempname,'wb')
    print gcc
    print "Alpha",gcc,gcc.invts_base + "/lm_gcc/elsa/elsa-2005.08.22b/elsa/ccparse" 
    ret=subprocess.call([gcc.invts_base + "/lm_gcc/elsa/elsa-2005.08.22b/elsa/ccparse","-tr","c_lang,printAST,stopAfterParse",fname],stdout=f,stderr=f)
    f.close()
    #print string
    if ret==0: #Everything ok, C file read and parsed
        f=open(tempname,'r')
        res=f.read()
        f.close
        #print res
        return (res,0)
    else: #Something went wrong. Horribly, horribly wrong. Probably a small pattern
        if retry:
            try:
                res=(call_elsa(string+";",False)[0],1)
            except:
                try:
                    res=(call_elsa("blah="+string+";",False)[0],2)
                except:
                    assert False
            return res
        else:
            assert False

def read_elsa(lines,il=2): #il is indentation-level
    if not lines:
        return {}
    blocks=[]
    bs=None
    current_block=[]
    dct={}
    for i in lines:
        if re.match(r"\s{%d}\w+"%il,i): #Start of new block
            if bs!=None:
                blocks+=[[bs,current_block]]
                bs=i[il:]
                current_block=[]
            else:
                bs=i[il:]
        elif re.match(r"\s{%d}\s+"%il,i): #Continuation of block
            current_block+=[i[il:]]
    if bs!=None:
        blocks+=[[bs,current_block]]
    for b in blocks:
        leader,body=b
        #print leader.replace(" ","_")
        if re.match(r"\w+:$",leader): #Contains a list
            idct={}
            for k,v in read_elsa(body).items():
                idct[re.match(r"\w+\[(\d+)\]",k).group(1)]=v
            dct[leader[:-1]]=idct
            dct[leader[:-1]]["type"]="list"
        elif re.match(r".+=.+:$",leader): #contains subdict
            mo=re.match(r"(.+)=(.+):$",leader)
            dct[mo.group(1).strip()]=read_elsa(body)
            dct[mo.group(1).strip()]["type"]=mo.group(2).strip()
        elif re.match(r".+=.+[^:]$",leader): #Simple node
            mo=re.match(r"(.+)=(.+[^:])$",leader) #Simple node
            dct[mo.group(1).strip()]=mo.group(2).strip()
        elif re.match(r".+\s+is\s+.+$",leader): #Simple node
            mo=re.match(r"(.+)\s+is\s+(.+)$",leader) #Simple node
            dct[mo.group(1).strip()]=mo.group(2).strip()
    return dct

def gen_str(string):
    """Convert string to an AST vial elsa"""
    ast,type=call_elsa(string)
    lines=ast.split("\n")[1:]
    ast=read_elsa(lines)
    #print >>Debug(), type
    if type==0: #Raw string
        pass
    elif type==1: #; appended
        pass
    elif type==2: #blah= <code> ; surrounded
        ast=ast["topForms"]["0"]["decl"]["decllist"]["0"]["init"]
        #print >>Debug(), ast.keys()
        pass
    print >>Debug(), string
    print >>Debug(), ast
    return AST(ast)

def tree_repr(tree, indent):
    global tree_repr
    print (" " * indent) + repr(tree)
    if indent < 20:
        for name,attribute in tree.getattributes().iteritems():
            if isinstance(attribute, gcc.Tree):
                print (" " * (indent + 2)) + repr(name)
                tree_repr(attribute, indent + 4)
            else:
                print (" " * (indent + 2)) + repr(name) + "=" + repr(attribute)
        for operand in tree.getoperands():
            tree_repr(operand, indent + 2) 


class Repr:
    """This class wraps the representation of the subject language"""
    def parse_file(self, infile):
        if infile=="NONE":
            return ""
        else:
            f=open(infile,'r')
            s=f.read()
            f.close()
            return s
    def get(self,string):
        if string in GimpleObject:
            return GimpleObject[string]
        if string in CObject:
            return CObject[string]
        #generate C Object here, as that's obviosly what's required at this point.
        res=gen_str(string)
        CObject[string]=res
        return self.get(string)

    def get_basic(self,repr):
        return self.get(self.to_string(repr))
    def prepare(self,repr):
        return repr
    def get_bare(self,repr):
        return repr
    def bare_from_code(self,code):
        return self.get_bare(self.get(code))
    def to_string(self,repr):
        if GimpleObject.rev_in(repr) and isinstance(repr, gcc.GIMPLE):
            return GimpleObject.get_key(repr)
        if CObject.rev_in(repr):
            return CObject.get_key(repr)
        return repr #None is invalid
    def annotate(self,infile,contents,driver,DB=None,error=False):
        return None 
    def find_locs(self,pattern,ast,pat,bound_vars,comp_ignore,debug,anntree=None):
        """ Tries to match ast2 to ast1, at all subnodes of ast2.
        Basically, re.search(ast1,ast2)
        pat is whether to match patterns
        """
        #Do not forget to dump these into GimpleObject map
        #for block in gcc.getblocks():
        #    print repr(block)
        #    for statement in block.getstatements():
        #        tree_repr(statement.gettree(), 2) 
         
        if isinstance(ast, gcc.GIMPLE):
            print >>Debug(), "Calling find_locs_constrained(%s,%s,%s)"%(pattern,ast,bound_vars)
            res=[]#gcc.find_locs_constrained(pattern,ast,bound_vars)
            print >>Debug(), "Returned from find_locs_constrained"
            print >>Debug(), "Returned %s"%res
        else:
            print >>Debug(), "Calling find_locs(%s,%s)"%(pattern,ast)
            res=[]#gcc.find_locs(pattern,bound_vars)
            print >>Debug(), "Returned from find_locs"
            print >>Debug(), "Returned %s"%res
        return res #Never returns None
    def get_parent(self,loc):
        return loc[2]
    def replace(self,parent,source,target):
        return None
    def replace_all(self,repr,dct):
        return None
    def prepend(self,src,repr):    
        return None
    def postpend(self,src,repr):    
        return None
    def find_function(self,src,name):
        return None

class LanguageModule:
    def __init__(self,params):
        global gcc
        self.ConditionalCode=ConditionalCode
        self.SubjectCode=Code
        self.LanguageID="C"     
        self.LanguageName="gcc"
        self.repr=Repr()
        self.verbose_logger=ansi_log
        #self.funcs=rule_func
        print "Gcc: %s"%params[-1]
        if params:
            gcc=params[-1]
        else:
            import gcc as gc2
            gcc=gc2
    def save(self,name,data):
        return None
    def load(self,name):
        return None
    def set_log_output(self,logger):
        global printer
        printer=logger

    def check_program(self,infile,contents,driver,DB=None,debug=False):
        return None

    def EvalMetaExpression(self,code,bindings):
        """ Evaluates the code, with variable bindings in the dict bindings"""
        _code=""
        for Var in bindings.keys():
            _code+=("%s=param['%s']\n"%(Var,Var))
        _code=(_code+"ret="+code+"\n\n")
        ret=None    
        try:
            #print _code
            #print bindings.keys()
            #print "ret"
            ret= eval_query(_code,bindings,"ret") 
        except NameError , inst:
            dprint (inst)
            ret=None
        except Exception, inst:
            dprint ("A\n")
            dprint(_code)
            dprint(bindings)
            raise Exception, inst
        return ret
  
class ConditionalCode:
    def __init__(self, code,strip=True):
        if code is None:
            self.code=""
            return
        if strip and code.startswith('{') and code.endswith('}'):
            lines = code[1:-1].splitlines() 
        else:
            lines = code.splitlines()
        while lines and blank_line_re.match(lines[0]): lines.pop(0)
        while lines and blank_line_re.match(lines[-1]): lines.pop(-1)
        if lines:
            
            #res=[]
            indents = [len(indent_re.match(line).group(0)) for line in lines]
            indent = indents[0]
            if min(indents) >= indent:
                lines = [line[indent:] for line in lines]

            lines=[line.rstrip() for line in lines]
            if False:
                ls=[]
                if (len(lines)>1):
                    indents = [len(indent_re.match(line).group(0)) for line in lines[1:]]
                    mi=min(indents)
                    if lines[0].rstrip()[-1]==':' and mi!=0:
                        mi-=1
                    ls=[line[mi:] for line in lines[1:]]
                lines=[lines[0].lstrip()]+ls
        self.code = "".join([line+'\n' for line in lines])
        #dprint( lines)
        #dprint( self.code)
    def __getstate__(self):
        return self.code

    def __setstate__(self, args):
        self.code=args
    def empty(self):
        return False
    def gen_code(self, dict={},dict2={},indent=None, counters=None, pos=None):
        if indent is None:
            ret=self.code.strip()
        else:
            ret= "\n".join([indent+line for line in self.code.splitlines()])
        #lst.reverse()
        #dprint([K for K,V in lst])
        #dprint([K for K,V in lst])
        for K,V in sorted([(K,V) for K,V in dict.items()],order_substring_tuple):
            #dprint K,V
            ret=ret.replace(K,V)
        for K,V in sorted([(K,V) for K,V in dict2.items()],order_substring_tuple):
            #dprint K,V
            ret=ret.replace(K,V)
        return ret
    def get_vars (self):
        return set(re.findall(r'\$[a-zA-Z]\w*',self.code))    
        
class Code:
    def __init__(self, code):
        self.name="mine"
        if code.startswith('{') and code.endswith('}'):
            self.code = code[1:-1]    
        else:
            self.code = code
    def __getstate__(self):
        return self.code
    def __setstate__(self, args):
        self.code=args
    def empty(self):
        return False
    def gen_code(self, dict={},dict2={},indent=None, counters=None, pos=None):
        ret=self.code
        for K,V in sorted([(K,V) for K,V in dict.items()],order_substring_tuple):
            ret=ret.replace(K,V)
        for K,V in sorted([(K,V) for K,V in dict2.items()],order_substring_tuple):
            ret=ret.replace(K,V)
        return ret
    def get_vars (self):
        return set(re.findall(r'\$[a-zA-Z]\w*',self.code))    

blank_line_re = re.compile("^\s*$")
indent_re = re.compile("^\s*")

def eval_query (code,param,retarg="ret"):
    #dprint code
    #dprint(code)
    exec(load_suite(code)["code"])
    return eval(retarg)

def order_substring_tuple(s1,s2):
    import string
    if string.find(s1[0],s2[0])!=-1: #s2 elem s1, s1>s2
        return -1
    if string.find(s2[0],s1[0])!=-1: #s2 elem s1, s1>s2
        return +1
    return 0

def dprint (*args):
    test=not not False
    if test:
        s=inspect.stack()[1]
        #for k,v in s[0].__dict__.items():
        #    print k , ": ",v
        #print (inspect.getargvalues(s[0]))
        iprint(("#","%s:%d"%(os.path.basename(s[1]),s[2]),"@",s[3]," : ")+args)

def iprint(args):
    import sys
    for i in args:
        sys.stdout.write( str(i)+" ")
    sys.stdout.write('\n')


