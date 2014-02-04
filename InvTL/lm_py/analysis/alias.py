import os.path
import sys
import inspect
import pdb
from StringIO import StringIO
import pyunparse
import compiler
from collections import defaultdict

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
             s=inspect.stack()[2]
         if (self.separator in text) and not text==self.separator:
             l = text.split(self.separator)
             for i in range(len(l)):
                 self.write(l[i],s)
                 if i!=len(l)-1:
                     self.write(self.separator,s)
             return
         if (self.last_separator):
             self.stream.write("# %s:%d @ %s # %s"%(os.path.basename(s[1]),s[2],s[3],text))
         else:
             self.stream.write(text)
         self.last_separator=(text==self.separator)

def ast2string(ast):
    file=StringIO()
    pyunparse.ast2py(ast,file)
    return file.getvalue()

def truncate(s):
   s=s.replace("\n","  ")
   s=s.replace("\r","  ")
   if len(s)<50:
      return s
   return "%s ... %d ... %s"%(s[:20],len(s),s[-20:])


class Graph:
  def __init__(self):
    self.F={}
    self.B={}
    self.crossTransitions=set()
    self.start=None
    self.nodes=set()
    self.revuid={}
  def addedge(self,f,t):
    if not self.F:
      self.start=f
    if f not in self.F:
      self.F[f]=set()
    self.F[f].add(t)
    if t not in self.B:
      self.B[t]=set()
    self.B[t].add(f)
    self.nodes.add(f)
    self.nodes.add(t)
  def visitEdges(self,visitor):
      for f,S in self.F.iteritems():
        for t in S:
          visitor(f,t)

  def visitNodes(self,visitor):
      for n in self.nodes:
        visitor(n)
  def dfs(self,action,start=None,stopcondition=lambda f: False,pre=False):
    visited=set()
    if start==None:
      start=self.start
    
    def idfs(cp,visitedset):
      if cp in visitedset:
        return
      visitedset.add(cp)
      if pre:
        action(cp)
      if not stopcondition(cp):
        if cp in self.F:
          for c in self.F[cp]:
            idfs(c,visitedset)
      if not pre:
        action(cp)
    
    idfs(start,visited)

  def revdfs(self,action,start=None,stopcondition=lambda f: False,pre=True):
    visited=set()
    if start==None:
      start=self.start
    
    def idfs(cp,visitedset):
      if cp in visitedset:
        return
      visitedset.add(cp)
      if pre:
        action(cp)
      if not stopcondition(cp):
        if cp in self.B:
          for c in self.B[cp]:
            idfs(c,visitedset)
      if not pre:
        action(cp)
    
    idfs(start,visited)

class visitCreator:
    def __init__(self):
        self.graph=Graph()
        self.max=0
        self.count=0

    def visitFunc(self):
        def visit(f,t):
            #visited CFG node t coming from f
            #pdb.set_trace()

            #pdb.set_trace()
            noadd=False
            if hasattr(t,"_parent") and isinstance(t._parent,compiler.ast.Function):
              #pdb.set_trace()
              z=f
              while (True):
                if hasattr(t,"getChildren") and t.getChildren() and t.getChildren()[-1]==z:
                  noadd=True
                  break
                if hasattr(z,"_parent"):
                  z=z._parent
                else:
                  break
            if not noadd:
              self.count+=1
              if f._uid>self.max:
                  self.max=f._uid
              if (self.count%1000 == 1):
                  if hasattr(f,"lineno"):
                      print self.count, f._uid, self.max, f.lineno
                  else:
                      print self.count, f._uid, self.max
              self.graph.addedge(f,t)
        return visit

def dispatch(namespace,*args):
    name=args[0].__class__.__name__
    if "handle%s"%name in namespace:
        namespace["handle%s"%name](*args)
    elif "default" in namespace:
        namespace["default"](*args)
    else:
        print >>Debug(), "Unhandled class %s"%name

def findAttr(node,attrname):
    try:
        while not hasattr(node,attrname):
            node=node._parent
        return node.__dict__[attrname]
    except Exception, E:
        #pdb.set_trace()
        return None
def stypes(param):
    res=set()
    for v_a in param._contexts.values():
        for s_v_a in v_a:
            if hasattr(s_v_a,"values"):
                for v in s_v_a.values:
                    res.add("%s< %s >"%(s_v_a._qualified_name,v._qualified_name))
            else:
                res.add(s_v_a._qualified_name)
    return res


def types(param):
    res=set()
    if hasattr(param,"_contexts"):
        for v_a in param._contexts.values():
            for s_v_a in v_a:
                res.add(s_v_a)
    else:
        if param.__class__.__name__=="Subscript":
            if hasattr(param.expr,"_context"):
                return types(param.expr)
        elif param.__class__.__name__=="Slice":
            if hasattr(param.expr,"_context"):
                return types(param.expr)
        else:
            pdb.set_trace()

    return res

def isObject(type,primitives=set("builtins.%s"%i for i in
                            ("boolean","none","int","long","float","string","buffer")
                            )):
    if type in primitives:
        return False
    if hasattr(type,"_qualified_name"):
        if type._qualified_name in primitives:
            return False
    return True

 
