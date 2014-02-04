
import autopath
import py.test
import sys
from pypy import conftest
from pypy.tool.udir import udir

from pypy.annotation import model as annmodel
from pypy.annotation.annrpython import RPythonAnnotator as _RPythonAnnotator
from pypy.translator.translator import graphof as tgraphof
from pypy.annotation import policy
from pypy.annotation import specialize
from pypy.annotation.listdef import ListDef, TooLateForChange
from pypy.annotation.dictdef import DictDef
from pypy.objspace.flow.model import *
from pypy.rlib.rarithmetic import r_uint, base_int, r_longlong, r_ulonglong
from pypy.rlib.rarithmetic import r_singlefloat
from pypy.rlib import objectmodel
from pypy.objspace.flow.objspace import FlowObjSpace

from pypy.translator.test import snippet

def graphof(a, func):
    return tgraphof(a.translator, func)

def listitem(s_list):
    assert isinstance(s_list, annmodel.SomeList)
    return s_list.listdef.listitem.s_value

def somelist(s_type=annmodel.SomeObject()):
    return annmodel.SomeList(ListDef(None, s_type))

def dictkey(s_dict):
    assert isinstance(s_dict, annmodel.SomeDict)
    return s_dict.dictdef.dictkey.s_value

def dictvalue(s_dict):
    assert isinstance(s_dict, annmodel.SomeDict)
    return s_dict.dictdef.dictvalue.s_value

def somedict(s_key=annmodel.SomeObject(), s_value=annmodel.SomeObject()):
    return annmodel.SomeDict(DictDef(None, s_key, s_value))


