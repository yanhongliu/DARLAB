import analysis.source
import analysis.common
import os.path
import compiler
import sys
import inspect
import pdb
from StringIO import StringIO
import pyunparse
import compiler
from compiler.visitor import ASTVisitor 
from collections import defaultdict
import cPickle
import gc

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
   if len(s)<50:
      return s
   #s=s.replace("\n","  ")
   return "%s ... %d ... %s"%(s[:20],len(s),s[-20:])


class Graph:
  def __init__(self):
    self.F={}
    self.B={}
    self.start=None
    self.nodes=set()
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

graph=Graph()
L=[]
graphslice=Graph()
newslice=Graph()

max=0
count=0
def visit(f,t):
    #visited CFG node t coming from f
    global graph
    global max
    global count
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
      count+=1
      if f._uid>max:
          max=f._uid
      if (count%100 == 1):
          if hasattr(f,"lineno"):
              print count, f._uid, max, f.lineno
          else:
              print count, f._uid, max
      graph.addedge(f,t)


def  computeinitialslice(ast):
  #lines=set(l.strip() for l in ast2string(ast).split('\n'))
  def F(f,t):
      global graphslice
      #res=truncate(ast2string(f))
      
      #if (len(res)>3 and res[-1]=="\n") or res.strip() in lines:
      #  L.append(info + " f: " + res + " \n         " + truncate(str(oldf)))
      graphslice.addedge(f,t)
      #x=analysis.common.ltype(t)
      #if x:
      #    print "\t%s : %s"%(`t`,analysis.common.lname(x[0]))
      #pass
  return F

def slice(f,t):
  global newslice
  global graphslice
  if f in graphslice.F:
    #pdb.set_trace()
    if t not  in graphslice.F:
      newtargets=set()
      def action(point):
        if point in graphslice.F:
          newtargets.add(point)
      def condition(cp):
        return cp in graphslice.F
      graph.dfs(action,t,condition)
      for n in newtargets:
        newslice.addedge(f,n)
    else:
      newslice.addedge(f,t)


def printnode():
  def F(f,t):
    info= "%d -> %d, lineno %s -> %s"%(f._uid,t._uid,f.lineno,t.lineno)
    res=truncate(ast2string(f))
    res=res.replace("\n"," \\n ")
    print "%s -> %s"%(truncate(str(f)), truncate(str(t)))
  return F

def graphvizGenerator(Graph):
    def F(f,t):
        _f=analysis.pydot.Node(str(f._uid))
        res=truncate(ast2string(f)).replace("\n","\\l").replace(":","->").replace("'","_").replace('"',"_")
        _f.set_label(r"\lid(%d) at line=%d\l\l%s\l"%(f._uid,f.lineno or -1,res))
        Graph.add_node(_f)
        _t=analysis.pydot.Node(str(t._uid))
        res=truncate(ast2string(t)).replace("\n","\\l").replace(":","->").replace("'","_").replace('"',"_")
        _t.set_label(r"\lid(%d) at line=%d\l\l%s\l"%(t._uid,t.lineno or -1,res))
        Graph.add_node(_t)
        Graph.add_edge(analysis.pydot.Edge(_f,_t,arrowhead='empty'))
    return F

#print s
#sys.exit(0)


fname=sys.argv[1]
session=analysis.source.AnalysisSession()
session.librarypath='analysis\\'
session.codepath=os.path.dirname(sys.argv[1])
session.simplify_files=True
ast=session.processFile_to_CFG(fname,cfg_visitor=visit,only_source_ast=False,post_traversal=False) #computes graph
print "Computed CFG!\n Slicing..."


#ast=session.process_file("chunk.py")
#sys.exit(0)
graph.visitEdges(computeinitialslice(ast)) #computes graphslice      
graphslice.visitEdges(slice) #computes newslice
#newslice.visitEdges(printnode())