class PreTransform:
    def __init__(self,G):
        self.found=False
        self.mustmodify=None
        self.targets=set()
        self.G=G
       
    def addSuccPred(self):            
        def addFB(F,T):
            if not hasattr(F,"_S"):
                F._S=set()
            if not hasattr(F,"_P"):
                F._P=set()
            if not hasattr(T,"_S"):
                T._S=set()
            if not hasattr(T,"_P"):
                T._P=set()
            F._S.add(T)
            T._P.add(F)
        self.G.visitEdges(addFB) #computes SUCC AND PRED      

    def addContainsandUID(self): #Computes self referene, needed for later parameter passing
        self.maxuid=0
        def container(node):
            c=node
            while hasattr(c,"_parent"):
                if (isinstance(c,compiler.ast.Module) or
                    isinstance(c,compiler.ast.Function)):
                    return c
                c=c._parent
            if (isinstance(c,compiler.ast.Module) or isinstance(c,compiler.ast.Function)):
                return c
            return None
        def findmaxUID(node):
            if hasattr(node,"_uid"):
                if self.maxuid<node._uid:
                    self.maxuid=node._uid
        self.G.visitNodes(findmaxUID)
        
        def setmaxUID(node):
            if not hasattr(node,"_uid"):
                self.maxuid+=1
                node._uid=self.maxuid
        self.G.visitNodes(setmaxUID)

        def setContainer(node):
            node._contains=container(node)
            if node._contains and not hasattr(node._contains,"_uid"):
                self.maxuid+=1
                node._contains._uid=self.maxuid
            if node.__class__.__name__=="Name":
                if not hasattr(node,"_qualified_name"):
                    node._qualified_name=node.name
                
        self.G.visitNodes(setContainer)

    def addReturn(self):
        def addRet(F,T):
            #print "FROM: ", truncate(str(F))
            #print "TO: ", truncate(str(T))
            #if F.__class__.__name__=="Getattr":
            #    pdb.set_trace()
            #if "pass" in ast2string(F):
            #    pdb.set_trace()
            if (#not isinstance(F,compiler.ast.Stmt) and 
              not isinstance(F,compiler.ast.Module) and not
              isinstance(F,compiler.ast.Function) and not
              #isinstance(T,compiler.ast.Stmt) and not
              isinstance(T,compiler.ast.Module) and not
              isinstance(T,compiler.ast.Function)):
                cf=F._contains
                ct=T._contains
                #print cf==ct
                if cf and ct and cf!=ct:
                    F._transitions=True
                    self.G.crossTransitions.add( ( F,T) )
                    #print "Adding transition between:"
                    #print F, F._parent
                    #print T
        self.G.visitEdges(addRet)


    def selfsearch(self): #Computes self referene, needed for later parameter passing
        def prepSelfAssign():
            def handleAssign(node):
                if "builtins" in node.filename: return
                if node.nodes:
                    if node.nodes[0].__class__.__name__=="AssName":
                        lhs=node.nodes[0]._qualified_name
                        if lhs in self.targets:
                            if node.expr.__class__.__name__=="Name":
                                self.targets.add(node.expr._qualified_name)
                            elif node.expr.__class__.__name__=="Getattr":
                                selfobj=node.expr.expr
                                if selfobj.__class__.__name__=="Name":
                                    if not hasattr(self.mustmodify,"_self"):
                                        self.mustmodify._self=set()
                                    self.mustmodify._self.add(selfobj)
                                    self.found=True

            def F(node):
                dispatch({"handleAssign":handleAssign,"default":lambda x:x},node)
                
            def handleCallFunc(node):
                if "builtins" in node.filename: return
                try:
                    for T in node._targets:
                        if "self" in T._locals and T.name!="__init__":
                            if node.node.__class__.__name__=="Name":
                                self.targets.add(node.node._qualified_name)
                                self.mustmodify=node
                                self.found=False
                                self.G.revdfs(F,node,lambda x: self.found)
                                #if self.found:
                                #    print ">> HandleCallFunc in selfsearch in FixpointSelfSearch >> Added self!", node, node._self
                                #else:
                                #    print ">> HandleCallFunc in selfsearch in FixpointSelfSearch >> No self found for:", node

                            elif node.node.__class__.__name__=="Getattr":
                                selfobj=node.node.expr
                                if not hasattr(node,"_self"):
                                    node._self=set()
                                if hasattr(selfobj,"_qualified_name"):
                                    node._self.add(selfobj)
                            else:
                                print ">> HandleCallFunc in selfsearch in FixpointSelfSearch >> Unhandled self type", node

                except Exception, E:
                    pdb.set_trace()
                    pass

            Dispatch={"handleCallFunc":handleCallFunc,"default":lambda x:x}
            def mainFunc(node):
                self.G.revuid[node._uid]=node
                dispatch(Dispatch,node)
            return mainFunc

        self.G.visitNodes(prepSelfAssign())
    
    def addParamAndReturns(self): #does parameter and return passing, tuple assignment handling
        def prepParamAndReturn():
                
            def handleCallFunc(node):
                if "builtins" in node.filename: return
                try:
                    for T in node._targets:
                        if not hasattr(node,"_postexec"): node._postexec=[]
                        argmap={}
                        if "self" in T._locals: #Method call
                            if T.name!="__init__":
                                if hasattr(node,"_self"):
                                    for SELF in node._self:
                                        argmap["%s.self"%T._qualified_name]=SELF
                            for i in range(len(node.args)):
                                arg=node.args[i]
                                if arg.__class__.__name__=="Keyword":
                                    argmap["%s.%s"%(T._qualified_name,arg.name)]=arg.expr
                                else:
                                    argmap["%s.%s"%(T._qualified_name,T.argnames[i+1])]=node.args[i]
                            pass
                        else: #Other function call
                            for i in range(len(node.args)):
                                arg=node.args[i]
                                if arg.__class__.__name__=="Keyword":
                                    argmap["%s.%s"%(T._qualified_name,arg.name)]=arg.expr
                                else:
                                    argmap["%s.%s"%(T._qualified_name,T.argnames[i])]=node.args[i]
                            pass
                        for (k,v) in argmap.iteritems():
                            node._postexec.append( (k,v) )
                        #pdb.set_trace()
                except IndexError, e:
                    pass
                except Exception, e:
                    pdb.set_trace()
                    pass

            def handleReturn(node):
                if "builtins" in node.filename: return
                if not hasattr(node,"_postexec"): node._postexec=[]
                rhs=node.value
                scopename=findAttr(node,"_qualified_name")
                if scopename:
                    node._postexec.append( ("%s.__RETVAL__"%scopename,rhs) )
            def handleAssign(node):
                if "builtins" in node.filename: return
                try:
                    if node.nodes:
                        lhs=node.nodes[0]
                        rhs=node.expr
                        if not hasattr(lhs,"_postexec"): lhs._postexec=[]

                        if rhs.__class__.__name__=="CallFunc": #lhs=rhs
                            for T in rhs._targets:
                                if T.name=="__init__":
                                    if not hasattr(rhs,"_postexec"): rhs._postexec=[]
                                    new_rhs=None
                                    if lhs.__class__.__name__=="AssName":
                                        new_rhs=compiler.ast.Name(lhs.name)
                                        new_rhs._qualified_name=lhs._qualified_name
                                    elif lhs.__class__.__name__=="AssAttr":
                                        new_rhs=compiler.ast.Getattr(lhs.expr,lhs.attrname)
                                    elif lhs.__class__.__name__=="Subscript":
                                        new_rhs=compiler.ast.Subscript(lhs.expr,compiler.transformer.OP_APPLY,lhs.subs)
                                    if new_rhs:
                                        new_rhs._contexts=lhs._contexts
                                        new_rhs._parent=rhs._parent
                                        rhs._postexec.append(
                                            ("%s.self"%T._qualified_name, new_rhs) )
                         
                            lhs._callnode=rhs        
                            match=False                            
                            if lhs.__class__.__name__=="AssName":
                                match=True
                                lq=lhs._qualified_name
                            elif lhs.__class__.__name__=="AssAttr":
                                match=True
                                lq="%s#%s"%(lhs.expr._qualified_name,lhs.attrname)
                            elif lhs.__class__.__name__=="Subscript":
                                match=True
                                if len(lhs.subs)==1 and lhs.subs[0].__class__.__name__=="Const":
                                    lq="%s:%s"%(lhs.expr._qualified_name,str(lhs.subs[0].value))
                                else:
                                    lq=lhs.expr._qualified_name
                            if match:
                                for T in rhs._targets:
                                    if T._returns:
                                        basename=compiler.ast.Name('__RETVAL__')
                                        basename._qualified_name="%s.__RETVAL__"%T._qualified_name
                                        lhs._postexec.append( (lq, basename) ) #Take __RETVAL__
 
                        if rhs.__class__.__name__=="Tuple": #a=(x,y,z) -> a.1=x, a.2=y, a.3=z, a=x, a=y, a=z      
                            c=0
                            for e in rhs.nodes:
                                if lhs.__class__.__name__=="AssName":
                                    lhs._postexec.append( ("%s:%d"%(lhs._qualified_name,c),e) )
                                elif lhs.__class__.__name__=="AssAttr":
                                    lhs._postexec.append( ("%s#%s:%d"%(lhs.expr._qualified_name,lhs.attrname,c),e) )
                                elif lhs.__class__.__name__=="Subscript":
                                    lhs._postexec.append(("%s:%d"%(lhs.expr._qualified_name,c),e) )
                                else:
                                    pdb.set_trace()
                                c+=1

                        if lhs.__class__.__name__=="AssTuple": #a,b=c -> a=c.1; b=c.2
                            c=0
                            for lhs_arg in lhs.nodes:
                                if lhs_arg.__class__.__name__=="AssName":
                                    lq=lhs_arg._qualified_name
                                elif lhs_arg.__class__.__name__=="AssAttr":
                                    lq="%s#%s"%(lhs_arg.expr._qualified_name,lhs_arg.attrname)
                                elif lhs_arg.__class__.__name__=="Subscript":
                                    if len(lhs_arg.subs)==1 and lhs_arg.subs[0].__class__.__name__=="Const":
                                        lq="%s:%s"%(lhs_arg.expr._qualified_name,str(lhs_arg.subs[0].value))
                                    else:
                                        lq=lhs_arg.expr._qualified_name
                                #lq is now the left qualified name
                                if rhs.__class__.__name__=="CallFunc": #lhs=rhs
                                    for T in rhs._targets:
                                        if T._returns:
                                            basename=compiler.ast.Name('__RETVAL__')
                                            basename._qualified_name="%s.__RETVAL__"%T._qualified_name
                                            index=compiler.ast.Subscript(basename,compiler.transformer.OP_APPLY,[compiler.ast.Const(c)])
                                            lhs._postexec.append( (lq, index) ) #Take __RETVAL__ indexing
                                else:
                                    index=compiler.ast.Subscript(rhs,compiler.transformer.OP_APPLY,[compiler.ast.Const(c)])
                                    lhs._postexec.append( (lq, index) )
                                        
                                c+=1
                            pass
                            #pbd.set_trace()
                        #else:
                        #    pdb.set_trace()                    
                except Exception, e:
                    pdb.set_trace()
                    pass

            Dispatch={"handleCallFunc":handleCallFunc,"handleAssign":handleAssign,"handleReturn":handleReturn,
                      "default": lambda x: x}
            def mainFunc(node):
                dispatch(Dispatch,node)
            return mainFunc

        self.G.visitNodes(prepParamAndReturn())

def set_tuple(T):
    r=set()
    r.add(T)
    return r

class WorksetStorage:
    def __init__(self):
        self.W=defaultdict(set)
        self.NESet=set()
        self.cache={}
        pass
    def add(self,NID,elem):
        self.W[NID].add(elem)
        self.NESet.add( NID )
        pass
    def getandremoveany(self):
        res=None
        for NID in self.NESet:
            for e in self.W[NID]:
                self.W[NID].remove(e)
                if not self.W[NID]:
                    del self.W[NID]
                    self.NESet.remove(NID)
                res=(NID,e)
                break
            break
        pass
        return res
    def succI(self,NID):
        N,id=NID
        if hasattr(N,"_postexec"):
            if id<len(N._postexec):
                return set_tuple((N,id+1))
            else:
                return set([(n,0) for n in N._S if n!=N])
        else:
            return set([(n,0) for n in N._S if n!=N])
    def succ(self,NID):
        ONID=NID
        if NID in self.cache:
            return self.cache[NID]
        S=self.succI(NID)
        rS=set()
        visited=set()
        while S:        #Skips over undesirable statements             
            NID=S.pop()
            visited.add(NID)
            node,id=NID
            if hasattr(node,"filename") and "builtins" in node.filename:
                S|=(self.succI(NID) - visited)
            if hasattr(node,"_postexec") and id<len(node._postexec):
                rS.add( NID )
            else:
                if node.__class__.__name__=="Assign":
                    rS.add( NID )
                else:
                    S|=(self.succI(NID) - visited)
        self.cache[ONID]=rS
        return rS
         
    def printWorkset(self):
        for (k,v) in self.W.iteritems():
            print "Node : %s, subid:%d"%(truncate(ast2string(k[0])),k[1])
            for e in v:
                print "    ",e