class TestAnnotateTestCase:
    def setup_class(cls): 
        cls.space = FlowObjSpace() 

    def teardown_method(self, meth):
        assert annmodel.s_Bool == annmodel.SomeBool()

    class RPythonAnnotator(_RPythonAnnotator):
        def build_types(self, *args):
            s = _RPythonAnnotator.build_types(self, *args)
            if conftest.option.view:
                self.translator.view()
            return s

    def make_fun(self, func):
        import inspect
        try:
            func = func.im_func
        except AttributeError:
            pass
        name = func.func_name
        funcgraph = self.space.build_flow(func)
        funcgraph.source = inspect.getsource(func)
        return funcgraph

    def test_simple_func(self):
        """
        one test source:
        def f(x):
            return x+1
        """
        x = Variable("x")
        result = Variable("result")
        op = SpaceOperation("add", [x, Constant(1)], result)
        block = Block([x])
        fun = FunctionGraph("f", block)
        block.operations.append(op)
        block.closeblock(Link([result], fun.returnblock))
        a = self.RPythonAnnotator()
        a.addpendingblock(fun, fun.startblock, [annmodel.SomeInteger()])
        a.complete()
        assert a.gettype(fun.getreturnvar()) == int

    def test_while(self):
        """
        one test source:
        def f(i):
            while i > 0:
                i = i - 1
            return i
        """
        i1 = Variable("i1")
        i2 = Variable("i2")
        i3 = Variable("i3")
        conditionres = Variable("conditionres")
        conditionop = SpaceOperation("gt", [i1, Constant(0)], conditionres)
        decop = SpaceOperation("add", [i2, Constant(-1)], i3)
        headerblock = Block([i1])
        whileblock = Block([i2])

        fun = FunctionGraph("f", headerblock)
        headerblock.operations.append(conditionop)
        headerblock.exitswitch = conditionres
        headerblock.closeblock(Link([i1], fun.returnblock, False),
                               Link([i1], whileblock, True))
        whileblock.operations.append(decop)
        whileblock.closeblock(Link([i3], headerblock))

        a = self.RPythonAnnotator()
        a.addpendingblock(fun, fun.startblock, [annmodel.SomeInteger()])
        a.complete()
        assert a.gettype(fun.getreturnvar()) == int

    def test_while_sum(self):
        """
        one test source:
        def f(i):
            sum = 0
            while i > 0:
                sum = sum + i
                i = i - 1
            return sum
        """
        i1 = Variable("i1")
        i2 = Variable("i2")
        i3 = Variable("i3")
        i4 = Variable("i4")
        sum2 = Variable("sum2")
        sum3 = Variable("sum3")
        sum4 = Variable("sum4")

        conditionres = Variable("conditionres")
        conditionop = SpaceOperation("gt", [i2, Constant(0)], conditionres)
        decop = SpaceOperation("add", [i3, Constant(-1)], i4)
        addop = SpaceOperation("add", [i3, sum3], sum4)
        startblock = Block([i1])
        headerblock = Block([i2, sum2])
        whileblock = Block([i3, sum3])

        fun = FunctionGraph("f", startblock)
        startblock.closeblock(Link([i1, Constant(0)], headerblock))
        headerblock.operations.append(conditionop)
        headerblock.exitswitch = conditionres
        headerblock.closeblock(Link([sum2], fun.returnblock, False),
                               Link([i2, sum2], whileblock, True))
        whileblock.operations.append(addop)
        whileblock.operations.append(decop)
        whileblock.closeblock(Link([i4, sum4], headerblock))

        a = self.RPythonAnnotator()
        a.addpendingblock(fun, fun.startblock, [annmodel.SomeInteger()])
        a.complete()
        assert a.gettype(fun.getreturnvar()) == int

    def test_f_calls_g(self):
        a = self.RPythonAnnotator()
        s = a.build_types(f_calls_g, [int])
        # result should be an integer
        assert s.knowntype == int

    def test_lists(self):
        a = self.RPythonAnnotator()
        end_cell = a.build_types(snippet.poor_man_rev_range, [int])
        # result should be a list of integers
        assert listitem(end_cell).knowntype == int

    def test_factorial(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.factorial, [int])
        # result should be an integer
        assert s.knowntype == int

    def test_factorial2(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.factorial2, [int])
        # result should be an integer
        assert s.knowntype == int

    def test_build_instance(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.build_instance, [])
        # result should be a snippet.C instance
        assert isinstance(s, annmodel.SomeInstance)
        assert s.classdef == a.bookkeeper.getuniqueclassdef(snippet.C)

    def test_set_attr(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.set_attr, [])
        # result should be an integer
        assert s.knowntype == int

    def test_merge_setattr(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.merge_setattr, [int])
        # result should be an integer
        assert s.knowntype == int

    def test_inheritance1(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.inheritance1, [])
        # result should be exactly:
        assert s == annmodel.SomeTuple([
                                a.bookkeeper.immutablevalue(()),
                                annmodel.SomeInteger()
                                ])

    def test_inheritance2(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet._inheritance_nonrunnable, [])
        # result should be exactly:
        assert s == annmodel.SomeTuple([
                                annmodel.SomeInteger(),
                                annmodel.SomeObject()
                                ])

    def test_poor_man_range(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.poor_man_range, [int])
        # result should be a list of integers
        assert listitem(s).knowntype == int

    def test_methodcall1(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet._methodcall1, [int])
        # result should be a tuple of (C, positive_int)
        assert s.knowntype == tuple
        assert len(s.items) == 2
        s0 = s.items[0]
        assert isinstance(s0, annmodel.SomeInstance)
        assert s0.classdef == a.bookkeeper.getuniqueclassdef(snippet.C)
        assert s.items[1].knowntype == int
        assert s.items[1].nonneg == True

    def test_classes_methodcall1(self):
        a = self.RPythonAnnotator()
        a.build_types(snippet._methodcall1, [int])
        # the user classes should have the following attributes:
        getcdef = a.bookkeeper.getuniqueclassdef
        assert getcdef(snippet.F).attrs.keys() == ['m']
        assert getcdef(snippet.G).attrs.keys() == ['m2']
        assert getcdef(snippet.H).attrs.keys() == ['attr'] 
        assert getcdef(snippet.H).about_attribute('attr') == (
                          a.bookkeeper.immutablevalue(1))

    def DISABLED_test_knownkeysdict(self):
        # disabled, SomeDict() is now a general {s_key: s_value} dict
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.knownkeysdict, [int])
        # result should be an integer
        assert s.knowntype == int

    def test_generaldict(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.generaldict, [str, int, str, int])
        # result should be an integer
        assert s.knowntype == int

    def test_somebug1(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet._somebug1, [int])
        # result should be a built-in method
        assert isinstance(s, annmodel.SomeBuiltin)

    def test_with_init(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.with_init, [int])
        # result should be an integer
        assert s.knowntype == int

    def test_with_more_init(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.with_more_init, [int, bool])
        # the user classes should have the following attributes:
        getcdef = a.bookkeeper.getuniqueclassdef
        # XXX on which class should the attribute 'a' appear?  We only
        #     ever flow WithInit.__init__ with a self which is an instance
        #     of WithMoreInit, so currently it appears on WithMoreInit.
        assert getcdef(snippet.WithMoreInit).about_attribute('a') == (
                          annmodel.SomeInteger())
        assert getcdef(snippet.WithMoreInit).about_attribute('b') == (
                          annmodel.SomeBool())

    def test_global_instance(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.global_instance, [])
        # currently this returns the constant 42.
        # XXX not sure this is the best behavior...
        assert s == a.bookkeeper.immutablevalue(42)

    def test_call_five(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.call_five, [])
        # returns should be a list of constants (= 5)
        assert listitem(s) == a.bookkeeper.immutablevalue(5)

    def test_call_five_six(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.call_five_six, [])
        # returns should be a list of positive integers
        assert listitem(s) == annmodel.SomeInteger(nonneg=True)

    def test_constant_result(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.constant_result, [])
        #a.translator.simplify()
        # must return "yadda"
        assert s == a.bookkeeper.immutablevalue("yadda")
        graphs = a.translator.graphs
        assert len(graphs) == 2
        assert graphs[0].func is snippet.constant_result
        assert graphs[1].func is snippet.forty_two
        a.simplify()
        #a.translator.view()

    def test_flow_type_info(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.flow_type_info, [object])
        a.simplify()
        #a.translator.view()
        assert s.knowntype == int

    def test_flow_type_info_2(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.flow_type_info,
                          [annmodel.SomeInteger(nonneg=True)])
        # this checks that isinstance(i, int) didn't lose the
        # actually more precise information that i is non-negative
        assert s == annmodel.SomeInteger(nonneg=True)

    def test_flow_usertype_info(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.flow_usertype_info, [object])
        #a.translator.view()
        assert isinstance(s, annmodel.SomeInstance)
        assert s.classdef == a.bookkeeper.getuniqueclassdef(snippet.WithInit)

    def test_flow_usertype_info2(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.flow_usertype_info, [snippet.WithMoreInit])
        #a.translator.view()
        assert isinstance(s, annmodel.SomeInstance)
        assert s.classdef == a.bookkeeper.getuniqueclassdef(snippet.WithMoreInit)

    def test_flow_identity_info(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.flow_identity_info, [object, object])
        a.simplify()
        #a.translator.view()
        assert s == a.bookkeeper.immutablevalue((None, None))

    def test_mergefunctions(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.mergefunctions, [int])
        # the test is mostly that the above line hasn't blown up
        # but let's at least check *something*
        assert isinstance(s, annmodel.SomePBC)

    def test_func_calls_func_which_just_raises(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.funccallsex, [])
        # the test is mostly that the above line hasn't blown up
        # but let's at least check *something*
        #self.assert_(isinstance(s, SomeCallable))

    def test_tuple_unpack_from_const_tuple_with_different_types(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.func_arg_unpack, [])
        assert isinstance(s, annmodel.SomeInteger) 
        assert s.const == 3 

    def test_pbc_attr_preserved_on_instance(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.preserve_pbc_attr_on_instance, [bool])
        #a.simplify()
        #a.translator.view()
        assert s == annmodel.SomeInteger(nonneg=True) 
        #self.assertEquals(s.__class__, annmodel.SomeInteger) 

    def test_pbc_attr_preserved_on_instance_with_slots(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.preserve_pbc_attr_on_instance_with_slots,
                          [bool])
        assert s == annmodel.SomeInteger(nonneg=True) 

    def test_is_and_knowntype_data(self): 
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.is_and_knowntype, [str])
        #a.simplify()
        #a.translator.view()
        assert s == a.bookkeeper.immutablevalue(None)

    def test_isinstance_and_knowntype_data(self): 
        a = self.RPythonAnnotator()
        x = a.bookkeeper.immutablevalue(snippet.apbc)
        s = a.build_types(snippet.isinstance_and_knowntype, [x]) 
        #a.simplify()
        #a.translator.view()
        assert s == x

    def test_somepbc_simplify(self):
        a = self.RPythonAnnotator()
        # this example used to trigger an AssertionError
        a.build_types(snippet.somepbc_simplify, [])

    def test_builtin_methods(self):
        a = self.RPythonAnnotator()
        iv = a.bookkeeper.immutablevalue
        # this checks that some built-in methods are really supported by
        # the annotator (it doesn't check that they operate property, though)
        for example, methname, s_example in [
            ('', 'join',    annmodel.SomeString()),
            ([], 'append',  somelist()), 
            ([], 'extend',  somelist()),           
            ([], 'reverse', somelist()),
            ([], 'insert',  somelist()),
            ([], 'pop',     somelist()),
            ]:
            constmeth = getattr(example, methname)
            s_constmeth = iv(constmeth)
            assert isinstance(s_constmeth, annmodel.SomeBuiltin)
            s_meth = s_example.getattr(iv(methname))
            assert isinstance(s_constmeth, annmodel.SomeBuiltin)

    def test_simple_slicing0(self):
        a = self.RPythonAnnotator()
        a.build_types(snippet.simple_slice, [list])
        g = graphof(a, snippet.simple_slice)
        for block in g.iterblocks():
            for op in block.operations:
                if op.opname == "newslice":
                    assert isinstance(a.binding(op.result),
                                      annmodel.SomeSlice)

    def test_simple_slicing(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.simple_slice, [list])
        assert isinstance(s, annmodel.SomeList)

    def test_simple_iter_list(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.simple_iter, [list])
        assert isinstance(s, annmodel.SomeIterator)
        
    def test_simple_iter_next(self):
        def f(x):
            i = iter(range(x))
            return i.next()
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert isinstance(s, annmodel.SomeInteger)

    def test_simple_iter_dict(self):
        a = self.RPythonAnnotator()
        t = somedict(annmodel.SomeInteger(), annmodel.SomeInteger())
        s = a.build_types(snippet.simple_iter, [t])
        assert isinstance(s, annmodel.SomeIterator)

    def test_simple_zip(self):
        a = self.RPythonAnnotator()
        x = somelist(annmodel.SomeInteger())
        y = somelist(annmodel.SomeString())
        s = a.build_types(snippet.simple_zip, [x,y])
        assert s.knowntype == list
        assert listitem(s).knowntype == tuple
        assert listitem(s).items[0].knowntype == int
        assert listitem(s).items[1].knowntype == str
        
    def test_dict_copy(self):
        a = self.RPythonAnnotator()
        t = somedict(annmodel.SomeInteger(), annmodel.SomeInteger())
        s = a.build_types(snippet.dict_copy, [t])
        assert isinstance(dictkey(s), annmodel.SomeInteger)
        assert isinstance(dictvalue(s), annmodel.SomeInteger)

    def test_dict_update(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.dict_update, [int])
        assert isinstance(dictkey(s), annmodel.SomeInteger)
        assert isinstance(dictvalue(s), annmodel.SomeInteger)

        a = self.RPythonAnnotator()
        s = a.build_types(snippet.dict_update, [str])
        assert not isinstance(dictkey(s), annmodel.SomeString)
        assert not isinstance(dictvalue(s), annmodel.SomeString)

    def test_dict_keys(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.dict_keys, [])
        assert isinstance(listitem(s), annmodel.SomeString)

    def test_dict_keys2(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.dict_keys2, [])
        assert not isinstance(listitem(s), annmodel.SomeString)

    def test_dict_values(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.dict_values, [])
        assert isinstance(listitem(s), annmodel.SomeString)
    
    def test_dict_values2(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.dict_values2, [])
        assert not isinstance(listitem(s), annmodel.SomeString)

    def test_dict_items(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.dict_items, [])
        assert isinstance(listitem(s), annmodel.SomeTuple)
        s_key, s_value = listitem(s).items
        assert isinstance(s_key, annmodel.SomeString)
        assert isinstance(s_value, annmodel.SomeInteger)

    def test_dict_setdefault(self):
        a = self.RPythonAnnotator()
        def f():
            d = {}
            d.setdefault('a', 2)
            d.setdefault('a', -3)
            return d
        s = a.build_types(f, [])
        assert isinstance(s, annmodel.SomeDict)
        assert isinstance(dictkey(s), annmodel.SomeString)
        assert isinstance(dictvalue(s), annmodel.SomeInteger)
        assert not dictvalue(s).nonneg
        
    def test_exception_deduction(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.exception_deduction, [])
        assert isinstance(s, annmodel.SomeInstance)
        assert s.classdef is a.bookkeeper.getuniqueclassdef(snippet.Exc)
        
    def test_exception_deduction_we_are_dumb(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.exception_deduction_we_are_dumb, [])
        assert isinstance(s, annmodel.SomeInstance)
        assert s.classdef is a.bookkeeper.getuniqueclassdef(snippet.Exc)
        
    def test_nested_exception_deduction(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.nested_exception_deduction, [])
        assert isinstance(s, annmodel.SomeTuple)
        assert isinstance(s.items[0], annmodel.SomeInstance)
        assert isinstance(s.items[1], annmodel.SomeInstance)
        assert s.items[0].classdef is a.bookkeeper.getuniqueclassdef(snippet.Exc)
        assert s.items[1].classdef is a.bookkeeper.getuniqueclassdef(snippet.Exc2)

    def test_exc_deduction_our_exc_plus_others(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.exc_deduction_our_exc_plus_others, [])
        assert isinstance(s, annmodel.SomeInteger)

    def test_exc_deduction_our_excs_plus_others(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.exc_deduction_our_excs_plus_others, [])
        assert isinstance(s, annmodel.SomeInteger)

    def test_operation_always_raising(self):
        def operation_always_raising(n):
            lst = []
            try:
                return lst[n]
            except IndexError:
                return 24
        a = self.RPythonAnnotator()
        s = a.build_types(operation_always_raising, [int])
        assert s == a.bookkeeper.immutablevalue(24)

    def test_slice_union(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.slice_union, [int])
        assert isinstance(s, annmodel.SomeSlice)

    def test_bltin_code_frame_confusion(self):
        a = self.RPythonAnnotator()
        a.build_types(snippet.bltin_code_frame_confusion,[])
        f_flowgraph = graphof(a, snippet.bltin_code_frame_f)
        g_flowgraph = graphof(a, snippet.bltin_code_frame_g)
        # annotator confused by original bltin code/frame setup, we just get SomeObject here
        assert a.binding(f_flowgraph.getreturnvar()).__class__ is annmodel.SomeObject
        assert a.binding(g_flowgraph.getreturnvar()).__class__ is annmodel.SomeObject

    def test_bltin_code_frame_reorg(self):
        a = self.RPythonAnnotator()
        a.build_types(snippet.bltin_code_frame_reorg,[])
        f_flowgraph = graphof(a, snippet.bltin_code_frame_f)
        g_flowgraph = graphof(a, snippet.bltin_code_frame_g)
        assert isinstance(a.binding(f_flowgraph.getreturnvar()),
                            annmodel.SomeInteger)
        assert isinstance(a.binding(g_flowgraph.getreturnvar()),
                          annmodel.SomeString)

    def test_propagation_of_fresh_instances_through_attrs(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.propagation_of_fresh_instances_through_attrs, [int])
        assert s is not None

    def test_propagation_of_fresh_instances_through_attrs_rec_0(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.make_r, [int])
        Rdef = a.bookkeeper.getuniqueclassdef(snippet.R)
        assert s.classdef == Rdef
        assert Rdef.attrs['r'].s_value.classdef == Rdef
        assert Rdef.attrs['n'].s_value.knowntype == int
        assert Rdef.attrs['m'].s_value.knowntype == int
    
        
    def test_propagation_of_fresh_instances_through_attrs_rec_eo(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.make_eo, [int])
        assert s.classdef == a.bookkeeper.getuniqueclassdef(snippet.B)
        Even_def = a.bookkeeper.getuniqueclassdef(snippet.Even)
        Odd_def = a.bookkeeper.getuniqueclassdef(snippet.Odd)
        assert listitem(Even_def.attrs['x'].s_value).classdef == Odd_def
        assert listitem(Even_def.attrs['y'].s_value).classdef == Even_def
        assert listitem(Odd_def.attrs['x'].s_value).classdef == Even_def
        assert listitem(Odd_def.attrs['y'].s_value).classdef == Odd_def

    def test_flow_rev_numbers(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.flow_rev_numbers, [int])
        assert s.knowntype == int
        assert not s.is_constant() # !

    def test_methodcall_is_precise(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.methodcall_is_precise, [bool])
        getcdef = a.bookkeeper.getuniqueclassdef
        assert 'x' not in getcdef(snippet.CBase).attrs
        assert (getcdef(snippet.CSub1).attrs['x'].s_value ==
                a.bookkeeper.immutablevalue(42))
        assert (getcdef(snippet.CSub2).attrs['x'].s_value ==
                a.bookkeeper.immutablevalue('world'))
        assert s == a.bookkeeper.immutablevalue(42)

    def test_call_star_args(self):
        a = self.RPythonAnnotator(policy=policy.AnnotatorPolicy())
        s = a.build_types(snippet.call_star_args, [int])
        assert s.knowntype == int

    def test_call_star_args_multiple(self):
        a = self.RPythonAnnotator(policy=policy.AnnotatorPolicy())
        s = a.build_types(snippet.call_star_args_multiple, [int])
        assert s.knowntype == int

    def test_class_spec(self):
        a = self.RPythonAnnotator(policy=policy.AnnotatorPolicy())
        s = a.build_types(snippet.class_spec, [])
        assert s.items[0].knowntype == int
        assert s.items[1].knowntype == str

    def test_class_spec_confused(self):
        x = snippet.PolyStk()
        def f():
            return x
        a = self.RPythonAnnotator(policy=policy.AnnotatorPolicy())
        py.test.raises(Exception, a.build_types, f, [])

    def test_exception_deduction_with_raise1(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.exception_deduction_with_raise1, [bool])
        assert isinstance(s, annmodel.SomeInstance)
        assert s.classdef is a.bookkeeper.getuniqueclassdef(snippet.Exc)


    def test_exception_deduction_with_raise2(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.exception_deduction_with_raise2, [bool])
        assert isinstance(s, annmodel.SomeInstance)
        assert s.classdef is a.bookkeeper.getuniqueclassdef(snippet.Exc)

    def test_exception_deduction_with_raise3(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.exception_deduction_with_raise3, [bool])
        assert isinstance(s, annmodel.SomeInstance)
        assert s.classdef is a.bookkeeper.getuniqueclassdef(snippet.Exc)

    def test_type_is(self):
        class C(object):
            pass
        def f(x):
            if type(x) is C:
                return x
            raise Exception
        a = self.RPythonAnnotator()
        s = a.build_types(f, [object])
        assert s.classdef is a.bookkeeper.getuniqueclassdef(C)

    def test_ann_assert(self):
        def assert_(x):
            assert x,"XXX"
        a = self.RPythonAnnotator()
        s = a.build_types(assert_, [int])
        assert s.const is None

    def test_string_and_none(self):
        def f(n):
            if n:
                return 'y'
            else:
                return 'n'
        def g(n):
            if n:
                return 'y'
            else:
                return None
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])
        assert s.knowntype == str
        assert not s.can_be_None
        s = a.build_types(g, [bool])
        assert s.knowntype == str
        assert s.can_be_None

    def test_implicit_exc(self):
        def f(l):
            try:
                l[0]
            except (KeyError, IndexError),e:
                return e
            return None

        a = self.RPythonAnnotator()
        s = a.build_types(f, [list])
        assert s.classdef is a.bookkeeper.getuniqueclassdef(IndexError)  # KeyError ignored because l is a list

    def test_overrides(self):
        import sys
        excs = []
        def record_exc(e):
            """NOT_RPYTHON"""
            excs.append(sys.exc_info)
        record_exc._annspecialcase_ = "override:record_exc"
        def g():
            pass
        def f():
            try:
                g()
            except Exception, e:
                record_exc(e)
        class MyAnnotatorPolicy(policy.AnnotatorPolicy):

            def override__record_exc(pol, s_e):
                return a.bookkeeper.immutablevalue(None)
            
        a = self.RPythonAnnotator(policy=MyAnnotatorPolicy())
        s = a.build_types(f, [])
        assert s.const is None

    def test_freeze_protocol(self):
        class Stuff:
            def __init__(self, flag):
                self.called = False
                self.flag = flag
            def _freeze_(self):
                self.called = True
                return self.flag
        myobj = Stuff(True)
        a = self.RPythonAnnotator()
        s = a.build_types(lambda: myobj, [])
        assert myobj.called
        assert isinstance(s, annmodel.SomePBC)
        assert s.const == myobj
        myobj = Stuff(False)
        a = self.RPythonAnnotator()
        s = a.build_types(lambda: myobj, [])
        assert myobj.called
        assert isinstance(s, annmodel.SomeInstance)
        assert s.classdef is a.bookkeeper.getuniqueclassdef(Stuff)

    def test_circular_mutable_getattr(self):
        class C:
            pass
        c = C()
        c.x = c
        def f():
            return c.x
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert isinstance(s, annmodel.SomeInstance)
        assert s.classdef == a.bookkeeper.getuniqueclassdef(C)

    def test_circular_list_type(self):
        def f(n):
            lst = []
            for i in range(n):
                lst = [lst]
            return lst
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert listitem(s) == s

    def test_harmonic(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.harmonic, [int])
        assert s.knowntype == float
        # check that the list produced by range() is not mutated or resized
        for s_value in a.bindings.values():
            if isinstance(s_value, annmodel.SomeList):
                assert not s_value.listdef.listitem.resized
                assert not s_value.listdef.listitem.mutated
                assert s_value.listdef.listitem.range_step

    def test_bool(self):
        def f(a,b):
            return bool(a) or bool(b)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int,list])
        assert s.knowntype == bool

    def test_float(self):
        def f(n):
            return float(n)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert s.knowntype == float

    def test_r_uint(self):
        def f(n):
            return n + constant_unsigned_five
        a = self.RPythonAnnotator()
        s = a.build_types(f, [r_uint])
        assert s == annmodel.SomeInteger(nonneg = True, unsigned = True)

    def test_large_unsigned(self):
        large_constant = sys.maxint * 2 + 1 # 0xFFFFFFFF on 32-bit platforms
        def f():
            return large_constant
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s.knowntype == r_uint

    def test_pbc_getattr(self):
        class C:
            def __init__(self, v1, v2):
                self.v2 = v2
                self.v1 = v1

            def _freeze_(self):
                return True

        c1 = C(1,'a')
        c2 = C(2,'b')
        c3 = C(3,'c')

        def f1(l, c):
            l.append(c.v1)
        def f2(l, c):
            l.append(c.v2)

        def g():
            l1 = []
            l2 = []
            f1(l1, c1)
            f1(l1, c2)
            f2(l2, c2)
            f2(l2, c3)
            return l1,l2

        a = self.RPythonAnnotator()
        s = a.build_types(g,[])
        l1, l2 = s.items
        assert listitem(l1).knowntype == int
        assert listitem(l2).knowntype == str


        acc1 = a.bookkeeper.getdesc(c1).getattrfamily()
        acc2 = a.bookkeeper.getdesc(c2).getattrfamily()
        acc3 = a.bookkeeper.getdesc(c3).getattrfamily()

        assert acc1 is acc2 is acc3

        assert len(acc1.descs) == 3
        assert dict.fromkeys(acc1.attrs) == {'v1': None, 'v2': None}

    def test_single_pbc_getattr(self):
        class C:
            def __init__(self, v1, v2):
                self.v1 = v1
                self.v2 = v2
            def _freeze_(self):
                return True
        c1 = C(11, "hello")
        c2 = C(22, 623)
        def f1(l, c):
            l.append(c.v1)
        def f2(c):
            return c.v2
        def f3(c):
            return c.v2
        def g():
            l = []
            f1(l, c1)
            f1(l, c2)
            return l, f2(c1), f3(c2)

        a = self.RPythonAnnotator()
        s = a.build_types(g,[])
        s_l, s_c1v2, s_c2v2 = s.items
        assert listitem(s_l).knowntype == int
        assert s_c1v2.const == "hello"
        assert s_c2v2.const == 623

        acc1 = a.bookkeeper.getdesc(c1).getattrfamily()
        acc2 = a.bookkeeper.getdesc(c2).getattrfamily()
        assert acc1 is acc2
        assert acc1.attrs.keys() == ['v1']

    def test_simple_pbc_call(self):
        def f1(x,y=0):
            pass
        def f2(x):
            pass
        def f3(x):
            pass
        def g(f):
            f(1)
        def h():
            f1(1)
            f1(1,2)
            g(f2)
            g(f3)
        
        a = self.RPythonAnnotator()
        s = a.build_types(h, [])

        fdesc1 = a.bookkeeper.getdesc(f1)
        fdesc2 = a.bookkeeper.getdesc(f2)
        fdesc3 = a.bookkeeper.getdesc(f3)

        fam1 = fdesc1.getcallfamily()
        fam2 = fdesc2.getcallfamily()
        fam3 = fdesc3.getcallfamily()

        assert fam1 is not fam2
        assert fam1 is not fam3
        assert fam3 is fam2

        gf1 = graphof(a, f1)
        gf2 = graphof(a, f2)
        gf3 = graphof(a, f3)

        assert fam1.calltables == {(2, (), False, False): [{fdesc1: gf1}], (1, (), False, False): [{fdesc1: gf1}]}
        assert fam2.calltables == {(1, (), False, False): [{fdesc2: gf2, fdesc3: gf3}]}

    def test_pbc_call_ins(self):
        class A(object):
            def m(self):
                pass
        class B(A):
            def n(self):
                pass
        class C(A):
            def __init__(self):
                pass
            def m(self):
                pass
        def f(x):
            b = B()
            c = C()
            b.n()
            if x:
                a = b
            else:
                a = c
            a.m()

        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])

        clsdef = a.bookkeeper.getuniqueclassdef
        bookkeeper = a.bookkeeper

        def getmdesc(bmeth):
            return bookkeeper.immutablevalue(bmeth).descriptions.keys()[0]

        mdescA_m = getmdesc(A().m)
        mdescC_m = getmdesc(C().m)
        mdescB_n = getmdesc(B().n)

        assert mdescA_m.name == 'm' == mdescC_m.name
        assert mdescB_n.name == 'n'

        famA_m = mdescA_m.getcallfamily()
        famC_m = mdescC_m.getcallfamily()
        famB_n = mdescB_n.getcallfamily()
        
        assert famA_m is famC_m
        assert famB_n is not famA_m

        gfB_n = graphof(a, B.n.im_func)
        gfA_m = graphof(a, A.m.im_func)
        gfC_m = graphof(a, C.m.im_func)

        assert famB_n.calltables == {(1, (), False, False): [{mdescB_n.funcdesc: gfB_n}] }
        assert famA_m.calltables == {(1, (), False, False): [{mdescA_m.funcdesc: gfA_m, mdescC_m.funcdesc: gfC_m }] }

        mdescCinit = getmdesc(C().__init__)
        famCinit = mdescCinit.getcallfamily()
        gfCinit = graphof(a, C.__init__.im_func)

        assert famCinit.calltables == {(1, (), False, False): [{mdescCinit.funcdesc: gfCinit}] }
        
    def test_isinstance_usigned(self):
        def f(x):
            return isinstance(x, r_uint)
        def g():
            v = r_uint(1)
            return f(v)
        a = self.RPythonAnnotator()
        s = a.build_types(g, [])
        assert s.const == True

    def test_isinstance_base_int(self):
        def f(x):
            return isinstance(x, base_int)
        def g(n):
            v = r_uint(n)
            return f(v)
        a = self.RPythonAnnotator()
        s = a.build_types(g, [int])
        assert s.const == True

    def test_alloc_like(self):
        class C1(object):
            pass
        class C2(object):
            pass

        def inst(cls):
            return cls()

        def alloc(cls):
            i = inst(cls)
            assert isinstance(i, cls)
            return i
        alloc._annspecialcase_ = "specialize:arg(0)"

        def f():
            c1 = alloc(C1)
            c2 = alloc(C2)
            return c1,c2

        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        C1df = a.bookkeeper.getuniqueclassdef(C1)
        C2df = a.bookkeeper.getuniqueclassdef(C2)
        
        assert s.items[0].classdef == C1df
        assert s.items[1].classdef == C2df

        allocdesc = a.bookkeeper.getdesc(alloc)
        s_C1 = a.bookkeeper.immutablevalue(C1)
        s_C2 = a.bookkeeper.immutablevalue(C2)
        graph1 = allocdesc.specialize([s_C1])
        graph2 = allocdesc.specialize([s_C2])
        assert a.binding(graph1.getreturnvar()).classdef == C1df
        assert a.binding(graph2.getreturnvar()).classdef == C2df
        assert graph1 in a.translator.graphs
        assert graph2 in a.translator.graphs
    
    def test_specialcase_args(self):
        class C1(object):
            pass
        
        class C2(object):
            pass
        
        def alloc(cls, cls2):
            i = cls()
            assert isinstance(i, cls)
            j = cls2()
            assert isinstance(j, cls2)
            return i
        
        def f():
            alloc(C1, C1)
            alloc(C1, C2)
            alloc(C2, C1)
            alloc(C2, C2)
        
        alloc._annspecialcase_ = "specialize:arg(0,1)"
        
        a = self.RPythonAnnotator()
        C1df = a.bookkeeper.getuniqueclassdef(C1)
        C2df = a.bookkeeper.getuniqueclassdef(C2)
        s = a.build_types(f, [])
        allocdesc = a.bookkeeper.getdesc(alloc)
        s_C1 = a.bookkeeper.immutablevalue(C1)
        s_C2 = a.bookkeeper.immutablevalue(C2)
        graph1 = allocdesc.specialize([s_C1, s_C2])
        graph2 = allocdesc.specialize([s_C2, s_C2])
        assert a.binding(graph1.getreturnvar()).classdef == C1df
        assert a.binding(graph2.getreturnvar()).classdef == C2df
        assert graph1 in a.translator.graphs
        assert graph2 in a.translator.graphs

    def test_specialize_arg_bound_method(self):
        class GC(object):
            def trace(self, callback, *args):
                return callback(*args)
            trace._annspecialcase_ = "specialize:arg(1)"

            def callback1(self, arg1):
                self.x = arg1
                return "hello"

            def callback2(self, arg2, arg3):
                self.y = arg2
                self.z = arg3
                return 6

        def f():
            gc = GC()
            s1 = gc.trace(gc.callback1, "foo")
            n2 = gc.trace(gc.callback2, 7, 2)
            return (s1, n2, gc.x, gc.y, gc.z)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s.items[0].const == "hello"
        assert s.items[1].const == 6
        assert s.items[2].const == "foo"
        assert s.items[3].const == 7
        assert s.items[4].const == 2

    def test_assert_list_doesnt_lose_info(self):
        class T(object):
            pass
        def g(l):
            assert isinstance(l, list)
            return l
        def f():
            l = [T()]
            return g(l)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        s_item = listitem(s)
        assert isinstance(s_item, annmodel.SomeInstance)
        assert s_item.classdef is a.bookkeeper.getuniqueclassdef(T)
          
    def test_assert_type_is_list_doesnt_lose_info(self):
        class T(object):
            pass
        def g(l):
            assert type(l) is list
            return l
        def f():
            l = [T()]
            return g(l)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        s_item = listitem(s)
        assert isinstance(s_item, annmodel.SomeInstance)
        assert s_item.classdef is a.bookkeeper.getuniqueclassdef(T)


    def test_int_str_mul(self):
        def f(x,a,b):
            return a*x+x*b
        a = self.RPythonAnnotator()
        s = a.build_types(f, [str,int,int])
        assert s.knowntype == str

    def test_list_tuple(self):
        def g0(x):
            return list(x)
        def g1(x):
            return list(x)
        def f(n):
            l1 = g0(())
            l2 = g1((1,))
            if n:
                t = (1,)
            else:
                t = (2,)
            l3 = g1(t)
            return l1, l2, l3
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])
        assert listitem(s.items[0]) == annmodel.SomeImpossibleValue()
        assert listitem(s.items[1]).knowntype == int
        assert listitem(s.items[2]).knowntype == int

    def test_empty_list(self):
        def f():
            l = []
            return bool(l)
        def g():
            l = []
            x = bool(l)
            l.append(1)
            return x, bool(l)
        
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s.const == False

        a = self.RPythonAnnotator()
        s = a.build_types(g, [])

        assert s.items[0].knowntype == bool and not s.items[0].is_constant()
        assert s.items[1].knowntype == bool and not s.items[1].is_constant()
        
    def test_empty_dict(self):
        def f():
            d = {}
            return bool(d)
        def g():
            d = {}
            x = bool(d)
            d['a'] = 1
            return x, bool(d)
        
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s.const == False

        a = self.RPythonAnnotator()
        s = a.build_types(g, [])

        assert s.items[0].knowntype == bool and not s.items[0].is_constant()
        assert s.items[1].knowntype == bool and not s.items[1].is_constant()

    def test_call_two_funcs_but_one_can_only_raise(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.call_two_funcs_but_one_can_only_raise,
                          [int])
        assert s == a.bookkeeper.immutablevalue(None)

    def test_reraiseKeyError(self):
        def f(dic):
            try:
                dic[5]
            except KeyError:
                raise
        a = self.RPythonAnnotator()
        a.build_types(f, [dict])
        fg = graphof(a, f)
        et, ev = fg.exceptblock.inputargs
        t = annmodel.SomeObject()
        t.knowntype = type
        t.const = KeyError
        t.is_type_of = [ev]
        assert a.binding(et) == t
        assert isinstance(a.binding(ev), annmodel.SomeInstance) and a.binding(ev).classdef == a.bookkeeper.getuniqueclassdef(KeyError)

    def test_reraiseAnything(self):
        def f(dic):
            try:
                dic[5]
            except:
                raise
        a = self.RPythonAnnotator()
        a.build_types(f, [dict])
        fg = graphof(a, f)
        et, ev = fg.exceptblock.inputargs
        t = annmodel.SomeObject()
        t.knowntype = type
        t.is_type_of = [ev]
        t.const = KeyError    # IndexError ignored because 'dic' is a dict
        assert a.binding(et) == t
        assert isinstance(a.binding(ev), annmodel.SomeInstance) and a.binding(ev).classdef == a.bookkeeper.getuniqueclassdef(KeyError)

    def test_exception_mixing(self):
        def h():
            pass

        def g():
            pass

        class X(Exception):
            def __init__(self, x=0):
                self.x = x

        def f(a, l):
            if a==1:
                raise X
            elif a==2:
                raise X(1)
            elif a==3:
                raise X,4
            else:
                try:
                    l[0]
                    x,y = l
                    g()
                finally:
                    h()
        a = self.RPythonAnnotator()
        a.build_types(f, [int, list])
        fg = graphof(a, f)
        et, ev = fg.exceptblock.inputargs
        t = annmodel.SomeObject()
        t.knowntype = type
        t.is_type_of = [ev]
        assert a.binding(et) == t
        assert isinstance(a.binding(ev), annmodel.SomeInstance) and a.binding(ev).classdef == a.bookkeeper.getuniqueclassdef(Exception)

    def test_try_except_raise_finally1(self):
        def h(): pass
        def g(): pass
        class X(Exception): pass
        def f():
            try:
                try:
                    g()
                except X:
                    h()
                    raise
            finally:
                h()
        a = self.RPythonAnnotator()
        a.build_types(f, [])
        fg = graphof(a, f)
        et, ev = fg.exceptblock.inputargs
        t = annmodel.SomeObject()
        t.knowntype = type
        t.is_type_of = [ev]
        assert a.binding(et) == t
        assert isinstance(a.binding(ev), annmodel.SomeInstance) and a.binding(ev).classdef == a.bookkeeper.getuniqueclassdef(Exception)

    def test_sys_attrs(self):
        import sys
        def f():
            return sys.argv[0]
        a = self.RPythonAnnotator()
        try:
            oldvalue = sys.argv
            sys.argv = []
            s = a.build_types(f, [])
        finally:
            sys.argv = oldvalue
        assert s is not None

    def test_pow(self):
        def f(n):
            n **= 2
            return 2 ** n
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        # result should be an integer
        assert s.knowntype == int

    def test_inplace_div(self):
        def f(n):
            n /= 2
            return n / 2
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert s.knowntype == int

    def test_prime(self):
        a = self.RPythonAnnotator()
        s = a.build_types(snippet.prime, [int])
        assert s.knowntype == bool

    def test_and_is_true_coalesce(self):
        def f(a,b,c,d,e):
            x = a and b
            if x:
                return d,c
            return e,c
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int, str, a.bookkeeper.immutablevalue(1.0), a.bookkeeper.immutablevalue('d'), a.bookkeeper.immutablevalue('e')])
        assert s == annmodel.SomeTuple([annmodel.SomeChar(), a.bookkeeper.immutablevalue(1.0)])
        assert not [b for b in a.bindings.itervalues() if b.__class__ == annmodel.SomeObject]

    def test_is_true_coalesce2(self):
        def f(a,b,a1,b1,c,d,e):
            x = (a or  b) and (a1 or b1)
            if x:
                return d,c
            return e,c
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int, str, float, list,  a.bookkeeper.immutablevalue(1.0), a.bookkeeper.immutablevalue('d'), a.bookkeeper.immutablevalue('e')])
        assert s == annmodel.SomeTuple([annmodel.SomeChar(), a.bookkeeper.immutablevalue(1.0)])
        assert not [b for b in a.bindings.itervalues() if b.__class__ == annmodel.SomeObject]

    def test_is_true_coalesce_sanity(self):
        def f(a):
            while a:
                pass
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert s == a.bookkeeper.immutablevalue(None)

    def test_non_None_path(self):
        class C:
            pass
        def g(c):
            if c is None:
                return C()
            return c
        def f(x):
            if x:
                c = None
            else:
                c = C()
            return g(c)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])
        assert s.can_be_none() == False

    def test_can_be_None_path(self):
        class C:
            pass
        def f(x):
            if x:
                c = None
            else:
                c = C()
            return isinstance(c, C)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])
        assert not s.is_constant()

    def test_nonneg_cleverness(self):
        def f(a, b, c, d, e, f, g, h):
            if a < 0: a = 0
            if b <= 0: b = 0
            if c >= 0:
                pass
            else:
                c = 0
            if d < a: d = a
            if e <= b: e = 1
            if c > f: f = 2
            if d >= g: g = 3
            if h != a: h = 0
            return a, b, c, d, e, f, g, h
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int]*8)
        assert s == annmodel.SomeTuple([annmodel.SomeInteger(nonneg=True)] * 8)

    def test_general_nonneg_cleverness(self):
        def f(a, b, c, d, e, f, g, h):
            if a < 0: a = 0
            if b <= 0: b = 0
            if c >= 0:
                pass
            else:
                c = 0
            if d < a: d = a
            if e <= b: e = 1
            if c > f: f = 2
            if d >= g: g = 3
            if h != a: h = 0
            return a, b, c, d, e, f, g, h
        a = self.RPythonAnnotator()
        s = a.build_types(f, [r_longlong]*8)
        assert s == annmodel.SomeTuple([annmodel.SomeInteger(nonneg=True, knowntype=r_longlong)] * 8)


    def test_more_nonneg_cleverness(self):
        def f(start, stop):
            assert 0 <= start <= stop
            return start, stop
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int, int])
        assert s == annmodel.SomeTuple([annmodel.SomeInteger(nonneg=True)] * 2)

    def test_more_general_nonneg_cleverness(self):
        def f(start, stop):
            assert 0 <= start <= stop
            return start, stop
        a = self.RPythonAnnotator()
        s = a.build_types(f, [r_longlong, r_longlong])
        assert s == annmodel.SomeTuple([annmodel.SomeInteger(nonneg=True, knowntype=r_longlong)] * 2)

    def test_nonneg_cleverness_is_gentle_with_unsigned(self):
        def witness1(x):
            pass
        def witness2(x):
            pass        
        def f(x):
            if 0 < x:
                witness1(x)
            if x > 0:
                witness2(x)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [annmodel.SomeInteger(unsigned=True)])
        wg1 = graphof(a, witness1)
        wg2 = graphof(a, witness2)        
        assert a.binding(wg1.getargs()[0]).unsigned is True
        assert a.binding(wg2.getargs()[0]).unsigned is True        
        
    def test_general_nonneg_cleverness_is_gentle_with_unsigned(self):
        def witness1(x):
            pass
        def witness2(x):
            pass        
        def f(x):
            if 0 < x:
                witness1(x)
            if x > 0:
                witness2(x)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [annmodel.SomeInteger(knowntype=r_ulonglong)])
        wg1 = graphof(a, witness1)
        wg2 = graphof(a, witness2)        
        assert a.binding(wg1.getargs()[0]).knowntype is r_ulonglong
        assert a.binding(wg2.getargs()[0]).knowntype is r_ulonglong

    def test_nonneg_cleverness_in_max(self):
        def f(x):
            return max(x, 0) + max(0, x)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert s.nonneg

    def test_attr_moving_into_parent(self):
        class A: pass
        class B(A): pass
        a1 = A()
        b1 = B()
        b1.stuff = a1
        a1.stuff = None
        def f():
            return b1.stuff
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert isinstance(s, annmodel.SomeInstance)
        assert not s.can_be_None
        assert s.classdef is a.bookkeeper.getuniqueclassdef(A)

    def test_class_attribute(self):
        class A:
            stuff = 42
        class B(A):
            pass
        def f():
            b = B()
            return b.stuff
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s == a.bookkeeper.immutablevalue(42)

    def test_attr_recursive_getvalue(self):
        class A: pass
        a2 = A()
        a2.stuff = None
        a1 = A()
        a1.stuff = a2
        def f():
            return a1.stuff
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert isinstance(s, annmodel.SomeInstance)
        assert s.can_be_None
        assert s.classdef is a.bookkeeper.getuniqueclassdef(A)

    def test_long_list_recursive_getvalue(self):
        class A: pass
        lst = []
        for i in range(500):
            a1 = A()
            a1.stuff = lst
            lst.append(a1)
        def f():
            A().stuff = None
            return (A().stuff, lst)[1]
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert isinstance(s, annmodel.SomeList)
        s_item = s.listdef.listitem.s_value
        assert isinstance(s_item, annmodel.SomeInstance)

    def test_immutable_dict(self):
        d = {4: "hello",
             5: "world"}
        def f(n):
            return d[n]
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert isinstance(s, annmodel.SomeString)

    def test_immutable_recursive_list(self):
        l = []
        l.append(l)
        def f():
            return l
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert isinstance(s, annmodel.SomeList)
        s_item = s.listdef.listitem.s_value
        assert isinstance(s_item, annmodel.SomeList)
        assert s_item.listdef.same_as(s.listdef)

    def test_defaults_with_list_or_dict(self):
        def fn1(a=[]):
            return a
        def fn2(a={}):
            return a
        def f():
            fn1()
            fn2()
            return fn1([6, 7]), fn2({2: 3, 4: 5})
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert isinstance(s, annmodel.SomeTuple)
        s1, s2 = s.items
        assert not s1.is_constant()
        assert not s2.is_constant()
        assert isinstance(s1.listdef.listitem. s_value, annmodel.SomeInteger)
        assert isinstance(s2.dictdef.dictkey.  s_value, annmodel.SomeInteger)
        assert isinstance(s2.dictdef.dictvalue.s_value, annmodel.SomeInteger)

    def test_pbc_union(self):
        class A:
            def meth(self):
                return 12
        class B(A):
            pass
        class C(B):
            pass
        def f(i):
            if i:
                f(0)
                x = B()
            else:
                x = C()
            return x.meth()
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert s == a.bookkeeper.immutablevalue(12)

    def test_int(self):
        def f(x, s):
            return int(x) + int(s) + int(s, 16)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int, str])
        assert s.knowntype == int

    def test_int_nonneg(self):
        def f(x, y):
            assert x >= 0
            return int(x) + int(y == 3)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int, int])
        assert isinstance(s, annmodel.SomeInteger)
        assert s.nonneg

    def test_listitem_merge_asymmetry_bug(self):
        class K:
            pass
        def mutr(k, x, i):
            k.l2 = [x] + k.l2 # this involves a side-effectful union and unification, with this order
                              # of arguments some reflowing was missed
            k.l2[i] = x
        def witness(i):
            pass
        def trouble(k):
            l = k.l1 + k.l2
            for i in range(len(l)):
                witness(l[i])
        def f(flag, k, x, i):
            if flag:
                k = K()
                k.l1 = []
                k.l2 = []
            trouble(k)
            mutr(k, x, i)
        a = self.RPythonAnnotator()
        a.build_types(f, [bool, K,  int, int])
        g = graphof(a, witness)
        assert a.binding(g.getargs()[0]).knowntype == int

    # check RPython static semantics of isinstance(x,bool|int) as needed for wrap

    def test_isinstance_int_bool(self):
        def f(x):
            if isinstance(x, int):
                if isinstance(x, bool):
                    return "bool"
                return "int"
            return "dontknow"
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])
        assert s.const == "bool"
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert s.const == "int"        
        a = self.RPythonAnnotator()
        s = a.build_types(f, [float])
        assert s.const == "dontknow"        
        
    def test_hidden_method(self):
        class Base:
            def method(self):
                return ["should be hidden"]
            def indirect(self):
                return self.method()
        class A(Base):
            def method(self):
                return "visible"
        class B(A):       # note: it's a chain of subclasses
            def method(self):
                return None
        def f(flag):
            if flag:
                obj = A()
            else:
                obj = B()
            return obj.indirect()
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])
        assert s == annmodel.SomeString(can_be_None=True)

    def test_dont_see_AttributeError_clause(self):
        class Stuff:
            def _freeze_(self):
                return True
            def createcompiler(self):
                try:
                    return self.default_compiler
                except AttributeError:
                    compiler = "yadda"
                    self.default_compiler = compiler
                    return compiler
        stuff = Stuff()
        stuff.default_compiler = 123
        def f():
            return stuff.createcompiler()
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s == a.bookkeeper.immutablevalue(123)

    def test_class_attribute_is_an_instance_of_itself(self):
        class Base:
            hello = None
        class A(Base):
            pass
        A.hello = globalA = A()
        def f():
            return (Base().hello, globalA)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert isinstance(s, annmodel.SomeTuple)
        assert isinstance(s.items[0], annmodel.SomeInstance)
        assert s.items[0].classdef is a.bookkeeper.getuniqueclassdef(A)
        assert s.items[0].can_be_None
        assert s.items[1] == a.bookkeeper.immutablevalue(A.hello)

    def test_dict_and_none(self):
        def f(i):
            if i:
                return {}
            else:
                return None
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert s.knowntype == dict

    def test_const_list_and_none(self):
        def g(l=None):
            return l is None
        L = [1,2]
        def f():
            g()
            return g(L)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s.knowntype == bool
        assert not s.is_constant()
            
    def test_const_dict_and_none(self):
        def g(d=None):
            return d is None
        D = {1:2}
        def f():
            g(D)
            return g()
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s.knowntype == bool
        assert not s.is_constant()
                        
    def test_issubtype_and_const(self):
        class A(object):
            pass
        class B(object):
            pass
        class C(A):
            pass
        b = B()
        c = C()
        def g(f):
            if f == 1:
                x = b
            elif f == 2:
                x = c
            else:
                x = C()
            t = type(x)
            return issubclass(t, A)

        def f():
            x = g(1)
            y = g(0)
            return x or y
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s.knowntype == bool
        assert not s.is_constant()
        a = self.RPythonAnnotator()
        # sanity check
        x = annmodel.SomeInteger()
        x.const = 1
        s = a.build_types(g, [x])
        assert s.const == False
        a = self.RPythonAnnotator()
        x = annmodel.SomeInteger()
        x.const = 2
        s = a.build_types(g, [x])
        assert s.const == True

    def test_reading_also_generalizes(self):
        def f1(i):
            d = {'c': i}
            return d['not-a-char'], d
        a = self.RPythonAnnotator()
        s = a.build_types(f1, [int])
        assert dictkey(s.items[1]).__class__ == annmodel.SomeString
        def f2(i):
            d = {'c': i}
            return d.get('not-a-char', i+1), d
        a = self.RPythonAnnotator()
        s = a.build_types(f2, [int])
        assert dictkey(s.items[1]).__class__ == annmodel.SomeString
        def f3(i):
            d = {'c': i}
            return 'not-a-char' in d, d
        a = self.RPythonAnnotator()
        s = a.build_types(f3, [int])
        assert dictkey(s.items[1]).__class__ == annmodel.SomeString
        def f4():
            lst = ['a', 'b', 'c']
            return 'not-a-char' in lst, lst
        a = self.RPythonAnnotator()
        s = a.build_types(f4, [])
        assert listitem(s.items[1]).__class__ == annmodel.SomeString
        def f5():
            lst = ['a', 'b', 'c']
            return lst.index('not-a-char'), lst
        a = self.RPythonAnnotator()
        s = a.build_types(f5, [])
        assert listitem(s.items[1]).__class__ == annmodel.SomeString

    def test_true_str_is_not_none(self):
        def f(s):
            if s:
                return s
            else:
                return ''
        def g(i):
            if i:
                return f(None)
            else:
                return f('')
        a = self.RPythonAnnotator()
        s = a.build_types(g, [int])
        assert s.knowntype == str
        assert not s.can_be_None

    def test_true_func_is_not_none(self):
        def a1():
            pass
        def a2():
            pass
        def f(a):
            if a:
                return a
            else:
                return a2
        def g(i):
            if i:
                return f(None)
            else:
                return f(a1)
        a = self.RPythonAnnotator()
        s = a.build_types(g, [int])
        assert not s.can_be_None

    def test_emulated_pbc_call_simple(self):
        def f(a,b):
            return a + b
        from pypy.annotation import annrpython
        a = annrpython.RPythonAnnotator()
        from pypy.annotation import model as annmodel

        s_f = a.bookkeeper.immutablevalue(f) 
        a.bookkeeper.emulate_pbc_call('f', s_f, [annmodel.SomeInteger(), annmodel.SomeInteger()])
        a.complete()

        assert a.binding(graphof(a, f).getreturnvar()).knowntype == int
        fdesc = a.bookkeeper.getdesc(f)

        someint = annmodel.SomeInteger()

        assert (fdesc.get_s_signatures((2,(),False,False)) 
                == [([someint,someint],someint)])

    def test_emulated_pbc_call_callback(self):
        def f(a,b):
            return a + b
        from pypy.annotation import annrpython
        a = annrpython.RPythonAnnotator()
        from pypy.annotation import model as annmodel

        memo = []
        def callb(ann, graph):
            memo.append(annmodel.SomeInteger() == ann.binding(graph.getreturnvar()))

        s_f = a.bookkeeper.immutablevalue(f) 
        s = a.bookkeeper.emulate_pbc_call('f', s_f, [annmodel.SomeInteger(), annmodel.SomeInteger()],
                                          callback=callb)
        assert s == annmodel.SomeImpossibleValue()
        a.complete()

        assert a.binding(graphof(a, f).getreturnvar()).knowntype == int
        assert len(memo) >= 1
        for t in memo:
            assert t

    def test_iterator_union(self):
        def it(d):
            return d.iteritems()
        d0 = {1:2}
        def f():
            it(d0)
            return it({1:2})
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert isinstance(s, annmodel.SomeIterator)
        assert s.variant == ('items',)
        
    def test_non_none_and_none_with_isinstance(self):
        class A(object):
            pass
        class B(A):
            pass
        def g(x):
            if isinstance(x, A):
                return x
            return None
        def f():
            g(B())
            return g(None)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert isinstance(s, annmodel.SomeInstance)
        assert s.classdef == a.bookkeeper.getuniqueclassdef(B)

    def test_type_is_no_improvement(self):
        class B(object):
            pass
        class C(B):
            pass
        class D(B):
            pass
        def f(x):
            if type(x) is C:
                return x
            raise Exception
        a = self.RPythonAnnotator()
        s = a.build_types(f, [D])
        assert s == annmodel.SomeImpossibleValue()

    def test_is_constant_instance(self):
        class A(object):
            pass
        prebuilt_instance = A()
        def f(x):
            if x is prebuilt_instance:
                return x
            raise Exception
        a = self.RPythonAnnotator()
        s = a.build_types(f, [A])
        assert s.is_constant()
        assert s.const is prebuilt_instance

    def test_call_memoized_function(self):
        fr1 = Freezing()
        fr2 = Freezing()
        def getorbuild(key):
            a = 1
            if key is fr1:
                result = eval("a+2")
            else:
                result = eval("a+6")
            return result
        getorbuild._annspecialcase_ = "specialize:memo"

        def f1(i):
            if i > 0:
                fr = fr1
            else:
                fr = fr2
            return getorbuild(fr)

        a = self.RPythonAnnotator()
        s = a.build_types(f1, [int])
        assert s.knowntype == int

    def test_call_memoized_function_with_bools(self):
        fr1 = Freezing()
        fr2 = Freezing()
        def getorbuild(key, flag1, flag2):
            a = 1
            if key is fr1:
                result = eval("a+2")
            else:
                result = eval("a+6")
            if flag1:
                result += 100
            if flag2:
                result += 1000
            return result
        getorbuild._annspecialcase_ = "specialize:memo"

        def f1(i):
            if i > 0:
                fr = fr1
            else:
                fr = fr2
            return getorbuild(fr, i % 2 == 0, i % 3 == 0)

        a = self.RPythonAnnotator()
        s = a.build_types(f1, [int])
        assert s.knowntype == int

    def test_stored_bound_method(self):
        # issue 129
        class H:
            def h(self):
                return 42
        class C:
            def __init__(self, func):
                self.f = func
            def do(self):
                return self.f()
        def g():
            h = H()
            c = C(h.h)
            return c.do()

        a = self.RPythonAnnotator()
        s = a.build_types(g, [])
        assert s.is_constant()
        assert s.const == 42

    def test_stored_bound_method_2(self):
        # issue 129
        class H:
            pass
        class H1(H):
            def h(self):
                return 42
        class H2(H):
            def h(self):
                return 17
        class C:
            def __init__(self, func):
                self.f = func
            def do(self):
                return self.f()
        def g(flag):
            if flag:
                h = H1()
            else:
                h = H2()
            c = C(h.h)
            return c.do()

        a = self.RPythonAnnotator()
        s = a.build_types(g, [int])
        assert s.knowntype == int
        assert not s.is_constant()

    def test_getorbuild_as_attr(self):
        from pypy.tool.cache import Cache
        class SpaceCache(Cache):
            def _build(self, callable):
                return callable()
        class CacheX(Cache):
            def _build(self, key):
                return key.x
        class CacheY(Cache):
            def _build(self, key):
                return key.y
        class X:
            def __init__(self, x):
                self.x = x
            def _freeze_(self):
                return True
        class Y:
            def __init__(self, y):
                self.y = y
            def _freeze_(self):
                return True
        X1 = X(1)
        Y2 = Y("hello")
        fromcache = SpaceCache().getorbuild
        def f():
            return (fromcache(CacheX).getorbuild(X1),
                    fromcache(CacheY).getorbuild(Y2))

        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s.items[0].knowntype == int
        assert s.items[1].knowntype == str

    def test_constant_bound_method(self):
        class C:
            def __init__(self, value):
                self.value = value
            def meth(self):
                return self.value
        meth = C(1).meth
        def f():
            return meth()
        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s.knowntype == int

    def test_annotate__del__(self):
        class A(object):
            def __init__(self):
                self.a = 2
            def __del__(self):
                self.a = 1
        def f():
            return A().a
        a = self.RPythonAnnotator()
        t = a.translator
        s = a.build_types(f, [])
        assert s.knowntype == int
        graph = tgraphof(t, A.__del__.im_func)
        assert graph.startblock in a.annotated

    def test_annotate__del__baseclass(self):
        class A(object):
            def __init__(self):
                self.a = 2
            def __del__(self):
                self.a = 1
        class B(A):
            def __init__(self):
                self.a = 3
        def f():
            return B().a
        a = self.RPythonAnnotator()
        t = a.translator
        s = a.build_types(f, [])
        assert s.knowntype == int
        graph = tgraphof(t, A.__del__.im_func)
        assert graph.startblock in a.annotated

    def test_annotate_type(self):
        class A:
            pass
        x = [A(), A()]
        def witness(t):
            return type(t)
        def get(i):
            return x[i]
        def f(i):
            witness(None)
            return witness(get(i))
            
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert s.__class__ == annmodel.SomeObject
        assert s.knowntype == type

    def test_annotate_iter_empty_container(self):
        def f():
            n = 0
            d = {}
            for x in []:                n += x
            for y in d:                 n += y
            for z in d.iterkeys():      n += z
            for s in d.itervalues():    n += s
            for t, u in d.items():      n += t * u
            for t, u in d.iteritems():  n += t * u
            return n

        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert s.is_constant()
        assert s.const == 0

    def test_mixin(self):
        class Mixin(object):
            _mixin_ = True

            def m(self, v):
                return v

        class Base(object):
            pass

        class A(Base, Mixin):
            pass

        class B(Base, Mixin):
            pass

        class C(B):
            pass

        def f():
            a = A()
            v0 = a.m(2)
            b = B()
            v1 = b.m('x')
            c = C()
            v2 = c.m('y')
            return v0, v1, v2

        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert isinstance(s.items[0], annmodel.SomeInteger)
        assert isinstance(s.items[1], annmodel.SomeChar)        
        assert isinstance(s.items[2], annmodel.SomeChar)        

    def test___class___attribute(self):
        class Base(object): pass
        class A(Base): pass
        class B(Base): pass
        class C(A): pass
        def seelater():
            C()
        def f(n):
            if n == 1:
                x = A()
            else:
                x = B()
            y = B()
            result = x.__class__, y.__class__
            seelater()
            return result

        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert isinstance(s.items[0], annmodel.SomePBC)
        assert len(s.items[0].descriptions) == 4
        assert isinstance(s.items[1], annmodel.SomePBC)
        assert len(s.items[1].descriptions) == 1

    def test_slots(self):
        # check that the annotator ignores slots instead of being
        # confused by them showing up as 'member' objects in the class
        class A(object):
            __slots__ = ('a', 'b')
        def f(x):
            a = A()
            a.b = x
            return a.b

        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert s.knowntype == int

    def test_unboxed_value(self):
        class A(object):
            __slots__ = ()
        class C(A, objectmodel.UnboxedValue):
            __slots__ = unboxedattrname = 'smallint'
        def f(n):
            return C(n).smallint

        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert s.knowntype == int


    def test_annotate_bool(self):
        def f(x):
            return ~x
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])
        assert s.knowntype == int
        

        def f(x):
            return -x
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])
        assert s.knowntype == int

        def f(x):
            return +x
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])
        assert s.knowntype == int

        def f(x):
            return abs(x)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])
        assert s.knowntype == int

        def f(x):
            return int(x)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool])
        assert s.knowntype == int


        def f(x, y):
            return x + y
        a = self.RPythonAnnotator()
        s = a.build_types(f, [bool, int])
        assert s.knowntype == int

        a = self.RPythonAnnotator()
        s = a.build_types(f, [int, bool])
        assert s.knowntype == int



    def test_annotate_rarith(self):
        inttypes = [int, r_uint, r_longlong, r_ulonglong]
        for inttype in inttypes:
            c = inttype()
            def f():
                return c
            a = self.RPythonAnnotator()
            s = a.build_types(f, [])
            assert isinstance(s, annmodel.SomeInteger)
            assert s.knowntype == inttype
            assert s.unsigned == (inttype(-1) > 0)
            
        for inttype in inttypes:
            def f():
                return inttype(0)
            a = self.RPythonAnnotator()
            s = a.build_types(f, [])
            assert isinstance(s, annmodel.SomeInteger)
            assert s.knowntype == inttype
            assert s.unsigned == (inttype(-1) > 0)

        for inttype in inttypes:
            def f(x):
                return x
            a = self.RPythonAnnotator()
            s = a.build_types(f, [inttype])
            assert isinstance(s, annmodel.SomeInteger)
            assert s.knowntype == inttype
            assert s.unsigned == (inttype(-1) > 0)

    def test_annotate_rshift(self):
        def f(x):
            return x >> 2
        a = self.RPythonAnnotator()
        s = a.build_types(f, [annmodel.SomeInteger(nonneg=True)])
        assert isinstance(s, annmodel.SomeInteger)
        assert s.nonneg

    def test_prebuilt_mutables(self):
        class A:
            pass
        class B:
            pass
        a1 = A()
        a2 = A()
        a1.d = {}    # this tests confusion between the two '{}', which
        a2.d = {}    # compare equal
        a1.l = []
        a2.l = []
        b = B()
        b.d1 = a1.d
        b.d2 = a2.d
        b.l1 = a1.l
        b.l2 = a2.l

        def dmutate(d):
            d[123] = 321

        def lmutate(l):
            l.append(42)

        def readout(d, l):
            return len(d) + len(l)

        def f():
            dmutate(b.d1)
            dmutate(b.d2)
            dmutate(a1.d)
            dmutate(a2.d)
            lmutate(b.l1)
            lmutate(b.l2)
            lmutate(a1.l)
            lmutate(a2.l)
            return readout(a1.d, a1.l) + readout(a2.d, a2.l)

        a = self.RPythonAnnotator()
        a.build_types(f, [])
        v1, v2 = graphof(a, readout).getargs()
        assert not a.bindings[v1].is_constant()
        assert not a.bindings[v2].is_constant()
    
    def test_helper_method_annotator(self):
        def fun():
            return 21
        
        class A(object):
            def helper(self):
                return 42
        
        a = self.RPythonAnnotator()
        a.build_types(fun, [])
        a.annotate_helper_method(A, "helper", [])
        assert a.bookkeeper.getdesc(A.helper).getuniquegraph()

    def test_chr_out_of_bounds(self):
        def g(n, max):
            if n < max:
                return chr(n)
            else:
                return '?'
        def fun(max):
            v = g(1000, max)
            return g(ord(v), max)

        a = self.RPythonAnnotator()
        s = a.build_types(fun, [int])
        assert isinstance(s, annmodel.SomeChar)

    def test_range_nonneg(self):
        def fun(n, k):
            for i in range(n):
                if k == 17:
                    return i
            return 0
        a = self.RPythonAnnotator()
        s = a.build_types(fun, [int, int])
        assert isinstance(s, annmodel.SomeInteger)
        assert s.nonneg

    def test_reverse_range_nonneg(self):
        def fun(n, k):
            for i in range(n-1, -1, -1):
                if k == 17:
                    return i
            return 0
        a = self.RPythonAnnotator()
        s = a.build_types(fun, [int, int])
        assert isinstance(s, annmodel.SomeInteger)
        assert s.nonneg

    def test_sig(self):
        def fun(x, y):
            return x+y
        s_nonneg = annmodel.SomeInteger(nonneg=True)
        fun._annenforceargs_ = policy.Sig(int, s_nonneg)

        a = self.RPythonAnnotator()
        s = a.build_types(fun, [s_nonneg, s_nonneg])
        assert isinstance(s, annmodel.SomeInteger)
        assert not s.nonneg
        py.test.raises(Exception, a.build_types, fun, [int, int])

    def test_sig_simpler(self):
        def fun(x, y):
            return x+y
        s_nonneg = annmodel.SomeInteger(nonneg=True)
        fun._annenforceargs_ = (int, s_nonneg)

        a = self.RPythonAnnotator()
        s = a.build_types(fun, [s_nonneg, s_nonneg])
        assert isinstance(s, annmodel.SomeInteger)
        assert not s.nonneg
        py.test.raises(Exception, a.build_types, fun, [int, int])

    def test_sig_lambda(self):
        def fun(x, y):
            return y
        s_nonneg = annmodel.SomeInteger(nonneg=True)
        fun._annenforceargs_ = policy.Sig(lambda s1,s2: s1, lambda s1,s2: s1)
        # means: the 2nd argument's annotation becomes the 1st argument's
        #        input annotation

        a = self.RPythonAnnotator()
        s = a.build_types(fun, [int, s_nonneg])
        assert isinstance(s, annmodel.SomeInteger)
        assert not s.nonneg
        py.test.raises(Exception, a.build_types, fun, [s_nonneg, int])

    def test_sig_bug(self):
        py.test.skip("_annenforceargs_ does not work for default arguments")
        def g(x, y=5):
            return y == 5
        g._annenforceargs_ = (int, int)
        def fun(x):
            return g(x)
        a = self.RPythonAnnotator()
        s = a.build_types(fun, [int])
        assert not s.is_constant()

    def test_sig_list(self):
        def g(buf):
            buf.append(5)
        g._annenforceargs_ = ([int],)
        def fun():
            lst = []
            g(lst)
            return lst[0]
        a = self.RPythonAnnotator()
        s = a.build_types(fun, [])
        assert s.knowntype is int
        assert not s.is_constant()

    def test_slots_check(self):
        class Base(object):
            __slots__ = 'x'
        class A(Base):
            __slots__ = 'y'
            def m(self):
                return 65
        class C(Base):
            __slots__ = 'z'
            def m(self):
                return 67
        for attrname, works in [('x', True),
                                ('y', False),
                                ('z', False),
                                ('t', False)]:
            def fun(n):
                if n: o = A()
                else: o = C()
                setattr(o, attrname, 12)
                return o.m()
            a = self.RPythonAnnotator()
            if works:
                a.build_types(fun, [int])
            else:
                from pypy.annotation.classdef import NoSuchAttrError
                py.test.raises(NoSuchAttrError, a.build_types, fun, [int])

    def test_slots_enforce_attrs(self):
        class Superbase(object):
            __slots__ = 'x'
        class Base(Superbase):
            pass
        class A(Base):
            pass
        class B(Base):
            pass
        def fun(s):
            if s is None:   # known not to be None in this test
                o = B()
                o.x = 12
            elif len(s) > 5:
                o = A()
            else:
                o = Base()
            return o.x
        a = self.RPythonAnnotator()
        s = a.build_types(fun, [str])
        assert s == annmodel.s_ImpossibleValue   # but not blocked blocks

    def test_enforced_attrs_check(self):
        class Base(object):
            _attrs_ = 'x'
        class A(Base):
            _attrs_ = 'y'
            def m(self):
                return 65
        class C(Base):
            _attrs_ = 'z'
            def m(self):
                return 67
        for attrname, works in [('x', True),
                                ('y', False),
                                ('z', False),
                                ('t', False)]:
            def fun(n):
                if n: o = A()
                else: o = C()
                setattr(o, attrname, 12)
                return o.m()
            a = self.RPythonAnnotator()
            if works:
                a.build_types(fun, [int])
            else:
                from pypy.annotation.classdef import NoSuchAttrError
                py.test.raises(NoSuchAttrError, a.build_types, fun, [int])

    def test_attrs_enforce_attrs(self):
        class Superbase(object):
            _attrs_ = 'x'
        class Base(Superbase):
            pass
        class A(Base):
            pass
        class B(Base):
            pass
        def fun(s):
            if s is None:   # known not to be None in this test
                o = B()
                o.x = 12
            elif len(s) > 5:
                o = A()
            else:
                o = Base()
            return o.x
        a = self.RPythonAnnotator()
        s = a.build_types(fun, [str])
        assert s == annmodel.s_ImpossibleValue   # but not blocked blocks


    def test_pbc_enforce_attrs(self):
        class F(object):
            _attrs_ = ['foo',]

            def _freeze_(self):
                return True

        p1 = F()
        p2 = F()

        def g(): pass

        def f(x):
            if x:
                p = p1
            else:
                p = p2
            g()
            return p.foo

        a = self.RPythonAnnotator()
        a.build_types(f, [bool])

    def test_enforce_settled(self):
        class A(object):
            _settled_ = True

            def m(self):
                raise NotImplementedError

        class B(A):

            def m(self):
                return 1

            def n(self):
                return 1

        def fun(x):
            if x:
                a = A()
            else:
                a = B()

            return a.m()

        a = self.RPythonAnnotator()
        s = a.build_types(fun, [bool])
        assert s.knowntype == int

        def fun(x):
            if x:
                a = A()
            else:
                a = B()

            return a.n()

        a = self.RPythonAnnotator()
        py.test.raises(Exception, a.build_types, fun, [bool])

    def test_float_cmp(self):
        def fun(x, y):
            return (x < y,
                    x <= y,
                    x == y,
                    x != y,
                    x > y,
                    x >= y)

        a = self.RPythonAnnotator(policy=policy.AnnotatorPolicy())
        s = a.build_types(fun, [float, float])
        assert [s_item.knowntype for s_item in s.items] == [bool] * 6

    def test_empty_range(self):
        def g(lst):
            total = 0
            for i in range(len(lst)):
                total += lst[i]
            return total
        def fun():
            return g([])

        a = self.RPythonAnnotator(policy=policy.AnnotatorPolicy())
        s = a.build_types(fun, [])
        assert s.const == 0

    def test_some_generic_function_call(self):
        def h(x):
            return int(x)

        def c(x):
            return int(x)
        
        def g(a, x):
            if x == -1:
                a = None
            if x < 0:
                if x == -1:
                    a = h
                else:
                    a = c
                x = x + .01
            return a(x)

        #def fun(x):   

        a = self.RPythonAnnotator(policy=policy.AnnotatorPolicy())
        s = a.build_types(g, [annmodel.SomeGenericCallable(
            args=[annmodel.SomeFloat()], result=annmodel.SomeInteger()),
                              annmodel.SomeFloat()])
        assert isinstance(s, annmodel.SomeInteger)
        assert not hasattr(s, 'const')

    def test_compare_int_bool(self):
        def fun(x):
            return 50 < x
        a = self.RPythonAnnotator(policy=policy.AnnotatorPolicy())
        s = a.build_types(fun, [bool])
        assert isinstance(s, annmodel.SomeBool)

    def test_long_as_intermediate_value(self):
        from sys import maxint
        from pypy.rlib.rarithmetic import intmask
        def fun(x):
            if x > 0:
                v = maxint
            else:
                v = -maxint
            return intmask(v * 10)
        P = policy.AnnotatorPolicy()
        P.allow_someobjects = False
        a = self.RPythonAnnotator(policy=P)
        s = a.build_types(fun, [bool])
        assert isinstance(s, annmodel.SomeInteger)

    def test_unionof_some_external_builtin(self):
        from pypy.rpython.ootypesystem.bltregistry import BasicExternal
        
        class A(BasicExternal):
            pass

        class B(A):
            pass

        class C(A):
            pass

        def f(x):
            if x:
                return B()
            else:
                return C()

        P = policy.AnnotatorPolicy()
        P.allow_someobjects = False
        a = self.RPythonAnnotator(policy=P)
        s = a.build_types(f, [bool])
        assert isinstance(s, annmodel.SomeExternalInstance)        

    def test_instance_with_flags(self):
        from pypy.rlib.jit import hint

        class A:
            _virtualizable_ = True
        class B(A):
            def meth(self):
                return self
        class C(A): 
            def meth(self):
                return self

        def f(n):
            x = B()
            x = hint(x, access_directly=True)
            m = x.meth
            for i in range(n):
                x = C()
                m = x.meth
            return x, m, m()

        a = self.RPythonAnnotator()
        s = a.build_types(f, [a.bookkeeper.immutablevalue(0)])
        assert isinstance(s.items[0], annmodel.SomeInstance)
        assert s.items[0].flags == {'access_directly': True}
        assert isinstance(s.items[1], annmodel.SomePBC)
        assert len(s.items[1].descriptions) == 1
        assert s.items[1].descriptions.keys()[0].flags == {'access_directly':
                                                           True}
        assert isinstance(s.items[2], annmodel.SomeInstance)
        assert s.items[2].flags == {'access_directly': True}

        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert isinstance(s.items[0], annmodel.SomeInstance)
        assert s.items[0].flags == {}
        assert isinstance(s.items[1], annmodel.SomePBC)
        assert isinstance(s.items[2], annmodel.SomeInstance)
        assert s.items[2].flags == {}

    def test_ctr_location(self):
        from pypy.rlib.jit import hint

        class A:
            _annspecialcase_ = 'specialize:ctr_location'
            def __init__(self, x):
                self.x = x

        def f(n):
            a = A(2 * n)
            a.x = n
            b = A("")
            b.x = str(n)
            return len(b.x) + a.x
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert isinstance(s, annmodel.SomeInteger)

    def test_weakref(self):
        import weakref

        class A:
            pass
        class B(A):
            pass
        class C(A):
            pass

        def f(n):
            if n:
                b = B()
                b.hello = 42
                r = weakref.ref(b)
            else:
                c = C()
                c.hello = 64
                r = weakref.ref(c)
            return r().hello
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert isinstance(s, annmodel.SomeInteger)
        assert not s.is_constant()

    def test_float_pow_unsupported(self):
        def f(x, y):
            x **= y
            return x ** y
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int, int])
        assert isinstance(s, annmodel.SomeInteger)
        a = self.RPythonAnnotator()
        py.test.raises(NotImplementedError, a.build_types, f, [float, float])

    def test_intcmp_bug(self):
        def g(x, y):
            return x <= y
        def f(x, y):
            if g(x, y):
                g(x, r_uint(y))
        a = self.RPythonAnnotator()
        a.build_types(f, [int, int])

    def test_compare_with_zero(self):
        def g():
            should_not_see_this
        def f(n):
            assert n >= 0
            if n < 0:
                g()
            if not (n >= 0):
                g()
        a = self.RPythonAnnotator()
        a.build_types(f, [int])

    def test_r_singlefloat(self):
        z = r_singlefloat(0.4)
        def g(n):
            if n > 0:
                return r_singlefloat(n * 0.1)
            else:
                return z
        a = self.RPythonAnnotator()
        s = a.build_types(g, [int])
        assert isinstance(s, annmodel.SomeSingleFloat)

    def test_unicode_simple(self):
        def f():
            return u'xxx'

        a = self.RPythonAnnotator()
        s = a.build_types(f, [])
        assert isinstance(s, annmodel.SomeUnicodeString)        

    def test_unicode(self):
        def g(n):
            if n > 0:
                return unichr(1234)
            else:
                return u"x\xe4x"

        def f(n):
            x = g(0)
            return x[n]

        a = self.RPythonAnnotator()
        s = a.build_types(g, [int])
        assert isinstance(s, annmodel.SomeUnicodeString)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert isinstance(s, annmodel.SomeUnicodeCodePoint)

    def test_unicode_from_string(self):
        def f(x):
            return unicode(x)

        a = self.RPythonAnnotator()
        s = a.build_types(f, [str])
        assert isinstance(s, annmodel.SomeUnicodeString)

    def test_unicode_add(self):
        def f(x):
            return unicode(x) + unichr(1234)

        def g(x):
            return unichr(x) + unichr(2)

        a = self.RPythonAnnotator()
        s = a.build_types(f, [str])
        assert isinstance(s, annmodel.SomeUnicodeString)
        a = self.RPythonAnnotator()
        s = a.build_types(f, [int])
        assert isinstance(s, annmodel.SomeUnicodeString)

    def test_unicode_startswith(self):
        def f(x):
            return u'xxxx'.replace(x, u'z')

        a = self.RPythonAnnotator()
        s = a.build_types(f, [unicode])
        assert isinstance(s, annmodel.SomeUnicodeString)

    def test_unicode_buildtypes(self):
        def f(x):
            return x

        a = self.RPythonAnnotator()
        s = a.build_types(f, [unicode])
        assert isinstance(s, annmodel.SomeUnicodeString)

    def test_replace_annotations(self):
        def f(x):
            return 'a'.replace(x, 'b')

        a = self.RPythonAnnotator()
        s = a.build_types(f, [str])
        assert isinstance(s, annmodel.SomeString)
        
        def f(x):
            return u'a'.replace(x, u'b')

        a = self.RPythonAnnotator()
        s = a.build_types(f, [unicode])
        assert isinstance(s, annmodel.SomeUnicodeString)

    def test_unicode_char(self):
        def f(x, i):
            for c in x:
                if c == i:
                    return c
            return 'x'
            
        a = self.RPythonAnnotator()
        s = a.build_types(f, [unicode, str])
        assert isinstance(s, annmodel.SomeUnicodeCodePoint)

    def test_strformatting_unicode(self):
        def f(x):
            return '%s' % unichr(x)
            
        a = self.RPythonAnnotator()
        py.test.raises(NotImplementedError, a.build_types, f, [int])
        def f(x):
            return '%s' % (unichr(x) * 3)
            
        a = self.RPythonAnnotator()
        py.test.raises(NotImplementedError, a.build_types, f, [int])
        def f(x):
            return '%s%s' % (1, unichr(x))
            
        a = self.RPythonAnnotator()
        py.test.raises(NotImplementedError, a.build_types, f, [int])
        def f(x):
            return '%s%s' % (1, unichr(x) * 15)
            
        a = self.RPythonAnnotator()
        py.test.raises(NotImplementedError, a.build_types, f, [int])


    def test_strformatting_tuple(self):
        """
        A function which returns the result of interpolating a tuple of a
        single str into a str format string should be annotated as returning
        SomeString.
        """
        def f(x):
            return '%s' % (x,)

        a = self.RPythonAnnotator()
        s = a.build_types(f, [str])
        assert isinstance(s, annmodel.SomeString)


    def test_negative_slice(self):
        def f(s, e):
            return [1, 2, 3][s:e]

        a = self.RPythonAnnotator()
        py.test.raises(TypeError, "a.build_types(f, [int, int])")
        a.build_types(f, [annmodel.SomeInteger(nonneg=True),
                          annmodel.SomeInteger(nonneg=True)])
        def f(x):
            return x[:-1]

        a.build_types(f, [str])

    def test_listitem_no_mutating(self):
        from pypy.rlib.debug import check_annotation
        called = []

        def checker(ann, bk):
            called.append(True)
            assert not ann.listdef.listitem.mutated
            ann.listdef.never_resize()
        
        def f():
            l = [1,2,3]
            check_annotation(l, checker)
            return l

        def g():
            l = f()
            l.append(4)

        a = self.RPythonAnnotator()
        py.test.raises(TooLateForChange, a.build_types, g, [])
        assert called

    def test_listitem_no_mutating2(self):
        from pypy.rlib.debug import make_sure_not_resized
        
        def f():
            return make_sure_not_resized([1,2,3])

        def g():
            l = [1,2,3]
            l.append(4)
            return l

        def fn(i):
            if i:
                func = f
            else:
                func = g
            return func()

        a = self.RPythonAnnotator()
        a.translator.config.translation.list_comprehension_operations = True
        py.test.raises(TooLateForChange, a.build_types, fn, [int])
            

    def test_listitem_never_resize(self):
        from pypy.rlib.debug import check_annotation

        def checker(ann, bk):
            ann.listdef.never_resize()

        def f():
            l = [1,2,3]
            l.append(4)
            check_annotation(l, checker)

        a = self.RPythonAnnotator()
        py.test.raises(TooLateForChange, a.build_types, f, [])
        

def g(n):
    return [0,1,2,n]

def f_calls_g(n):
    total = 0
    lst = g(n)
    i = 0
    while i < len(lst):
        total += i
        i += 1
    return total

constant_unsigned_five = r_uint(5)
        
class Freezing:
    def _freeze_(self):
        return True
