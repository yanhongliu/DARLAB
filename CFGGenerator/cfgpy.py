import analysis.source
import analysis.common
import os.path
import compiler
import pdb
from StringIO import StringIO

def visit(f,t):
    #visited CFG node t coming from f
    print "%d -> %d, lineno %s -> %s"%(f._uid,t._uid,f.lineno,t.lineno)
    x=analysis.common.ltype(t)
    if x:
        print "\t%s : %s"%(`t`,analysis.common.lname(x[0]))
    pass

ast=compiler.parseFile("testout.py")
session=analysis.source.AnalysisSession()
session.librarypath='analysis\\'
session.path='.'
ast=session.processAST_to_CFG(ast,cfg_visitor=visit,only_source_ast=False,post_traversal=False)