class Storage:
    def __init__(self,Print=False):
        self.N=defaultdict(set)
        self.FSet=defaultdict(dict)
        self.RSet=defaultdict(dict)
        self.Print=Print
        self.E2=defaultdict(set)
        self.count=0 #Number of attempts to add alias pairs
        self.ucount=0  #Number of stored alias pairs
        #self.I=defaultdict(set)
        print "Using storage %s"%self.__class__.__name__

    def incI(self,NodeID,x,y,SUCC):
        added=False
        if self.Print:
            print NodeID[0]._uid,x,y
        self.count+=1
        R=(x,y)
        if R not in self.N[NodeID]:
            self.ucount+=1
            self.N[NodeID].add(R)
            added=True
        #self.I[(NodeID,x[0])].add((x,y))

        if x not in self.FSet[NodeID]:
            self.FSet[NodeID][x]=set()
        if y not in self.FSet[NodeID][x]:
            self.ucount+=1
            self.FSet[NodeID][x].add(y)
        #else:
        #    pdb.set_trace()

        if y not in self.RSet[NodeID]:
            self.RSet[NodeID][y]=set()
        if x not in self.RSet[NodeID][y]:
            self.ucount+=1
            self.RSet[NodeID][y].add(x)
        return added
    def nuke(self,NodeID):
        if NodeID in self.N:
            self.ucount-=len(self.N[NodeID])
            del self.N[NodeID]
        if NodeID in self.FSet:
            self.ucount-=len(self.FSet[NodeID])
            del self.FSet[NodeID]
        if NodeID in self.RSet:
            self.ucount-=len(self.RSet[NodeID])
            del self.RSet[NodeID]
            
    def printStatistics(self):
        print "Items stored in alias graph: %d"%self.ucount
        print "Items added to alias graph:  %d"%self.count
    def incE2(self,NodeID,context, ARG):
        self.E2[(NodeID,context)].add( ARG )
    def getE2(self,NodeID,context):
        self.E2[(NodeID,context)]
    #def getI(self,NodeID,context):
    #    return self.I[(NodeID,context)]
    def decE2(self,NodeID,context,ARG):
        self.E2[(NodeID,context)].remove(ARG)
    
    def dump(self):
        def container(node):
            c=node
            while hasattr(c,"_parent"):
                if (isinstance(c,compiler.ast.Module) or
                    isinstance(c,compiler.ast.Function)):
                    return c
                c=c._parent
            if (isinstance(c,compiler.ast.Module) or isinstance(c,compiler.ast.Function)):
                return c
            return None
        def r():
            return defaultdict(set)
        funcAl={}
        for NodeID,vars in self.FSet.iteritems():
            N=NodeID[0]
            if isinstance(N,tuple):
                N=N[0]
            cf=container(N)
            if cf:
                for var, rhss in vars.iteritems():
                    if cf._qualified_name not in funcAl:
                        funcAl[cf._qualified_name]={}
                    if var[1] not in funcAl[cf._qualified_name]:
                        funcAl[cf._qualified_name][var[1]]=set()
                    funcAl[cf._qualified_name][var[1]]|=rhss
                    if "@" not in funcAl:
                        funcAl["@"]={}
                    if var[1] not in funcAl["@"]:
                        funcAl["@"][var[1]]=set()
                    funcAl["@"][var[1]]|=rhss
                    #self.revStorage(var)[1] is the varName
                    #pdb.set_trace()
            else:
                pdb.set_trace()
        return funcAl


    def contains(self,NodeID,x,y):
        return (x,y) in self.N[NodeID]
    def aliases(self,NodeID,p):
        if p in self.FSet[NodeID]:
            return self.FSet[NodeID][p]
        else:
            return set()
    def rev_aliases(self,NodeID,q):
        if q in self.RSet[NodeID]:
            return self.RSet[NodeID][q]
        else:
            return set()

    def inP(self,NodeID,p):
        return p in self.FSet[NodeID]
    def printStatus(self):
        print self.ucount,len(self.N)
        pass
    def printAliasSet(self,filename,varname):
        for nid in self.FSet.keys():
            if isinstance(nid[0],tuple):
                N=nid[0][0]
            else:
                N=nid[0]
            if hasattr(N,"filename") and filename in N.filename:
                if ((),varname) in self.FSet[nid]:
                    print self.FSet[nid][((),varname)], N._uid, truncate(ast2string(N)) 
                    print "  ", ",".join(["%d"%n._uid for n in N._S])

class CStorage(Storage):
    def __init__(self,Print=False):
        Storage.__init__(self,Print)

        self.instancestorage={}
        self.revinstancestorage={}
        self.iuid=0
    def printStatus(self):
        print self.ucount,len(self.instancestorage),len(self.E2)
        pass

    def getStorage(self,elem):
        a=elem[0]
        b=elem[1]
        if a not in self.instancestorage:
            self.iuid+=1
            self.instancestorage[a]=self.iuid
            self.revinstancestorage[self.iuid]=a
            x=self.iuid
        else:
            x=self.instancestorage[a]
        if b not in self.instancestorage:
            self.iuid+=1
            self.instancestorage[b]=self.iuid
            self.revinstancestorage[self.iuid]=b
            y=self.iuid
        else:
            y=self.instancestorage[b]
        if (x,y) not in self.instancestorage:
            self.iuid+=1
            self.instancestorage[(x,y)]=self.iuid
            self.revinstancestorage[self.iuid]=(x,y)
            r=self.iuid
        else:
            r=self.instancestorage[(x,y)]
        return r
    def revStorage(self,elem):
        a,b=self.revinstancestorage[elem]
        return (self.revinstancestorage[a],self.revinstancestorage[b])
    def incI(self,NodeID,X,Y,SUCC):
        added=False
        x=self.getStorage(X)
        y=self.getStorage(Y)
        #print X,x
        #print Y,y
        if self.Print:
            print NodeID[0]._uid,x,y
        self.count+=1

        #self.I[(NodeID,x[0])].add((x,y))

        if x not in self.FSet[NodeID]:
            self.FSet[NodeID][x]=set()
        if y not in self.FSet[NodeID][x]:
            self.ucount+=1
            added=True
            self.FSet[NodeID][x].add(y)


        if y not in self.RSet[NodeID]:
            self.RSet[NodeID][y]=set()
        if x not in self.RSet[NodeID][y]:
            self.ucount+=1
            self.RSet[NodeID][y].add(x)
        return added

    def dump(self):
        def container(node):
            c=node
            while hasattr(c,"_parent"):
                if (isinstance(c,compiler.ast.Module) or
                    isinstance(c,compiler.ast.Function)):
                    return c
                c=c._parent
            if (isinstance(c,compiler.ast.Module) or isinstance(c,compiler.ast.Function)):
                return c
            return None
        def r():
            return defaultdict(set)
        funcAl={}
        for NodeID,vars in self.FSet.iteritems():
            N=NodeID[0]
            if isinstance(N,tuple):
                N=N[0]
            cf=container(N)
            if cf:
                for var, rhss in vars.iteritems():
                    if cf._qualified_name not in funcAl:
                        funcAl[cf._qualified_name]={}
                    if self.revStorage(var)[1] not in funcAl[cf._qualified_name]:
                        funcAl[cf._qualified_name][self.revStorage(var)[1]]=set()
                    funcAl[cf._qualified_name][self.revStorage(var)[1]]|=rhss
                    if "@" not in funcAl:
                        funcAl["@"]={}
                    if self.revStorage(var)[1] not in funcAl["@"]:
                        funcAl["@"][self.revStorage(var)[1]]=set()
                    funcAl["@"][self.revStorage(var)[1]]|=rhss
                    #self.revStorage(var)[1] is the varName
                    #pdb.set_trace()
            else:
                pdb.set_trace()
        def printRes(res):        
           for k,v in res.iteritems():
                print k
                for i,v2 in v.iteritems():
                    print "    ",i
                    print "            ",",".join([str(z) for z in v2])
        return funcAl

    def nuke(self,NodeID):
        if NodeID in self.FSet:
            self.ucount-=len(self.FSet[NodeID])
            del self.FSet[NodeID]
        if NodeID in self.RSet:
            self.ucount-=len(self.RSet[NodeID])
            del self.RSet[NodeID]
    
    def contains(self,NodeID,X,Y):
        x=self.getStorage(X)
        y=self.getStorage(Y)
        return x in self.FSet[NodeID] and y in self.FSet[NodeID][x]
    def aliases(self,NodeID,P):
        p=self.getStorage(P)
        if p in self.FSet[NodeID]:
            return set([self.revStorage(i) for i in self.FSet[NodeID][p]])
        else:
            return set()
    def rev_aliases(self,NodeID,Q):
        q=self.getStorage(Q)
        if q in self.RSet[NodeID]:
            return set([self.revStorage(i) for i in self.RSet[NodeID][q]])
        else:
            return set()

    def inP(self,NodeID,P):
        p=self.getStorage(P)
        return Storage.inP(self,NodeID,p)

    def printAliasSet(self,filename,varname):
        for nid in self.FSet.keys():
            if isinstance(nid[0],tuple):
                N=nid[0][0]
            else:
                N=nid[0]
            if hasattr(N,"filename") and filename in N.filename:
                q=self.getStorage(((),varname))
                if q in self.FSet[nid]:
                    SID=set([self.revStorage(i) for i in self.FSet[nid][q]])
                    #self.instancestorage[i]
                    #pdb.set_trace()
                    print SID, N._uid, truncate(ast2string(N)) 
                    print "  ", ",".join(["%d"%n._uid for n in N._S])


