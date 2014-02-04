import lm_py
#sys.path.append(os.path.realpath(os.path.split(os.path.realpath(os.path.dirname(__file__)))[0]+"/pypy-dist/pypy"))
from pypy.translator.tool.pygame import graphclient
from pypy.translator.tool.make_dot import DotGen, make_dot, make_dot_graphs
from UserString import UserString
from pypy.translator.tool.graphpage import GraphPage
from util import *
class MyGraphPage(GraphPage):
    def test (self,dotgen):
        r_old,r_new=rule.get_blocks_diff(rule.HL.first().pre,rule.HL.last().post)


        #label=[l for l in open("InvTS.py").read().split('\n') if len(l)>0]
        def DrawCode(code,sid,color="red"):
            i=0
            for j in code:
                fillcolor="white"
                if hasattr(j,'added'):
                    fillcolor=color
                data = "\\n" + "\\l".join(j)
                dotgen.emit_node('%s%d'%(sid,i), shape="box", color="black", fillcolor=fillcolor,label=data)
                i+=1
            for j in range(i-1):
                dotgen.emit_edge('%s%d'%(sid,j),'%s%d'%(sid,j+1), label="", style="solid")
        DrawCode(r_old,"old_code","blue")        
        data="Left pane is original code, right pane is transformed code\\n"
        data+="Removed code is blue, inserted code is red\\n"
        data+="All changes are shown. \\n To show changes only relating to a particular rule, click it. \\n\\n"

        data+="%d rules were applied. \\n Please select one: \\n"%len(rule.HL.apps)
        index=0
        for i in rule.HL.apps:
            data+="\\nrule_%d: %s\\l"%(index,i.rule.orig_pat)
            self.links["rule_%d"%index]="See this rule applied"
            index+=1
        data+="\\n\\nShow a global diff due to all rules"
        self.links["all"]="See all rules applied"

        dotgen.emit_node('ball1', shape="box", color="black", fillcolor="white",label=data)
        DrawCode(r_new,"new_code","red")        

        #data = "\\n" + "\\l".join(label)
        #dotgen.emit_node("test234", label=data, shape="box", fillcolor="green", style="filled")

        #self.links['v329']=UserString("123")
        #self.links['test_2']='zog',(1,210,23)
    def main (self,dotgen):
        data="%d rules were applied. \\n Please select one: \\n"%len(rule.HL.apps)
        index=0
        for i in rule.HL.apps:
            data+="\\nrule_%d: %s\\l"%(index,i.rule.orig_pat)
            self.links["rule_%d"%index]="See this rule applied"
            index+=1
        data+="\\n\\nShow a global diff due to all rules"
        self.links["all"]="See all rules applied"
        dotgen.emit_node('mainnode', shape="box", color="black", fillcolor="white",label=data)
    def draw_rule (self,dotgen,id,id2=-1):
        if id2==-1:
            r_old,r_new=rule.get_blocks_diff(rule.HL.apps[id].pre,rule.HL.apps[id].post)
        else:
            r_old,r_new=rule.get_blocks_diff(rule.HL.apps[id].apps[id2][1],rule.HL.apps[id].apps[id2][2])

        def makecode(code,prepend):
            n=len(prepend)
            return "%s\\l"%prepend+"\\l".join([" "*n+i for i in code.split('\n')])+"\\l"
        #label=[l for l in open("InvTS.py").read().split('\n') if len(l)>0]
        def DrawCode(code,sid,color="red"):
            i=0
            for j in code:
                fillcolor="white"
                if hasattr(j,'added'):
                    fillcolor=color
                data = "\\n" + "\\l".join(j)
                dotgen.emit_node('%s%d'%(sid,i), shape="box", color="black", fillcolor=fillcolor,label=data)
                i+=1
            for j in range(i-1):
                dotgen.emit_edge('%s%d'%(sid,j),'%s%d'%(sid,j+1), label="", style="solid")
        def DrawControl ():
            data="Left pane is original code, right pane is transformed code\\n"
            data+="Removed code is blue, inserted code is red\\n"
            if id2==-1:
                data+="All changes are shown. \\n To show changes only relating to the inv or at clauses, \\n click the corresponding clause.\\n\\n"
            elif id2==0:
                data+="Changes due to modifications at query clause are shown. \\n To show changes relating to the inv or at clauses, \\n click the corresponding clause.\\n\\n"
            else:
                data+="Changes due to the at clause \\n %s \\n To show changes only relating to the inv or at clauses, \\n click the corresponding clause.\\n\\n"%rule.HL.apps[id].apps[id2][0].orig_at
            #dotgen.emit_node('ball1', shape="box", color="black", fillcolor="white",label=data)

            data+= "Application of rule %s %s \\l\\n"%("rule_%d"%id, rule.HL.apps[id].rule.orig_pat)
            self.links["rule_%d"%id]="Application of entire rule"
            cr=rule.HL.apps[id]


            for i in range(len(cr.apps)):
                if i==0:
                    data+="inv_%d : inv %s = %s\\l"%(id,cr.rule.var,cr.rule.orig_pat)
                    self.links["inv_%d"%id]="Rule application at query scope"
                else:
                    if cr.apps[i][0].orig_at is None or cr.apps[i][0].orig_at=='':
                        continue
                    data+="at_%d_%d : at %s\\l"%(id,i,cr.apps[i][0].orig_at)
                    self.links["at_%d_%d"%(id,i)]="Rule application at update scope"

                if cr.apps[i][0].orig_if is None or cr.apps[i][0].orig_if!="":
                    data+="              if %s\\l"%(cr.apps[i][0].orig_if)
                #if cr.apps[i][0].orig_de_field!="":
                #    data+="inv_%d : inv %s = %s\\l\\n"%(id,cr.rule.orig_pat)
                if cr.apps[i][0].orig_do_before!="":
                    data+=makecode(cr.apps[i][0].orig_do_before,"              do before %s"%(" py "))
                if cr.apps[i][0].orig_do_instead!="":
                    data+=makecode(cr.apps[i][0].orig_do_instead,"              do instead %s"%(" py "))
                if cr.apps[i][0].orig_do_after!="":
                    data+=makecode(cr.apps[i][0].orig_do_after,"              do after %s"%(" py "))

            dotgen.emit_node('ball2', shape="box", color="black", fillcolor="white",label=data)

            #dotgen.emit_edge('ball1','ball2', label="", style="solid")

        DrawCode(r_old,"old_code","blue")    
        DrawControl()
        DrawCode(r_new,"new_code","red")        

        #data = "\\n" + "\\l".join(label)
        #dotgen.emit_node("test234", label=data, shape="box", fillcolor="green", style="filled")

        #self.links['v329']=UserString("123")
        #self.links['test_2']='zog',(1,210,23)
    def compute(self,title="main"):
        dotgen=DotGen("binding")
        if title=="main":
            self.main(dotgen)
        else:
            if title[:4]=="rule":
                id=int(title[5:])
                self.draw_rule(dotgen,id)
            if title[:3]=="inv":
                id=int(title[4:])
                self.draw_rule(dotgen,id,0)
            if title[:2]=="at":
                ids=map(int,(title[3:].split('_')))
                self.draw_rule(dotgen,ids[0],ids[1])
            if title=="all":
                self.test(dotgen)
        self.source = dotgen.generate(target=None)

    def followlink(self, hlink_name):
        #print hlink_name
        res=MyGraphPage(hlink_name)
        return res