def analysis(slice):
    def dispatch(namespace,*args):
        name=args[0].__class__.__name__
        if "handle%s"%name in namespace:
            namespace["handle%s"%name](*args)
        elif "default" in namespace:
            namespace["default"](*args)
        else:
            print >>Debug(), "Unhandled class %s"%name
    
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
        for v_a in param._contexts.values():
            for s_v_a in v_a:
                res.add(s_v_a)
        return res

    def isObject(type,primitives=set("builtins.%s"%i for i in
                                ("boolean","none","int","long","float","string","buffer","tuple")
                                )):
        if type in primitives:
            return False
        if hasattr(type,"_qualified_name"):
            if type._qualified_name in primitives:
                return False
        return True

    class pClass:
        def __init__(self,function,name):
            self._qualified_name=function._qualified_name+"."+name
            pass

    class AnalysisVisitorAndersens(ASTVisitor):

        # Top-level node processing.

        def __init__(self):

            """
            Initialise the visitor with an optional 'session', 'filename', and an
            optional 'module_name'.
            """

            ASTVisitor.__init__(self) 
            self.objCreations=defaultdict(set)
            self.objTypes=defaultdict(set)
            self.count=0;
            self.objmaps=defaultdict(set)
            self.depmap=defaultdict(set)


        def find_return(self,target,node):
            def ifindreturn(target,node,visited):               
                visited.add(node)
                #print "Visiting ", node
                if target.__class__==node.__class__ :
                    if target.lineno==node.lineno:
                        if repr(target)==repr(node):
                            return node
                for F in node._followedby:
                    if F not in visited:
                        return ifindreturn(target,F,visited)
                return None
            return ifindreturn(target,node,set())


        def recadd(self,var,val):
            if val not in self.objmaps[var]:
                #print "%s references %s"%(var,val)
                self.objmaps[var].add(val)
                for p in self.depmap[var]:
                    self.recadd(p,val)

        def merge(self,p,q):
            self.recadd(p,q)
            for o in self.objmaps[q]:
                self.recadd(p,o)
            self.depmap[q].add(p)
    
                            
        def handleGetattr(self, rhs,lhs):
            print "GetAttr", lhs, rhs
            pdb.set_trace()
            pass

        def handleName(self,rhs,lhs):
            #print "Assigning %s to %s"%(rhs,lhs)
            try:
                ST=stypes(rhs)
                T = set(i for i in ST if isObject(i))           
                if T:
                    #print ">> %s = %s"%(lhs._qualified_name, rhs._qualified_name)
                    self.merge(lhs._qualified_name,rhs._qualified_name)
            except:
                pass
            try:
                self.merge(lhs._qualified_name,rhs._qualified_name)
            except:
                pass


        def visitCallFunc(self, func):
            def handleName(rhs,lhs):
                self.handleName(rhs,lhs)
            #print ">>>>>>>>>", func
            if "_targets" in func.__dict__:
                for T in func._targets:
                    if 'self' in T._locals:
                        if T.name!="__init__":
                            for Type in T._locals['self']:
                                q_selffq="%s.__init__.self"%Type._qualified_name
                                p_selffq="%s.self"%T._qualified_name
                                self.merge(p_selffq,q_selffq)
                        for i in range(len(func.args)):
                            try:
                                param=pClass(T,T.argnames[i+1])
                                dispatch(locals(),func.args[i],param)
                            except:
                                pass
                    else:                            
                       #Add params
                        for i in range(len(func.args)):
                            try:                           
                                param=pClass(T,T.argnames[i])
                                dispatch(locals(),func.args[i],param)
                            except:
                                pass

        def visitAssign(self, ass):  
            if hasattr(ass,"_parent"):
                if len(ass.nodes)==1:
                    target=ass.nodes[0]
                    def doAssign(x,y):
                        def handleAssAttr(lhs,rhs):
                            def handleGetattr(rhs,lhs):
                                #q=pClass(rhs.expr,rhs.attrname)
                                rhs._qualified_name=rhs.expr._qualified_name+"."+rhs.attrname
                                self.handleName(rhs,lhs)
                            def handleCallFunc(rhs,lhs):
                                for T in rhs._targets:    
                                    
                                    #pdb.set_trace()
                                    #Add base field
                                    try:
                                        if T.name=="__init__":
                                            self.recadd(lhs._qualified_name,rhs._uid)                                        
                                            for i in range(len(rhs.args)):
                                                param=pClass(T,T.argnames[i+1])
                                                dispatch(LOCALS,rhs.args[i],param)
                                            self.recadd(T._qualified_name+"."+T.argnames[0], rhs._uid)
                                        else:
                                            if 'self' in T._locals:
                                                for Type in T._locals['self']:
                                                    q_selffq="%s.__init__.self"%Type._qualified_name
                                                    p_selffq="%s.self"%T._qualified_name
                                                    self.merge(p_selffq,q_selffq)
                                                for i in range(len(rhs.args)):
                                                    param=pClass(T,T.argnames[i+1])
                                                    dispatch(LOCALS,rhs.args[i],param)
                                            else:                            
                                                #Add params
                                                for i in range(len(rhs.args)):
                                                    param=pClass(T,T.argnames[i])
                                                    dispatch(LOCALS,rhs.args[i],param)
                                                #Handle return propagation
                                                for R in T._returns:
                                                    r=self.find_return(R,rhs)
                                                    if r:
                                                        dispatch(LOCALS,r.value,lhs)
                                                    else:
                                                        pass
                                                        #pdb.set_trace()
                                    except:
                                        pass
                            def handleDict(rhs,lhs):
                                self.recadd(lhs._qualified_name,rhs._uid)
                                pass
                            def handleList(rhs,lhs):
                                self.recadd(lhs._qualified_name,rhs._uid)
                                pass
                            def handleName(rhs,lhs):
                                self.handleName(rhs,lhs)
                            def handleSubscript(rhs,lhs):
                                self.handleName(rhs.expr,lhs)
                            param=pClass(lhs.expr,lhs.attrname)
                            LOCALS=locals()
                            #pdb.set_trace()
                            dispatch(LOCALS,rhs,param)
 
                        def handleAssTuple(lhs,rhs):
                            print "A"
                            for a,b in zip(lhs.getChildNodes(),rhs.getChildNodes()):
                                doAssign(a,b)
                        def handleSubscript(lhs,rhs):
                            handleAssName(lhs.expr,rhs)
                        def handleAssName(lhs,rhs):
                            def handleGetattr(rhs,lhs):
                                #q=pClass(rhs.expr,rhs.attrname)
                                try:
                                    rhs._qualified_name=rhs.expr._qualified_name+"."+rhs.attrname
                                    self.handleName(rhs,lhs)
                                except:
                                    pass
                            def handleCallFunc(rhs,lhs):
                                for T in rhs._targets:    
                                    #pdb.set_trace()
                                    #Add base field
                                    try:
                                        if T.name=="__init__":
                                            self.recadd(lhs._qualified_name,rhs._uid)                                        
                                            for i in range(len(rhs.args)):
                                                param=pClass(T,T.argnames[i+1])
                                                dispatch(LOCALS,rhs.args[i],param)
                                            self.recadd(T._qualified_name+"."+T.argnames[0], rhs._uid)
                                        else:
                                            if 'self' in T._locals:
                                                for Type in T._locals['self']:
                                                    q_selffq="%s.__init__.self"%Type._qualified_name
                                                    p_selffq="%s.self"%T._qualified_name
                                                    self.merge(p_selffq,q_selffq)
                                                for i in range(len(rhs.args)):
                                                    param=pClass(T,T.argnames[i+1])
                                                    dispatch(LOCALS,rhs.args[i],param)
                                            else:                            
                                                #Add params
                                                for i in range(len(rhs.args)):
                                                    param=pClass(T,T.argnames[i])
                                                    dispatch(LOCALS,rhs.args[i],param)
                                                #Handle return propagation
                                                for R in T._returns:
                                                    r=self.find_return(R,rhs)
                                                    if r:
                                                        dispatch(LOCALS,r.value,lhs)
                                                    else:
                                                        #pdb.set_trace()
                                                        pass
                                    except:
                                        pass
                                    else: #Handle return propagation
                                       for R in T._returns:
                                            r=self.find_return(R,rhs)
                                            if r:
                                                dispatch(LOCALS,r.value,lhs)
                                            else:
                                                pass
                                                #pdb.set_trace()
                            def handleList(rhs,lhs):
                                self.recadd(lhs._qualified_name,rhs._uid)
                                pass
                            def handleDict(rhs,lhs):
                                self.recadd(lhs._qualified_name,rhs._uid)
                                pass
                            def handleName(rhs,lhs):
                                self.handleName(rhs,lhs)
                            def handleSubscript(rhs,lhs):
                                self.handleName(rhs.expr,lhs)
                            #def default(*args):
                            #    pass
                            LOCALS=locals()
                            dispatch(LOCALS,rhs,lhs)
                        dispatch(locals(),x,y)
                    doAssign(target,ass.expr)
            pass


    walker=AnalysisVisitorAndersens()
    #compiler.walk(ast,walker)
    def visitFun(W):
        def myVisit(node):
            if node.__class__.__name__=="Assign":
                W.visitAssign(node)
            elif node.__class__.__name__=="CallFunc":
                W.visitCallFunc(node)
            else:
                pass
        return myVisit

    graph.visitNodes(visitFun(walker))
    for k,v in walker.objmaps.iteritems():
        print "%s -> %s"%(k,v) 
    #print walker.objCreations.keys()
    

analysis(graph)