class Goyal:
    def __init__(self,graph,workset,storage):
        self.G=graph
        self.W=workset
        self.S=storage
        self.P=PreTransform(self.G)
    def getSuccSet(self,node,id=0):
        pass

    def doAnalysis(self):
        self.P.addSuccPred()
        self.P.addContainsandUID()
        self.P.addReturn()
        self.P.selfsearch()
        self.P.addParamAndReturns()
        self.buildInitialWorkset()
        #self.W.printWorkset()
        self.worksetalgo()
        self.S.printStatistics()

    def buildInitialWorkset(self):
        print "Building initial workset!"
        def handleAssign(node):            
            if node.__class__.__name__=="Assign" and node.nodes and hasattr(node,"filename") and "builtins" not in node.filename:
                if node.nodes[0].__class__.__name__=="AssName":
                    lhs=node.nodes[0]
                    rhs=node.expr
                    if hasattr(rhs,"_targets"):
                        createsObj=bool([t for t in rhs._targets if  "__init__"==t.name])
                        T = [t for t in rhs._targets if hasattr(t,"filename") and "builtins" in t.filename]
                        isObj=[t for t in types(rhs) if isObject(t)]
                        createsObj|=(bool(T) and bool(isObj))
                        if createsObj:
                            self.W.add((node,0),(((),lhs._qualified_name),((),rhs._uid)))
                    else:
                        pass
                elif node.nodes[0].__class__.__name__=="AssAttr":
                    lhs=node.nodes[0]
                    rhs=node.expr
                    name="%s#%s"%(lhs.expr._qualified_name,lhs.attrname)
                    if hasattr(rhs,"_targets"):
                        createsObj=bool([t for t in rhs._targets if  "__init__"==t.name])
                        T = [t for t in rhs._targets if hasattr(t,"filename") and "builtins" in t.filename]
                        isObj=[t for t in types(rhs) if isObject(t)]
                        createsObj|=(bool(T) and bool(isObj))
                        if createsObj:
                            self.W.add((node,0),(((),name),((),rhs._uid)))
                    else:
                        pass
                    pass
                elif node.nodes[0].__class__.__name__=="AssTuple":
                    pass
                elif node.nodes[0].__class__.__name__=="Subscript":
                    pass
                else:
                    pdb.set_trace()
        self.G.visitNodes(handleAssign)
        #Does preprocessing for HyperCompressed storage
        def preProcessForHyper():
            W=set()
            visited=set()
            W.add( (self.G.start,0) )
            while W:
                NID=W.pop()
                rS=self.W.succ(NID)
                visited.add(NID)
                if rS:
                    #print W
                    W|=set([i for i in rS if i not in visited])

                    if not hasattr(NID[0],'_S2'):
                        NID[0]._S2=set()
                    for r in rS:
                        node,id=r
                        #if node!=NID:
                        if not hasattr(node,'_P2'):
                            node._P2=set()
                        node._P2.add( NID[0] )
                    NID[0]._S2|= set([i[0] for i in rS if i!=NID and i not in NID[0]._S2])
        preProcessForHyper()

        
        pass
    
    def doWeakUpdate(self,NID,p,q,x,y):
                #if assigning to q, and q does not point to y

                if x[1]==q[1] and not self.S.contains(NID,q,y): incQ=set((y,))
                else:                                           incQ=set()
                if ((x[1] in p[1]) or x[1]==p[1]) and not self.S.inP(NID,p):
                    incP=set ( (p,) )
                    #print "AAAAAA"
                    #print x
                    #print y
                    #print p
                    #print q
                else:
                    incP=set()


                incE3=set(((x,y),))                
                for qi in incQ:
                    incE3.add((p,qi))
                for pi in incP:
                    for qi in self.S.aliases(NID,q):
                        incE3.add( (pi,qi) )
                for pi in incP:
                    for qi in incQ:
                        incE3.add( (pi,qi) )
                    
                return incE3


    def doStrongUpdate(self,NID,p,q,x,y):
                #P=self.S.inP(NID,p)
                #if assigning to p, and q does not point to y
                #if X==lq and not P:     incP=set((p,))
                #else:                   incP=set()
                incP=set()
                P=True

                #if assigning to q, and q does not point to y
                if x==q and not self.S.contains(NID,q,y): incQ=set((y,))
                else:                                           incQ=set()
                    
                if x!=p and x not in incP:
                    incE2=set(((x,y),))
                else:
                    incE2=set()
                decE2=set( (x,i) for i in self.S.aliases(NID,x))
                if not P and not incP:
                    incE1=set()
                elif not P and incP: #Len of incP cannot be >1
                    for i in incE2:
                        self.S.incE2(NID,pcontext,i)
                    for i in decE2:
                        self.S.decE2(NID,pcontext,i)
                    incE1 = self.S.getE2(NID,pcontext)
                    if incE1==None: incE1=set()
                elif P and not incP:
                    incE1 = incE2
                elif P and incP: #Will never happen. Thus, we do not need self.S.I!
                    pass
                    #incE1 = self.S.getI(NID,pcontext) | set( ((x,y),)) - self.s.getE2(NID,pcontext)
                else:
                    incE1 = set( ((x,y),))
                incE3=set()
                
                if P: 
                    for qi in incQ:
                        incE3.add((p,qi))
                for pi in incP:
                    for qi in self.S.aliases(NID,q):
                        incE3.add( (pi,qi) )
                for pi in incP:
                    for qi in incQ:
                        incE3.add( (pi,qi) )
                incE4 = incE1 | incE3
                #pdb.set_trace()
                return incE4

    def handleEdge(self,NID,rhs,lq,x,y):
        if rhs.__class__.__name__=="CallFunc": #done
            if [t for t in rhs._targets if "__init__"==t.name]:
                #is a constructor call, block propagation of x
                #Others will be blocked by __RETVAL__ propagation
                if x[1]!=lq or y[1]==rhs._uid:
                    return self.propagate(NID,x,y)
                #else: pdb.set_trace()
            else:
                return self.propagate(NID,x,y)
        elif rhs.__class__.__name__=="Tuple": #done
            if x[1]!=lq or y[1]==rhs._uid:
                return self.propagate(NID,x,y)
            #else: pdb.set_trace()
        elif rhs.__class__.__name__=="List": #done
            if x[1]!=lq or y[1]==rhs._uid:
                return self.propagate(NID,x,y)
            #else: pdb.set_trace()
        elif rhs.__class__.__name__=="Const": #done
            if x[1]!=lq: #Abort propagation of x
                return self.propagate(NID,x,y)
            #else: pdb.set_trace()
        else:                #done
            if x[1]!=lq: #Abort propagation of x
                return self.propagate(NID,x,y)
            #else: pdb.set_trace()
        return set()

    def handleRHSComplex(self,NID,pcontext,qcontext,p,q,rbase,aug,res,x,y):
        aliases=self.S.aliases(NID,(qcontext,rbase))
        if aliases:
            oset=set()
            #pdb.set_trace()
            for a in aliases:
                oset|=self.S.rev_aliases(NID,a)
            oset=set([(c,"%s%s"%(n,aug)) for (c,n) in oset if
                      (c,"%s%s"%(n,aug))!=p])
            for o in oset:
                res|=self.doWeakUpdate(NID,p,o,x,y)
            #pdb.set_trace()
        return res


    def handleAssName(self,NID,rhs,left_qualified_name,x,y):
        lq=left_qualified_name
        if rhs.__class__.__name__=="Name":
            #Context is always from the x part, as the y part is the
            #abstract location
            rq=rhs._qualified_name
            pcontext=x[0]
            qcontext=x[0]
            p=(pcontext,lq)
            q=(qcontext,rq)
            res= self.doStrongUpdate(NID,p,q,x,y)
            return res

        elif rhs.__class__.__name__=="Getattr":
            if not [t for t in types(rhs) if t.__class__.__name__=="Function"]:
                #pdb.set_trace()                    
                rq="%s#%s"%(rhs.expr._qualified_name,rhs.attrname)
                pcontext=x[0]
                qcontext=x[0]
                p=(pcontext,lq)
                q=(qcontext,rq)
                res=self.doStrongUpdate(NID,p,q,x,y)
                #pdb.set_trace()
                res=self.handleRHSComplex(NID,pcontext,qcontext,p,q,rhs.expr._qualified_name,"#%s"%rhs.attrname,res,x,y)
                return res
            else:
                pass
            return self.propagate(NID,x,y)
        elif rhs.__class__.__name__=="Subscript":
            if len(rhs.subs)==1 and rhs.subs[0].__class__.__name__=="Const":
                if rhs.expr.__class__.__name__=="Name":
                    rn=rhs.expr._qualified_name
                elif rhs.expr.__class__.__name__=="Getattr":
                    rn="%s#%s"%(rhs.expr.expr._qualified_name,rhs.expr.attrname)
                rq="%s:%s"%(rn,str(rhs.subs[0].value))
                pcontext=x[0]
                qcontext=x[0]
                p=(pcontext,lq)
                q=(qcontext,rq)
                res=self.doStrongUpdate(NID,p,q,x,y)
                res=self.handleRHSComplex(NID,pcontext,qcontext,p,q,rn,":%s"%str(rhs.subs[0].value),res,x,y)
                return res
            else:
                return self.handleAssName(NID,rhs.expr,lq,x,y)
        else:
            return self.handleEdge(NID,rhs,lq,x,y)

    def handleAssAug(self,NID,rhs,left_qualified_name,aug,x,y):
        lq=left_qualified_name
        flq="%s%s"%(lq,aug)
        pcontext=x[0]
        p=(pcontext,flq)
        aliases=self.S.aliases(NID,(pcontext,lq))
        oset=set()
        if x==(pcontext,lq) and y not in aliases:
            aliases.add(y)
            oset.add((pcontext,lq))
        if x!=(pcontext,lq) and y in aliases:
            oset.add(x)
            
        if rhs.__class__.__name__=="Name":
            #Context is always from the x part, as the y part is the
            #abstract location
            rq=rhs._qualified_name
            qcontext=x[0]
            q=(qcontext,rq)

            res=self.doStrongUpdate(NID,p,q,x,y)
            if aliases:
                flab=bool(oset)
                for a in aliases:
                    oset|=self.S.rev_aliases(NID,a)
                oset2=set([(c,"%s%s"%(n,aug)) for (c,n) in oset if
                          (c,"%s%s"%(n,aug))!=p and (aug not in n)])
                for o in oset2:
                    #if o[1]=='test4.c#R': pdb.set_trace()
                    res2=self.doWeakUpdate(NID,o,q,x,y)
                    res|=res2

            return res
        elif rhs.__class__.__name__=="Getattr": #Should never happen                
            #pdb.set_trace()
            #if x[1]!=flq: #Abort propagation of x
            #    return self.propagate(NID,x,y)
            rq="%s#%s"%(rhs.expr._qualified_name,rhs.attrname)
            qcontext=x[0]
            q=(qcontext,rq)
            res=self.doStrongUpdate(NID,p,q,x,y)
            #pdb.set_trace()
            res=self.handleRHSComplex(NID,pcontext,qcontext,p,q,rhs.expr._qualified_name,"#%s"%rhs.attrname,res,x,y)
            if aliases:
                flab=bool(oset)
                for a in aliases:
                    oset|=self.S.rev_aliases(NID,a)
                oset2=set([(c,"%s%s"%(n,aug)) for (c,n) in oset if
                          (c,"%s%s"%(n,aug))!=p and (aug not in n)])
                for o in oset2:
                    #if o[1]=='test4.c#R': pdb.set_trace()
                    res2=self.doWeakUpdate(NID,o,q,x,y)
                    res|=res2            
            return res
            #else: pdb.set_trace()
        elif rhs.__class__.__name__=="Subscript":
            if x[1]!=flq: #Abort propagation of x
                return self.propagate(NID,x,y)                                
            return set()
            #else: pdb.set_trace()
        else:
            return self.handleEdge(NID,rhs,flq,x,y)

    def handlePostexec(self,NID,node,x,y):
        #pdb.set_trace()
        if isinstance(node[0],str):
            #print node
            if ":" not in node[0] and "#" not in node[0]: #this is an AssName
                R= self.handleAssName(NID,node[1],node[0],x,y)
                return R
            elif "#" in node[0] and not ":" in node[0]:
                L=node[0].split("#")                
                R= self.handleAssAug(NID,node[1],"#".join(L[:-1]),"#%s"%L[-1],x,y)
                return R
            elif ":" in node[0] and not "#" in node[0]:
                L=node[0].split(":")                
                R= self.handleAssAug(NID,node[1],":".join(L[:-1]),":%s"%L[-1],x,y)
                return R
            else:
                pdb.set_trace()
        return self.propagate(NID,x,y)


    def handleAssign(self,NID,node,x,y):
        S=set()
        lhs=node.nodes[0]
        rhs=node.expr    
        if lhs.__class__.__name__=="AssName": #Handling names 
            return self.handleAssName(NID,rhs,lhs._qualified_name,x,y)
            #print rhs.__class__.__name__
        elif lhs.__class__.__name__=="AssAttr":            
            return self.handleAssAug(NID,rhs,lhs.expr._qualified_name,"#%s"%lhs.attrname,x,y)
        elif lhs.__class__.__name__=="Subscript":
            if len(lhs.subs)==1 and lhs.subs[0].__class__.__name__=="Const":
                lq="%s:%s"%(lhs.expr._qualified_name,str(lhs.subs[0].value))
            else:
                lq=lhs.expr._qualified_name
            return self.propagate(NID,x,y)
        elif lhs.__class__.__name__=="AssTuple":
            return self.propagate(NID,x,y)
        else:
            pdb.set_trace()
        return S
    def propagate(self,NID,x,y):
        r= set()
        if not self.S.contains( NID, x,y ):
            r.add( (x,y) )
        return r
        
    def computeNewEdges(self,NID,x,y):
        N,id=NID
        if self.S.contains(NID,x,y):
            return set()
        if hasattr(N,"filename") and "builtins" in N.filename:
            return self.propagate(NID,x,y)
        if hasattr(N,"_postexec") and id<len(N._postexec):
            return self.handlePostexec(NID,N._postexec[id],x,y)
        else:
            if N.__class__.__name__=="Assign":
                return self.handleAssign(NID,N,x,y)
            else:
                return self.propagate(NID,x,y)

    def worksetalgo(self):
        import time
        print "Running workset!"
        counter=0
        cc=0
        stime=time.clock()
        while True:
            any=self.W.getandremoveany()
            if any:
                N,((cx,x),(cy,y))=any
                #print "Handling ",N
                #print "         ", ((cx,x),(cy,y))
                rS = self.W.succ(N)
                if rS:
                    newedges=self.computeNewEdges(N,(cx,x),(cy,y))
                    #print newedges
                    #print "Newedges: ", newedges
                    for k in rS:
                        for n in newedges:
                            #print "Adding K:",k," N:",n
                            self.W.add(k,n)
                        #print "Successor: ", k[1]
                        pass                
                #print any
                if self.S.incI(N,(cx,x),(cy,y),rS): cc+=1
                counter+=1
                if not counter%1000:
                    ctime=time.clock()
                    etime=ctime-stime
                    stime=ctime
                    #print N
                    print "Processed %d workset elements, %f el/sec, %d %d %d"%(counter,1000./etime,len(self.W.W),cc,sum([len(self.W.W[k]) for k in self.W.W.keys()]))
                    # gc.collect()
                    #print gc.get_referrers(X,Y)
                    #self.S.printStatus()
                 
            else:
                break


