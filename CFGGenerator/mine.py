import analysis.source
import analysis.common
import os.path
import compiler
import sys
import inspect
import pdb
from StringIO import StringIO
import pyunparse
from StringIO import StringIO
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
  def addedge(self,f,t):
    if not self.F:
      self.start=f
    if f not in self.F:
      self.F[f]=set()
    self.F[f].add(t)
    if t not in self.B:
      self.B[t]=set()
    self.B[t].add(f)
  def visitEdges(self,visitor):
      for f,S in self.F.iteritems():
        for t in S:
          visitor(f,t)
  def dfs(self,action,start=None,stopcondition=lambda f,t: True,pre=False):
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


def printnode(prefix):
  def F(f,t):
    global L
    info= "%d -> %d, lineno %s -> %s"%(f._uid,t._uid,f.lineno,t.lineno)
    res=truncate(ast2string(f))
    res=res.replace("\n"," \\n ")
    #truncate(str(f))
    L.append(prefix + info + " f: " + res + " \n         " + truncate(str(f)))
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

from analysis.plugins.simplify import simplify

#print s
#sys.exit(0)
fname=sys.argv[1]
session=analysis.source.AnalysisSession()
session.librarypath='analysis\\'
ast=compiler.parseFile(fname)#session.simplify(fname))
ast=session.processAST_to_CFG(ast,cfg_visitor=visit,only_source_ast=True,post_traversal=False) #computes graph
print "Computed CFG!\n Slicing..."
#ast=session.process_file("chunk.py")
#sys.exit(0)
graph.visitEdges(computeinitialslice(ast)) #computes graphslice      
graphslice.visitEdges(slice) #computes newslice

#graph.visitEdges(printnode("graph: "))
#graphslice.visitEdges(printnode("graphslice: "))
print "Done Slicing!"

print "Saving Slice!"
session.save(newslice,fname+".cache")
print "Computing DOT Graph!"
import analysis.pydot
G=analysis.pydot.Dot(graph_type="graph")
newslice.visitEdges(graphvizGenerator(G))
print "Computed Graph. Saving SVG!"
#print G.to_string()
#pdb.set_trace()
G.write_svg(fname+".svg")
#import analysis.dotviewer.graphclient
#analysis.dotviewer.graphclient.display_dot_file(fname+".plain")
#print "Done"

def zog():
    def dispatch(namespace,*args):
        name=args[0].__class__.__name__
        if "handle%s"%name in namespace:
            namespace["handle%s"%name](*args)
        elif "default" in namespace:
            namespace["default"](*args)
        else:
            print >>Debug(), "Unhandled class %s"%name

    def set_values(sets):
        res=set()
        if isinstance(sets,set):
            for s in sets:
                if s.__class__.__name__=="Reference":
                    if hasattr(s,"values"):
                        for v in s.values:
                            res.add(v)
                else:
                    r=set_values(s)
                    res|=r
        else:
            container=sets
            if hasattr(container,"_contexts"):
                for v_b in container._contexts.values():
                    for s_v_b in v_b:
                        if hasattr(s_v_b,"values"):
                            for v in s_v_b.values:
                                res.add(v)
        return res


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





    class AnalysisVisitorGetCreationSites(ASTVisitor):

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
        def visitAssign(self, ass):  
            if hasattr(ass,"_parent"):
                if len(ass.nodes)==1:
                    target=ass.nodes[0]
                    def doAssign(x,y):
                        def handleAssTuple(lhs,rhs):
                            for a,b in zip(lhs.getChildNodes(),rhs.getChildNodes()):
                                doAssign(a,b)
                        def handleAssName(lhs,rhs):
                            def handleCallFunc(rhs,lhs):
                                T = set(i for i in stypes(rhs) if isObject(i))
                                for t in T:
                                    self.count+=1
                                    self.objCreations[lhs].add(self.count)
                                    self.objTypes[self.count] |= T
                                pdb.set_trace()
                            def handleList(rhs,lhs):
                                self.count+=1
                                self.objCreations[lhs].add(self.count)
                                self.objTypes[self.count] |= stypes(rhs)
                            def default(*args):
                                pass
                                #pdb.set_trace()
                            dispatch(locals(),rhs,lhs._qualified_name)
                        dispatch(locals(),x,y)


                    doAssign(target,ass.expr)
            pass


    def walk_cfgnode(f,t):
        if isinstance(f,compiler.ast.Assign):
            compiler.walk(f,AnalysisVisitorGetCreationSites())

    #newslice.visitEdges(walk_cfgnode)

    walker=AnalysisVisitorGetCreationSites()
    compiler.walk(ast,walker)
    print walker.objCreations.keys()


#L.sort()
#for l in L:
#  print l

#print len(L)
#print ast2string(ast)

