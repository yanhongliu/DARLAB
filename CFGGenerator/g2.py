import gc
import sys
import os

import analysis.source
import analysis.alias

def printRes(res):        
   for k,v in res.iteritems():
        print k
        for i,v2 in v.iteritems():
            print "    ",i
            print "            ",",".join([str(z) for z in v2])


fname=sys.argv[1]
session=analysis.source.AnalysisSession()
session.librarypath='analysis\\'
session.codepath=os.path.dirname(sys.argv[1])
session.simplify_files=True
sys.setrecursionlimit(400000)
vc=analysis.alias.visitCreator()
visit=vc.visitFunc()
graph=vc.graph
ast=session.processFile_to_CFG(fname,cfg_visitor=visit,only_source_ast=True,post_traversal=False) #computes graph

#print ast2string(ast)
print "Computed CFG!\n Slicing..."
gc.enable()
import cProfile


w=analysis.alias.TraceWorksetStorage(graph,maxallowed=1)
#storage=CStorageCompTrace(w,Print=False)
storage=analysis.alias.CStorageCompHyperTrace(w,Print=False)
#storage=analysis.alias.CStorage(Print=False)
#storage=Storage(Print=False)
#storage=ComboStorage(storage1,storage2)
goyal=analysis.alias.GoyalTrace(graph,w,storage,maxallowed=1)


#w=WorksetStorage()
#storage=CStorageComp(w,Print=False)
#storage=CStorageCompHyper(w,Print=False)
#storage=CStorage(Print=False)
#goyal=Goyal(graph,w,storage)


#cProfile.run("goyal.doAnalysis()")#,"%s.profile"%sys.argv[1])
goyal.doAnalysis()
res=storage.dump()
#printRes(res)

import pickle
F=open('%s.G'%fname,'w')
sys.setrecursionlimit(40000)
pickle.dump(res,F,pickle.HIGHEST_PROTOCOL)
F.close()

#goyal.S.printAliasSet("test3.py","test3.a")