#Differentially compressed storage
class CStorageComp(CStorage):
    def __init__(self,workset,Print=False):
        CStorage.__init__(self,Print)
        self.FDSet=defaultdict(dict)
        self.RDSet=defaultdict(dict)
        self.W=workset
        self.oneSucOnePred=0
        self.onePredoneSuc=0
        self.onePred=0
        self.fcount=0
        self.rcount=0

    #Add X->Y alias pair to NodeID
    def incI(self,NodeID,X,Y,SUCC):
        added=False
        x=self.getStorage(X)
        y=self.getStorage(Y)
        #pdb.set_trace()
        if self.hasOneSucc(NodeID):
            succ=self.getSucc(NodeID)
            if self.hasOnePred(succ):
                self.oneSucOnePred+=1
                #Add propagation stoppers in next
                if x not in self.FDSet[succ]:
                    self.FDSet[succ][x]=set()
                #if y in self.FDSet[succ][x]: pdb.set_trace()                        
                if y not in self.FDSet[succ][x]:
                    self.FDSet[succ][x].add(y)
                if y not in self.RDSet[succ]:
                    self.RDSet[succ][y]=set()
                #if x in self.RDSet[succ][y]: pdb.set_trace()                        
                if x not in self.RDSet[succ][y]:
                    self.RDSet[succ][y].add(x)
                     
        self.count+=1
                
        if self.hasOnePred(NodeID):
            pred=self.getPred(NodeID)
            self.onePred+=1
            if self.hasOneSucc(pred): #Look up in prevs
                self.onePredoneSuc+=1
                #Kill propagation stoppers
                if x in self.FDSet[NodeID] and y in self.FDSet[NodeID][x]:
                    if y in self.FDSet[NodeID][x]:
                        self.FDSet[NodeID][x].remove(y)
                    if not self.FDSet[NodeID][x]:
                        del self.FDSet[NodeID][x]
                if y in self.RDSet[NodeID] and x in self.RDSet[NodeID][y]:
                    if x in self.RDSet[NodeID][y]:
                        self.RDSet[NodeID][y].remove(x)
                    if not self.RDSet[NodeID][y]:
                        del self.RDSet[NodeID][y]
                #Do the compressed addition
                #pdb.set_trace()
                if not self.contains(NodeID,X,Y):
                    if x not in self.FSet[NodeID]:
                        self.FSet[NodeID][x]=set()
                    if y not in self.FSet[NodeID][x]:
                        self.ucount+=1
                        self.fcount+=1
                        added=True
                        self.FSet[NodeID][x].add(y)
                if not self.rcontains(NodeID,Y,X): 
                    if y not in self.RSet[NodeID]:
                        self.RSet[NodeID][y]=set()
                    if x not in self.RSet[NodeID][y]:
                        self.ucount+=1
                        self.rcount+=1
                        self.RSet[NodeID][y].add(x)
                return added
            #else:
            #    if len(pred[0][0]._S2)>1 and not(hasattr(pred[0][0],"_contextjump") and pred[0][0]._contextjump):
            #        pdb.set_trace()
        #if self.count%10000 ==0: print self.count, self.oneSucOnePred, self.onePredoneSuc, self.fcount, self.rcount, self.onePred
        #Else do as normal
        #print X,x
        #print Y,y
        if self.Print:
            print NodeID[0]._uid,x,y

        if x not in self.FSet[NodeID]:
            self.FSet[NodeID][x]=set()
        if y not in self.FSet[NodeID][x]:
            self.ucount+=1
            added=True
            self.FSet[NodeID][x].add(y)

        if y not in self.RSet[NodeID]:
            self.RSet[NodeID][y]=set()
        if x not in self.RSet[NodeID][y]:
            self.ucount+=1
            self.RSet[NodeID][y].add(x)
        return added
    def nuke(self,NodeID):
        if NodeID in self.FSet:
            self.ucount-=len(self.FSet[NodeID])
            del self.FSet[NodeID]
        if NodeID in self.RSet:
            self.ucount-=len(self.RSet[NodeID])
            del self.RSet[NodeID]
        if NodeID in self.FDSet:
            del self.FDSet[NodeID]
        if NodeID in self.RDSet:
            del self.RDSet[NodeID]
    
    def hasOnePred(self,NodeID):        
        #N,C=NodeID[0]
        N=self.getNode(NodeID[0])
        id=NodeID[1]
        if hasattr(N,"_postexec"):
            if len(N._postexec)>0:
                if id==0:
                    if len(N._P)==1:
                        return True                
                elif id:
                    return True
            else:
                if len(N._P)==1:
                    return True                
        else:
            if len(N._P)==1:
                return True
        return False
    def hasOneSucc(self,NodeID):
        #return False
        N=self.getNode(NodeID[0])
        id=NodeID[1]
        if hasattr(N,"_postexec"):
            if id<len(N._postexec):
                return True
            else:
                if len(N._S)==1:
                    return True                
        else:
            if len(N._S)==1:
                return True
        return False
    
    def getSucc(self,NodeID):
        N=self.getNode(NodeID[0])
        NC=NodeID[0]
        id=NodeID[1]
        if hasattr(N,"_postexec"):
            if id<len(N._postexec):
                return (NC,id+1)
        for E in N._S:
            return (self.makeNode(E,NC),0)


    def getPred(self,NodeID):
        N=self.getNode(NodeID[0])
        NC=NodeID[0]
        #N,C=NodeID[0]
        id=NodeID[1]
        if hasattr(N,"_postexec"):
            if len(N._postexec)>0:
                if id==0:
                    for E in N._P:
                        if hasattr(E,"_postexec"):
                            return (self.makeNode(E,NC),len(E._postexec))
                        else:
                            return (self.makeNode(E,NC),0)
                elif id:
                    return (NC,id-1)
            else:
                for E in N._P:
                    if hasattr(E,"_postexec"):
                        return (self.makeNode(E,NC),len(E._postexec))
                    else:
                        return (self.makeNode(E,NC),0)
        else:
            for E in N._P:
                if hasattr(E,"_postexec"):
                    return (self.makeNode(E,NC),len(E._postexec))
                else:
                    return (self.makeNode(E,NC),0)
        pdb.set_trace()
    def contains(self,NodeID,X,Y):
        x=self.getStorage(X)
        y=self.getStorage(Y)
        if x in self.FDSet[NodeID] and y in self.FDSet[NodeID][x]:
            return False
        if x in self.FSet[NodeID] and y in self.FSet[NodeID][x]:
            return True
        #c=0
        while self.hasOnePred(NodeID):
            pred=self.getPred(NodeID)
            if self.hasOneSucc(pred): #Look up in prevs
                NodeID=pred
                #c+=1
                if x in self.FDSet[NodeID] and y in self.FDSet[NodeID][x]:
                    return False
                if x in self.FSet[NodeID] and y in self.FSet[NodeID][x]:
                    #print c
                    return True
            else:
                break
        #print c
        return x in self.FSet[NodeID] and y in self.FSet[NodeID][x]
    def rcontains(self,NodeID,X,Y):
        x=self.getStorage(X)
        y=self.getStorage(Y)
        if x in self.RDSet[NodeID] and y in self.RDSet[NodeID][x]:
            return False
        if x in self.RSet[NodeID] and y in self.RSet[NodeID][x]:
            return True
        while self.hasOnePred(NodeID):
            pred=self.getPred(NodeID)
            if self.hasOneSucc(pred): #Look up in prevs
                NodeID=pred
                if x in self.RDSet[NodeID] and y in self.RDSet[NodeID][x]:
                    return False
                if x in self.RSet[NodeID] and y in self.RSet[NodeID][x]:
                    return True
            else:
                break
        return x in self.RSet[NodeID] and y in self.RSet[NodeID][x]
    def aliases(self,NodeID,P):
        p=self.getStorage(P)
        iset=set()
        if p in self.FSet[NodeID]:            
            rset=set([i for i in self.FSet[NodeID][p]])
        else:
            rset=set()
        if p in self.FDSet[NodeID]:            
            iset=set([i for i in self.FDSet[NodeID][p]])                
   
        while self.hasOnePred(NodeID):
            pred=self.getPred(NodeID)
            if self.hasOneSucc(pred): #Look up in prevs
                NodeID=pred                
                if p in self.FDSet[NodeID]:            
                    iset|=set([i for i in self.FDSet[NodeID][p]])                
                if p in self.FSet[NodeID]:            
                    rset|=set([i for i in self.FSet[NodeID][p] if i not in iset])                
            else:
                break
        return set([self.revStorage(i) for i in rset])
        
    def rev_aliases(self,NodeID,Q):
        q=self.getStorage(Q)
        iset=set()
        if q in self.RSet[NodeID]:
            rset = set([i for i in self.RSet[NodeID][q]])
        else:
            rset = set()
        if q in self.RDSet[NodeID]:            
            iset=set([i for i in self.RDSet[NodeID][q]])                
        while self.hasOnePred(NodeID):
            pred=self.getPred(NodeID)
            if self.hasOneSucc(pred): #Look up in prevs
                NodeID=pred
                if q in self.RDSet[NodeID]:            
                    iset|=set([i for i in self.RDSet[NodeID][q]])                
                if q in self.RSet[NodeID]:            
                    rset|=set([i for i in self.RSet[NodeID][q] if i not in iset])                
            else:
                break
        return set([self.revStorage(i) for i in rset])


    def inP(self,NodeID,P):
        p=self.getStorage(P)
        if p in self.FSet[NodeID]:
            return True
        while self.hasOnePred(NodeID):
            pred=self.getPred(NodeID)
            if self.hasOneSucc(pred): #Look up in prevs
                NodeID=pred
                if p in self.FSet[NodeID]:
                    return True
            else:
                break
        return False


    def printAliasSet(self,filename,varname):
        for nid in self.FSet.keys():
            if isinstance(nid[0],tuple):
                N=nid[0][0]
            else:
                N=nid[0]
            if hasattr(N,"filename") and filename in N.filename:
                q=self.getStorage(((),varname))
                if q in self.FSet[nid]:
                    SID=set([self.revStorage(i) for i in self.FSet[nid][q]])
                    #self.instancestorage[i]
                    #pdb.set_trace()
                    print SID, N._uid, truncate(ast2string(N)) 
                    print "  ", ",".join(["%d"%n._uid for n in N._S])

    def getNode(self,node):
        return node
    def makeNode(self,newNode,NC):
        return newNode

