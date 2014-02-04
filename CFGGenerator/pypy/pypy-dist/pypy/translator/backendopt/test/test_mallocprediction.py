import py
from pypy.translator.translator import TranslationContext
from pypy.translator.backendopt import inline
from pypy.translator.backendopt.all import backend_optimizations
from pypy.translator.translator import TranslationContext, graphof
from pypy.rpython.llinterp import LLInterpreter
from pypy.objspace.flow.model import checkgraph, flatten, Block
from pypy.conftest import option
import sys

from pypy.translator.backendopt.mallocprediction import *

def rtype(fn, signature):
    t = TranslationContext()
    t.buildannotator().build_types(fn, signature)
    t.buildrtyper().specialize()
    graph = graphof(t, fn)
    if option.view:
        t.view()
    return t, graph
    

def check_inlining(t, graph, args, result):
    callgraph, caller_candidates = find_malloc_removal_candidates(t, t.graphs)
    nice_callgraph = {}
    for caller, callee in callgraph:
        nice_callgraph.setdefault(caller, {})[callee] = True
    inline_and_remove(t, t.graphs)
    if option.view:
        t.view()
    interp = LLInterpreter(t.rtyper)
    res = interp.eval_graph(graph, args)
    assert res == result
    return nice_callgraph, caller_candidates

def test_fn():
    class A:
        pass
    class B(A):
        pass
    def g(a, b, i):
        a.b = b
        b.i = i
        return a.b.i
    def h(x):
        return x + 42
    def fn(i):
        a = A()
        b = B()
        x = h(i)
        return g(a, b, x)
    t, graph = rtype(fn, [int])
    callgraph, caller_candidates = check_inlining(t, graph, [0], 42)
    assert caller_candidates == {graph: True}
    assert len(callgraph) == 1
    ggraph = graphof(t, g)
    assert callgraph[graph] == {ggraph: True}

def test_multiple_calls():
    class A:
        pass
    class B(A):
        pass
    def g2(b, i): 
        b.i = h(i)
    def g1(a, b, i):
        a.b = b
        g2(b, h(i))
        return a.b.i
    def h(x):
        return x + 42
    def fn(i):
        a = A()
        b = B()
        x = h(i)
        return g1(a, b, x)
    t, graph = rtype(fn, [int])
    callgraph, caller_candidates = check_inlining(t, graph, [0], 3 * 42)
    print callgraph
    assert caller_candidates == {graph: True}
    assert len(callgraph) == 1
    g1graph = graphof(t, g1)
    g2graph = graphof(t, g2)
    assert callgraph[graph] == {g1graph: True}
    callgraph, caller_candidates = check_inlining(t, graph, [0], 3 * 42)
    assert callgraph[graph] == {g2graph: True}
    
def test_indirect_call():
    class A(object):
        pass
    def f1(a, i):
        return a.x
    def f2(a, i):
        return a.x + 1
    def g1(a, i):
        return a
    def g2(a, i):
        return None
    def f(i):
        a1 = A()
        a2 = A()
        a1.x = 1
        a2.x = 2
        if i:
            f = f1
            g = g1
        else:
            f = f2
            g = g2
        x = f(a1, 0)
        a0 = g(a2, 1)
        if a0 is not None:
            return 43
        else:
            return 42
    t, graph = rtype(f, [int])
    callgraph, caller_candidate = check_inlining(t, graph, [0], 42)
    assert caller_candidate == {}

def test_pystone():
    from pypy.translator.goal.targetrpystonex import make_target_definition
    entrypoint, _, _ = make_target_definition(10)
    def heuristic(graph):
        for block in graph.iterblocks():
            for op in block.operations:
                if op.opname in ('malloc',):
                    return inline.inlining_heuristic(graph)
        return sys.maxint, False
    # does not crash
    t, graph = rtype(entrypoint, [int])
    total0 = preparation(t, t.graphs, heuristic=heuristic)
    total = clever_inlining_and_malloc_removal(t)
    assert total0 + total == 10

def test_richards():
    py.test.skip("Unsure if this makes any sense any more")
    from pypy.translator.goal.richards import entry_point
    t, graph = rtype(entry_point, [int])
    total0 = preparation(t, t.graphs)
    total = clever_inlining_and_malloc_removal(t)
    assert total0 + total == 9
