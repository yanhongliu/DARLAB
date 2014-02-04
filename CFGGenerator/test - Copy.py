import analysis.source
import analysis.common
import os.path
import compiler
import pdb
from StringIO import StringIO
import pyunparse
from StringIO import StringIO

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

  
def visit(f,t):
    #visited CFG node t coming from f
    global graph
    #pdb.set_trace()
    noadd=False
    if hasattr(t,"_parent") and isinstance(t._parent,compiler.ast.Function):
      #pdb.set_trace()
      z=f
      while (True):
        if t.getChildren()[-1]==z:
          noadd=True
          break
        if hasattr(z,"_parent"):
          z=z._parent
        else:
          break
    if not noadd:
      graph.addedge(f,t)


def  computeinitialslice(ast):
  lines=set(l.strip() for l in ast2string(ast).split('\n'))
  def F(f,t):
      global graphslice
      res=truncate(ast2string(f))
      
      if (len(res)>3 and res[-1]=="\n") or res.strip() in lines:
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

ast=compiler.parseFile("testsmall.py")
session=analysis.source.AnalysisSession()
session.librarypath='analysis\\'
session.path='.'
ast=session.processAST_to_CFG(ast,cfg_visitor=visit,only_source_ast=True,post_traversal=False) #computes graph
graph.visitEdges(computeinitialslice(ast)) #computes graphslice      
graphslice.visitEdges(slice) #computes newslice
#graph.visitEdges(printnode("graph: "))
#graphslice.visitEdges(printnode("graphslice: "))
newslice.visitEdges(printnode("newslice: "))

L.sort()
for l in L:
  print l
#print ast2string(ast)