#Differentially compressed storage extended for trace
#Takes context into acct.
class CStorageCompTrace(CStorageComp):
    def __init__(self,workset,Print=False):
        CStorageComp.__init__(self,workset,Print)
    def getNode(self,node):
        return node[0]
    def makeNode(self,newNode,NC):
        return (newNode,NC[1])
 
    def hasOneSucc(self,NodeID):
        #return False
        N=self.getNode(NodeID[0])
        id=NodeID[1]
        if hasattr(N,"_postexec"):
            if id<len(N._postexec):
                return True
            else:
                if hasattr(N,"_transitions"):
                    return False
                if hasattr(N,"_targets"):
                    return False
                if len(N._S)==1:
                    return True                
        else:
            if hasattr(N,"_transitions"):
                return False
            if hasattr(N,"_targets"):
                return False
            if len(N._S)==1:
                return True
        return False   


#Highly efficient diff-compressed storage for trace
#Assumes node._S2, _P2, and _contextjump are computed already.
#This requires preprocessing on the level of the workset algorithm.
class CStorageCompHyper(CStorageComp):
    def __init__(self,workset,Print=False):
        CStorageComp.__init__(self,workset,Print)
    def hasOnePred(self,NodeID):        
        #N,C=NodeID[0]
        N=self.getNode(NodeID[0])
        id=NodeID[1]
        try:
            if hasattr(N,"_postexec"):
                if len(N._postexec)>0:
                    if id==0:
                        if len(N._P2)==1:
                            return True                
                    elif id:
                        return True
                else:
                    if len(N._P2)==1:
                        return True                
            else:
                if len(N._P2)==1:
                    return True
        except:
            return False
        return False
    
    def hasOneSucc(self,NodeID):
        #return False
        N=self.getNode(NodeID[0])
        id=NodeID[1]
        if hasattr(N,"_postexec"):
            if id<len(N._postexec):
                return True
            else:
                try:
                    if len(N._S2)==1:
                        if not N._contextjump:
                            return True         
                except:
                    return False
        else:
            try:
                if len(N._S2)==1:
                    if not N._contextjump:
                        return True         
            except:
                return False
        return False   

    def getSucc(self,NodeID):
        N=self.getNode(NodeID[0])
        id=NodeID[1]
        if hasattr(N,"_postexec"):
            if id<len(N._postexec):
                return (N,id+1)        
        for E in N._S2:
            return (self.makeNode(E,None),0)


    def getPred(self,NodeID):
        N=self.getNode(NodeID[0])
        #N,C=NodeID[0]
        id=NodeID[1]
        if hasattr(N,"_postexec"):
            if len(N._postexec)>0:
                if id==0:
                    for E in N._P2:
                        if hasattr(E,"_postexec"):
                            return (self.makeNode(E,None),len(E._postexec))
                        else:
                            return (self.makeNode(E,None),0)
                elif id:
                    return (N,id-1)
            else:
                for E in N._P2:
                    if hasattr(E,"_postexec"):
                        return (self.makeNode(E,None),len(E._postexec))
                    else:
                        return (self.makeNode(E,None),0)
        else:
            for E in N._P2:
                if hasattr(E,"_postexec"):
                    return (self.makeNode(E,None),len(E._postexec))
                else:
                    return (self.makeNode(E,None),0)



#Highly efficient diff-compressed storage for trace
#Assumes node._S2, _P2, and _contextjump are computed already.
#This requires preprocessing on the level of the workset algorithm.
class CStorageCompHyperTrace(CStorageCompTrace):
    def __init__(self,workset,Print=False):
        CStorageCompTrace.__init__(self,workset,Print)
        self.remPred=dict()
        self.remSucc=dict()
        self.sawPred=set()
        self.sawSucc=set()
    def hasOnePred(self,NodeID):        
        #N,C=NodeID[0]
        if NodeID in self.remPred:
            return True
        if NodeID in self.sawPred:
            return False
        self.sawPred.add(NodeID)
        N=self.getNode(NodeID[0])
        id=NodeID[1]        
        try:
            if hasattr(N,"_postexec"):
                if len(N._postexec)>0:
                    if id==0:
                        if len(N._P2)==1:
                            self.remPred[NodeID]=self.getPred(NodeID)
                            return True                
                    elif id:
                        self.remPred[NodeID]=self.getPred(NodeID)
                        return True
                else:
                    if len(N._P2)==1:
                        self.remPred[NodeID]=self.getPred(NodeID)
                        return True                
            else:
                if len(N._P2)==1:
                    self.remPred[NodeID]=self.getPred(NodeID)
                    return True
        except:
            return False
        return False
    
    def hasOneSucc(self,NodeID):
        #return False
        if NodeID in self.remSucc:
            return True
        if NodeID in self.sawSucc:
            return False
        self.sawSucc.add(NodeID)
        N=self.getNode(NodeID[0])
        id=NodeID[1]
        if hasattr(N,"_postexec"):
            if id<len(N._postexec):
                self.remSucc[NodeID]=self.getSucc(NodeID)
                return True
            else:
                try:
                    if len(N._S2)==1:
                        if not N._contextjump:
                            self.remSucc[NodeID]=self.getSucc(NodeID)
                            return True         
                except:
                    return False
        else:
            try:
                if len(N._S2)==1:
                    if not N._contextjump:
                        self.remSucc[NodeID]=self.getSucc(NodeID)
                        return True         
            except:
                return False
        return False   
    def getSucc(self,NodeID):
        if NodeID in self.remSucc:
            return self.remSucc[NodeID]
        
        N=self.getNode(NodeID[0])
        NC=NodeID[0]
        id=NodeID[1]
        if hasattr(N,"_postexec"):
            if id<len(N._postexec):
                return (NC,id+1)        
        for E in N._S2:
            return (self.makeNode(E,NC),0)


    def getPred(self,NodeID):
        if NodeID in self.remPred:
            return self.remPred[NodeID]
        N=self.getNode(NodeID[0])
        NC=NodeID[0]
        #N,C=NodeID[0]
        id=NodeID[1]
        if hasattr(N,"_postexec"):
            if len(N._postexec)>0:
                if id==0:
                    for E in N._P2:
                        if hasattr(E,"_postexec"):
                            return (self.makeNode(E,NC),len(E._postexec))
                        else:
                            return (self.makeNode(E,NC),0)
                elif id:
                    return (NC,id-1)
            else:
                for E in N._P2:
                    if hasattr(E,"_postexec"):
                        return (self.makeNode(E,NC),len(E._postexec))
                    else:
                        return (self.makeNode(E,NC),0)
        else:
            for E in N._P2:
                if hasattr(E,"_postexec"):
                    return (self.makeNode(E,NC),len(E._postexec))
                else:
                    return (self.makeNode(E,NC),0)

