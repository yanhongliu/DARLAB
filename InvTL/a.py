import string, os,sys,re,types,pprint
import lm_py
from pypy.translator.tool.pygame import graphclient
from pypy.translator.tool.make_dot import DotGen, make_dot, make_dot_graphs
from UserString import UserString
from pypy.translator.tool.graphpage import GraphPage

class MyGraphPage(GraphPage):
    def compute(self,title="TEST"):
        dotgen=DotGen("binding")

        dotgen.emit_node('0', shape="box", color="red", label=title)
        dotgen.emit_node('1', shape="box", color="red", label='v329')
        dotgen.emit_edge('0','1', label=" test_2 ", style="solid")


        label=[l for l in open("InvTS.py").read().split('\n') if len(l)>0]
        i=0
        #for l in label:
        #    dotgen.emit_node('code%d'%i, shape="box", color="black", label="\\l%s"%l)
        #    i+=1

        #for j in range(i-1):
        #    dotgen.emit_edge('code%d'%j,'code%d'%(j+1), label="", style="solid")
        #data = "\\n" + "\\l".join(label)
        #dotgen.emit_node("test234", label=data, shape="box", fillcolor="green", style="filled")
        lnk=UserString("123")
        lnk.asd=123
        #print dir(lnk)
        self.links['v329']=lnk
        self.links['test_2']='zog',(1,210,23)

        self.source = dotgen.generate(target=None)

    def followlink(self, hlink_name):
        print hlink_name.asd
        #print dir(hlink_name)
        res=MyGraphPage(hlink_name)
        return res


MyGraphPage().display()