class TraceWorksetStorage(WorksetStorage):
    def __init__(self,graph,maxallowed=1):
        WorksetStorage.__init__(self)
        self.maxallowed=maxallowed
        self.G=graph
        self.cache={}
        self.refcount=defaultdict(int)
    def add(self,NID,elem):
        if elem not in self.W[NID]:
            self.refcount[NID[0][0]]+=1
        WorksetStorage.add(self,NID,elem)
    def getandremoveany(self):
        res=WorksetStorage.getandremoveany(self)
        if res:
            self.refcount[res[0][0][0]]-=1
        return res
        
    def newContext(self,context,newcid):
        newL=[]
        enc=0
        for i in context:
            if i!=newcid:
                newL.append(i)
            else:
                enc+=1
                if enc<self.maxallowed:
                    newL.append(i)
                elif enc==self.maxallowed:
                    newL.append(i)
                    break
        if enc<self.maxallowed:
            newL.append(newcid)
        return tuple(newL)
     
    def getSucc(self,context,node):
        #pdb.set_trace()
        if hasattr(node,"_targets") and node._targets:#node.__class__.__name__=="CallFunc":            
            nc=context
            #pdb.set_trace()
            if not(hasattr(node,"filename") and "builtins" in node.filename):
                T=[t for t in node._targets if not (hasattr(t,"filename") and "builtins" in t.filename)]
                if T:
                    #print "CALL:  %s"%node
                    #PPcontext(self,node,context)
                    #pdb.set_trace()
                    nc=self.newContext(context,node._uid)
                    
            return set([(nc,s) for s in node._S])
        if hasattr(node,"_transitions"):
            r=set()
            for s in node._S:
                if (node,s) in self.G.crossTransitions:
                    if node._parent.__class__.__name__=="CallFunc":
                        uidS=set()
                        for t in node._parent._targets:
                            if hasattr(t,"_uid"):
                                uidS.add(t._uid)
                            else:
                                uidS.add(-1)
                        
                        iscall=True
                        try:
                            iscall=s._contains._uid in uidS
                        except:
                            pass
                        #pdb.set_trace()
                        if iscall:
                            nc=context
                        else:
                            if not(hasattr(node,"filename") and "builtins" in node.filename):
                                callercontexts=[self.G.revuid[c]._contains._uid for c in context]
                                searchingcontext=s._contains
                                lastpos=-1
                                for i,c in enumerate(callercontexts):
                                    if c==searchingcontext._uid:
                                        lastpos=i
                                if lastpos!=-1:
                                    #pdb.set_trace()
                                    nc=context[:lastpos]
                                else:
                                    s=None
                            else:
                                nc=context
                    elif node._parent.__class__.__name__=="Return":                            
                        continue
                    else:
                        if not(hasattr(node,"filename") and "builtins" in node.filename):
                            #nc=context[:-1]
                            callercontexts=[self.G.revuid[c]._contains._uid for c in context]
                            searchingcontext=s._contains
                            lastpos=-1
                            for i,c in enumerate(callercontexts):
                                if c==searchingcontext._uid:
                                    lastpos=i
                            if lastpos!=-1:
                                #pdb.set_trace()
                                nc=context[:lastpos]
                            else:
                                s=None
                        else:
                            nc=context
                else:
                    nc=context
                if s!=None:
                    r.add( (nc,s) )
            #if not r:
            #    pdb.set_trace()
            return r
        else:
            return set([(context,s) for s in node._S])
    def succI(self,NID):
        N,C=NID[0]
        id=NID[1]
        if hasattr(N,"_postexec"):
            if id<len(N._postexec):
                return set(( ((N,C),id+1), ) )
        res=self.getSucc(C,N)
        #pdb.set_trace()
        #Here we are flipping context,node to node,context
        return set([ ((r[1],r[0]),0) for r in res])
    def succ(self,NID):
        ONID=NID
        if ONID in self.cache:
            return self.cache[ONID]
        S=self.succI(NID)
        rS=set()
        #print 1
        visited=set()
        while S:        #Skips over undesirable statements             
            NID=S.pop()
            visited.add(NID)
            (node,c),id=NID
            if hasattr(node,"filename") and "builtins" in node.filename:
                S|=(self.succI(NID) - visited)
            if hasattr(node,"_postexec") and id<len(node._postexec):
                rS.add( NID )
            else:
                if node.__class__.__name__=="Assign":
                    rS.add( NID )
                else:
                    S|=(self.succI(NID) - visited)
        #print 0
        self.cache[ONID]=rS
        return rS
        
        #if N.__class__.__name__=="CallFunc":
        #    if hasattr(N,"filename") and "builtins" not in N.filename:
        #        nc=self.newContext(C,N._uid)
        #    else:
        #        nc=C
        #    R=set([((n,nc),0) for n in N._S])
        #    return R
        #if hasattr(N,"_transitions"):
        #    r=set()
        #    for s in N._S:
        #        if (N,s) in self.G.crossTransitions:
        #            if N._parent.__class__.__name__=="CallFunc":
        #                snc=C
        #            elif N._parent.__class__.__name__=="Return":                            
        #                continue
        #            else:
        #                if hasattr(N,"filename") and "builtins" not in N.filename:
        #                    snc=C[:-1]
        #                else:
        #                    snc=C
        #        else:
        #            snc=C
        #        r.add( ((s,snc),0) )
        #    return r
        #else:
        #    R=set([((n,C),0) for n in N._S])
        #    return R

            
    def printWorkset(self):
        for (k,v) in self.W.iteritems():
            print "Node : %s, subid:%d"%(truncate(ast2string(k[0][0])),k[1])
            for e in v:
                print "    ",e


class GoyalTrace(Goyal):
    def __init__(self,graph,workset,storage,maxallowed):
        Goyal.__init__(self,graph,workset,storage)
        self.maxallowed=maxallowed
        self.done=False
        self.hasemptyworkset=False
        self.saw=0

    def newContext(self,context,newcid):
        newL=[]
        enc=0
        for i in context:
            if i!=newcid:
                newL.append(i)
            else:
                enc+=1
                if enc<self.maxallowed:
                    newL.append(i)
                elif enc==self.maxallowed:
                    newL.append(i)
                    break
        if enc<self.maxallowed:
            newL.append(newcid)
        return tuple(newL)


    def buildInitialWorkset(self):
        print "Building initial workset!"
        def handleAssign(c,node):            
            if node.__class__.__name__=="Assign" and node.nodes and hasattr(node,"filename") and "builtins" not in node.filename:
                if node.nodes[0].__class__.__name__=="AssName":
                    lhs=node.nodes[0]
                    rhs=node.expr
                    if hasattr(rhs,"_targets"):
                        initObj=bool([t for t in rhs._targets if  "__init__"==t.name])
                        if initObj:
                            self.W.add(((node,c),0),((c,lhs._qualified_name),(c,rhs._uid)))
                            
                        T = [t for t in rhs._targets if hasattr(t,"filename") and "builtins" in t.filename]
                        isObj=[t for t in types(rhs) if isObject(t)]
                        createsObj=(bool(T) and bool(isObj)) and not initObj
                        if createsObj:
                            self.W.add(((lhs,c),0),((c,lhs._qualified_name),(c,rhs._uid)))
                    else:
                        pass
                elif node.nodes[0].__class__.__name__=="AssAttr":
                    lhs=node.nodes[0]
                    rhs=node.expr
                    name="%s#%s"%(lhs.expr._qualified_name,lhs.attrname)
                    if hasattr(rhs,"_targets"):                        
                        initObj=bool([t for t in rhs._targets if  "__init__"==t.name])
                        if initObj:
                            self.W.add(((node,c),0),((c,name),(c,rhs._uid)))
                            
                        T = [t for t in rhs._targets if hasattr(t,"filename") and "builtins" in t.filename]
                        isObj=[t for t in types(rhs) if isObject(t)]
                        createsObj=(bool(T) and bool(isObj)) and not initObj
                        if createsObj:
                            self.W.add(((lhs,c),0),((c,name),(c,rhs._uid)))
                    #if rhs.__class__.__name__=="CallFunc":
                    #    if [t for t in rhs._targets if "__init__"==t.name]:
                    #        self.W.add(((node,c),0),((c,name,),(c,rhs._uid)))
                    #elif rhs.__class__.__name__=="List":                        
                    #    self.W.add(((node,c),0),((c,name),(c,rhs._uid)))
                    #elif rhs.__class__.__name__=="Tuple":                        
                    #    self.W.add(((node,c),0),((c,name),(c,rhs._uid)))
                    else:
                        pass
                    pass
                elif node.nodes[0].__class__.__name__=="AssTuple":
                    pass
                elif node.nodes[0].__class__.__name__=="Subscript":
                    pass
                else:
                    pdb.set_trace()
        #self.G.visitNodes(handleAssign)
        def PPcontext(self,node,context):
            print "NODE: ",node
            for c in context:
                N=self.G.revuid[c]
                print "    ",truncate(str(N)),N.lineno
                #pdb.set_trace()

        W=set()
        visited=set()
        W.add( ((self.G.start._uid,),self.G.start) )
        count=0
        while W:
            R=W.pop()
            c,n=R
            S=self.W.getSucc(c,n)
            count+=1
            if not count%10000:
                try:
                    print len(W), n.filename
                except:
                    print len(W)
            for s in S:
                if s not in visited:
                    W.add(s)
            handleAssign(c,n)
            visited.add( (c,n) )

        #Does preprocessing for HyperCompressed storage
        def preProcessForHyper():
            W=set()
            visited=set()
            W.add( ((self.G.start,(self.G.start._uid,)),0) )
            while W:
                NID=W.pop()
                rS=self.W.succ(NID)
                visited.add(NID)
                if rS:
                    #print rS
                    #print W
                    W|=set([i for i in rS if i not in visited])

                    if not hasattr(NID[0][0],'_S2'):
                        NID[0][0]._S2=set()
                    if not hasattr(NID[0][0],'_contextjump'):
                        NID[0][0]._contextjump=False
                    for r in rS:
                        (node,c),id=r
                        NID[0][0]._contextjump|= (c!=NID[0][1])
                        #if node!=NID:
                        if not hasattr(node,'_P2'):
                            node._P2=set()
                        node._P2.add( NID[0][0] )
                    NID[0][0]._S2|= set([i[0][0] for i in rS if i!=NID and i not in NID[0][0]._S2])
        preProcessForHyper()

    def handleAssName(self,NID,rhs,left_qualified_name,x,y):
        lq=left_qualified_name
        pcontext=NID[0][1]
        qcontext=NID[0][1]
        if NID[0][0].__class__.__name__=="CallFunc":
            pcontext=self.newContext(pcontext,NID[0][0]._uid)
        if rhs.__class__.__name__=="Name":
            #Context is always from the x part, as the y part is the
            #abstract location
            rq=rhs._qualified_name
            if "__RETVAL__" in rq: #This is a return stmt
                fromUID=NID[0][0]._parent.expr._uid
                qcontext=self.newContext(pcontext,fromUID)
                #pdb.set_trace()
            p=(pcontext,lq)
            q=(qcontext,rq)
            res= self.doStrongUpdate(NID,p,q,x,y)
            return res

        elif rhs.__class__.__name__=="Getattr":
            if not [t for t in types(rhs) if t.__class__.__name__=="Function"]:
                #pdb.set_trace()                    
                rq="%s#%s"%(rhs.expr._qualified_name,rhs.attrname)
                p=(pcontext,lq)
                q=(qcontext,rq)
                res=self.doStrongUpdate(NID,p,q,x,y)
                #pdb.set_trace()
                res=self.handleRHSComplex(NID,pcontext,qcontext,p,q,rhs.expr._qualified_name,"#%s"%rhs.attrname,res,x,y)
                return res
            else:
                pass
            return self.propagate(NID,x,y)
        elif rhs.__class__.__name__=="Subscript":
            if len(rhs.subs)==1 and rhs.subs[0].__class__.__name__=="Const":
                if rhs.expr.__class__.__name__=="Name":
                    rn=rhs.expr._qualified_name
                elif rhs.expr.__class__.__name__=="Getattr":
                    rn="%s#%s"%(rhs.expr.expr._qualified_name,rhs.expr.attrname)
                rq="%s:%s"%(rn,str(rhs.subs[0].value))
                p=(pcontext,lq)
                q=(qcontext,rq)
                res=self.doStrongUpdate(NID,p,q,x,y)
                res=self.handleRHSComplex(NID,pcontext,qcontext,p,q,rn,":%s"%str(rhs.subs[0].value),res,x,y)
                return res
            else:
                return self.handleAssName(NID,rhs.expr,lq,x,y)
        else:
            return self.handleEdge(NID,rhs,lq,x,y)

    def handleAssAug(self,NID,rhs,left_qualified_name,aug,x,y):
        lq=left_qualified_name
        flq="%s%s"%(lq,aug)
        pcontext=NID[0][1]
        qcontext=NID[0][1]
        p=(pcontext,flq)
        aliases=self.S.aliases(NID,(pcontext,lq))
        oset=set()
        if x==(pcontext,lq) and y not in aliases:
            aliases.add(y)
            oset.add((pcontext,lq))
        if x!=(pcontext,lq) and y in aliases:
            oset.add(x)
            
        if rhs.__class__.__name__=="Name":
            #Context is always from the x part, as the y part is the
            #abstract location
            rq=rhs._qualified_name
            q=(qcontext,rq)

            res=self.doStrongUpdate(NID,p,q,x,y)
            if aliases:
                flab=bool(oset)
                for a in aliases:
                    oset|=self.S.rev_aliases(NID,a)
                oset2=set([(c,"%s%s"%(n,aug)) for (c,n) in oset if
                          (c,"%s%s"%(n,aug))!=p and (aug not in n)])
                for o in oset2:
                    #if o[1]=='test4.c#R': pdb.set_trace()
                    res2=self.doWeakUpdate(NID,o,q,x,y)
                    res|=res2

            return res
        elif rhs.__class__.__name__=="Getattr": #Should never happen                
            rq="%s#%s"%(rhs.expr._qualified_name,rhs.attrname)
            q=(qcontext,rq)

            res=self.doStrongUpdate(NID,p,q,x,y)
            res=self.handleRHSComplex(NID,pcontext,qcontext,p,q,rhs.expr._qualified_name,"#%s"%rhs.attrname,res,x,y)
            if aliases:
                flab=bool(oset)
                for a in aliases:
                    oset|=self.S.rev_aliases(NID,a)
                oset2=set([(c,"%s%s"%(n,aug)) for (c,n) in oset if
                          (c,"%s%s"%(n,aug))!=p and (aug not in n)])
                for o in oset2:
                    #if o[1]=='test4.c#R': pdb.set_trace()
                    res2=self.doWeakUpdate(NID,o,q,x,y)
                    res|=res2
            return res
            #pdb.set_trace()
            #if x[1]!=flq: #Abort propagation of x
            #    return self.propagate(NID,x,y)
            #return set()
            #else: pdb.set_trace()
        elif rhs.__class__.__name__=="Subscript":
            if x[1]!=flq: #Abort propagation of x
                return self.propagate(NID,x,y)                                
            return set()
            #else: pdb.set_trace()
        else:
            return self.handleEdge(NID,rhs,flq,x,y)

    def computeNewEdges(self,NID,x,y):
        (N,c),id=NID
        if self.S.contains(NID,x,y):
            #pdb.set_trace()
            return set()
        if hasattr(N,"filename") and "builtins" in N.filename:
            return self.propagate(NID,x,y)
        if hasattr(N,"_postexec") and id<len(N._postexec):
            return self.handlePostexec(NID,N._postexec[id],x,y)
        else:
            if N.__class__.__name__=="Assign":
                return self.handleAssign(NID,N,x,y)
            else:
                return self.propagate(NID,x,y)

    def worksetalgo(self):
        import time
        print "Running workset!"
        counter=0
        cc=0
        ic=0
        stime=time.clock()
        tracenodes=defaultdict(set)
        def tracecompress(tracenodes):
            def F(node):
                self.saw+=1
                if self.W.refcount[node]!=0:
                    self.hasemptyworkset=False
                    self.done=True
            for node in tracenodes.keys():
                self.hasemptyworkset=True
                self.saw=0
                self.done=False
                self.G.revdfs(F,node,lambda x : self.done)
                if self.hasemptyworkset:
                    #print "Unreachable %s"%str(node)
                    #print "Nuking %d"%len(tracenodes[node])
                    for NID in tracenodes[node]:
                        self.S.nuke(NID)
                    del tracenodes[node]

        while True:
            any=self.W.getandremoveany()
            if any:
                N,(X,Y)=any
                #print "Handling ",N
                #print "         ", (X,Y)
                rS = self.W.succ(N)
                if rS:
                    newedges=self.computeNewEdges(N,X,Y)
                    #print "Newedges: ", newedges
                    for k in rS:
                        for n in newedges:
                            #print "Adding K:",k," N:",n
                            self.W.add(k,n)
                        #print "Successor: ", k[1]
                        pass
                if self.S.incI(N,X,Y,rS): cc+=1
                if self.S.incI(((N[0][0],()),N[1]),((),X[1]),((),Y[1]),rS): ic+=1
                tracenodes[N[0][0]].add(N)
                counter+=1
                if not counter%10000:
                    #print 1
                    #tracecompress(tracenodes)
                    #print 2
                    ctime=time.clock()
                    etime=ctime-stime
                    stime=ctime

                    #print N
                    print "Processed %d workset elements, %f el/sec, %d %d %d %d %s %d"%(counter,10000./etime,len(self.W.W),cc,ic,sum([len(self.W.W[k]) for k in self.W.W.keys()]),str(N[0][1]),self.S.ucount)
                    # gc.collect()
                    #print gc.get_referrers(X,Y)
                    #self.S.printStatus()
                    #if not counter%300000:
                    #    pdb.set_trace()
                    #    self.S.ZERO()
                    #    gc.collect()
            else:
                break
        #tracecompress(tracenodes)


class ComboStorage:
    def __init__(self,S1,S2):
        self.S1=S1
        self.S2=S2
        print "Using storages %s, %s"%(S1.__class__.__name__,S2.__class__.__name__)


    def __getattr__(self,attr):
        if attr in dir(self.S1) and attr in dir(self.S2):
            s1attr=eval("self.S1.%s"%attr)
            s2attr=eval("self.S2.%s"%attr)
            if type(s1attr)==type(self.__init__):
                def F(*args):
                    r1=s1attr(*args)
                    r2=s2attr(*args)
                    if r1==r2:
                        return r1
                    else:
                        #pdb.set_trace()
                        return r1
                return F
            else:
                if s1attr==s2attr:
                    return s1attr
                else:
                    print ">>> Unequal %s: %s %s"%(attr,str(s1attr),str(s2attr))
                    return s1attr
        pass


