import theast as ast
import codegen
import pdb

class Decomposer(ast.NodeTransformer):
    def __init__(self):
        self.temp = 0
    
    def atomic(self,node):
        if isinstance(node, ast.Num) or isinstance(node, ast.Str) or isinstance(node, ast.Name) or node == None:
            return True
        else:
            return False
    def getTemp(self,ctx):
        tempname = 'temp' + str(self.temp)
        self.temp += 1
        return ast.Name(tempname,ctx)

    def visit_Return(self,node):
        if node.value is not None:
            v = self.visit(node.value)
            if not isinstance(v,list):
                if not self.atomic(v):
                    x = []
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],v))
                    x.append(ast.Return(temp))
                    return x
                else:
                    return node
            else:
                x = v[:-1]
                if not self.atomic(v[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],v[-1]))
                    x.append(ast.Return(temp))
                    return x
                else:
                    x.append(ast.Return(v[-1]))                
                return x
        else:
            return node
    
    def visit_Delete(self,node):
        x = []
        for t in node.targets:
            v = self.visit(t)
            if isinstance(v,list):
                x.extend(v[:1])
                x.append(ast.Delete([v[-1]]))
            else:
                x.append(ast.Delete([v]))
        return x
    
    def visit_Assign(self,node):
        v = self.visit(node.value)
        if len(node.targets) > 1:
            node.targets.reverse()
            first = True
            if not isinstance(v,list):
                r = [ast.Assign([node.targets[0]],v)]
            else:
                r = v[:-1]
                if isinstance(node.targets[0],ast.Tuple) and isinstance(v[-1],ast.Tuple):
                    le=[]
                    for L,R in zip(node.targets[0].elts,v[-1].elts):
                        le.append(ast.Assign([L],R))
                else:
                    le=[ast.Assign([node.targets[0]],v[-1])]
                for l in le:
                    r.append(l)
            v = node.targets[0]
            for target in node.targets[1:]:
                if isinstance(target,ast.Tuple) and isinstance(v,ast.Tuple):
                    le=[]
                    for L,R in zip(target.elts,v.elts):
                        le.append(ast.Assign([L],R))
                else:
                    le=[ast.Assign([target],v)]
                for l in le:
                    r.append(l)
                v = target
            return r
        else:
            t = self.visit(node.targets[0])
            if not isinstance(v,list):
                if not isinstance(t,list):
                    return ast.Assign([node.targets[0]],v)
                else:
                    x = t[:-1]
                    x.append(ast.Assign([t[-1]],v))
                    return x

            else:
                if not isinstance(t,list):                    
                    x = v[:-1]
                    x.append(ast.Assign([node.targets[0]],v[-1]))
                    return x
                else:
                    x = v[:-1]+t[:-1]
                    if isinstance(t[-1],ast.Tuple) and isinstance(v[-1],ast.Tuple):
                        le=[]
                        for l,r in zip(t[-1].elts,v[-1].elts):
                            le.append(ast.Assign([l],r))
                    else:
                        le=[ast.Assign([t[-1]],v[-1])]
                    for l in le:
                        x.append(l)
                    return x

    def visit_AugAssign(self,node):
        v = self.visit(node.value)
        if not isinstance(v,list):
            return ast.AugAssign(node.target,node.op,v)
        else:
            x = v[0:len(v)-1]
            x.append(ast.AugAssign(node.target,node.op,v[len(v)-1]))
            return x
    
    def visit_Print(self,node):
        x = []
        if not self.atomic(node.dest):
            v = self.visit(node.dest)
            if isinstance(v,list):
                x.extend(v[0:len(v)-1])
                if not self.atomic(v[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],v[-1]))
                    node.dest = temp
                else:
                    node.dest = v[-1]
        if isinstance(node.values,list):
            for a in node.values:
                v = self.visit(a)
                ret = ast.Print(node.dest,a,node.nl)
                if isinstance(v,list):
                    x.extend(v[0:len(v)-1])
                    if not self.atomic(v[-1]):
                        temp = self.getTemp(ast.Store())
                        x.append(ast.Assign([temp],v[-1]))
                        ret.values = [temp]
                    else:
                        ret.values = [v[-1]]
                else:
                    ret.values = [ret.values]
                x.append(ret)
        else:
            x.append(node)
        return x
    
    def visit_For(self,node):
        t = self.visit(node.target)
        if isinstance(t,list):
            if len(t) == 1:
                t = t[0]
            else:
                raise RuntimeError, 'for has a tuple result with length more than one'
        i = self.visit(node.iter)
        newbody = []
        for b in node.body:
            v = self.visit(b)
            if isinstance(v,list):
                newbody.extend(v)
            else:
                newbody.append(v)
        node.body = newbody
        
        neworelse = []
        for o in node.orelse:
            v = self.visit(o)
            if isinstance(v,list):
                neworelse.extend(v)
            else:
                neworelse.append(v)        
        node.orelse = neworelse
        if isinstance(i,list):
            x = i[0:len(i)-1]
            #code below by misha, i think unnecessary.
            #if isinstance(t,list) and len(t)==1:
            #    t=t[0]
            temp = self.getTemp(ast.Store())
            x.append(ast.Assign([temp],i[-1]))
            x.append(ast.For(t,temp,node.body,node.orelse))
            return x            
        else:
            return node
    
    def visit_While(self,node):
        t = self.visit(node.test)
        newbody = []
        for b in node.body:
            v = self.visit(b)
            if isinstance(v,list):
                newbody.extend(v)
            else:
                newbody.append(v)
        node.body = newbody
        
        neworelse = []
        for o in node.orelse:
            v = self.visit(o)
            if isinstance(v,list):
                neworelse.extend(v)
            else:
                neworelse.append(v)        
        node.orelse = neworelse
        x = []
        if not self.atomic(t):
            if isinstance(t,list):
                x = t[0:len(t)-1]
                node.body.extend(x)
                x.append(ast.While(t[len(t)-1],node.body,node.orelse))
            else:
                temp = self.getTemp(ast.Store())
                x.append(ast.Assign([temp],t))
                node.body.append(ast.Assign([temp],t))
                x.append(ast.While(temp,node.body,node.orelse))
            return x    
        else:
            return node
    
    def visit_If(self,node):
        t = self.visit(node.test)
        newbody = []
        for b in node.body:
            v = self.visit(b)
            if isinstance(v,list):
                newbody.extend(v)
            else:
                newbody.append(v)
        node.body = newbody
        
        neworelse = []
        for o in node.orelse:
            v = self.visit(o)
            if isinstance(v,list):
                neworelse.extend(v)
            else:
                neworelse.append(v)        
        node.orelse = neworelse
        
        x = []
        if not self.atomic(t):
            if isinstance(t,list):
                x = t[0:len(t)-1]
                if self.atomic(t[-1]):
                    x.append(ast.If(t[len(t)-1],node.body,node.orelse))
                else:
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],t[-1]))
                    x.append(ast.If(temp,node.body,node.orelse))
            else:
                temp = self.getTemp(ast.Store())
                x.append(ast.Assign([temp],t))
                x.append(ast.If(temp,node.body,node.orelse))
            return x
        else:
            return node
    
    def visit_Assert(self,node):
        v = self.visit(node.test)
        x = []
        if isinstance(v,list):
            x.extend(v[0:len(v)-1])
            x.append(ast.Assert(v[-1],node.msg))
            return x
        else:        
            return node
    
    def visit_Import(self,node):
        return [ast.Import([n]) for n in node.names]
    
    def visit_ImportFrom(self,node):
        return [ast.ImportFrom(node.module,[n],node.level) for n in node.names]
        
    def visit_BoolOp(self,node):
        x = []
        for idx, v in enumerate(node.values):
            if not self.atomic(v):
                a = self.visit(v)
                if isinstance(a, list):
                    x.extend(a[0:len(a)-1])
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],a[len(a)-1]))
                    node.values[idx] = temp
                else:
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],a))
                    node.values[idx] = temp
        x.append(node)
        return x
    
    def visit_BinOp(self,node):
        if self.atomic(node.left) and self.atomic(node.right):
            return node
        else:
            if self.atomic(node.right):
                lefttemp = self.getTemp(ast.Store())
                v = self.visit(node.left)
                if isinstance(v,list):
                    leftpart = ast.Assign([lefttemp],v[len(v)-1])
                    x = v[0:len(v)-1]
                else:
                    leftpart = ast.Assign([lefttemp],v)
                    x = []
                self.visit(leftpart)
                operation = ast.BinOp(lefttemp,node.op,node.right)

                x.append(leftpart)
                x.append(operation)
                return x
            elif self.atomic(node.left):
                righttemp = self.getTemp(ast.Store())
                v = self.visit(node.right)
                if isinstance(v,list):
                    rightpart = ast.Assign([righttemp],v[len(v)-1])
                    x = v[0:len(v)-1]
                else:
                    rightpart = ast.Assign([righttemp],v)
                    x = []
                self.visit(rightpart)
                operation = ast.BinOp(node.left,node.op,righttemp)

                x.append(rightpart)
                x.append(operation)
                return x
            else:
                lefttemp = self.getTemp(ast.Store())
                v = self.visit(node.left)
                if isinstance(v,list):
                    leftpart = ast.Assign([lefttemp],v[len(v)-1])
                    x = v[0:len(v)-1]
                else:
                    leftpart = ast.Assign([lefttemp],v)
                    x = []
                self.visit(leftpart)
                x.append(leftpart)
                righttemp = self.getTemp(ast.Store())
                v = self.visit(node.right)
                if isinstance(v,list):
                    rightpart = ast.Assign([righttemp],v[len(v)-1])
                    y = v[0:len(v)-1]
                else:
                    rightpart = ast.Assign([righttemp],v)
                    y = []
                self.visit(rightpart)
                
                operation = ast.BinOp(lefttemp,node.op,righttemp)
                
                y.append(rightpart)
                x.extend(y)
                x.append(operation)
                return x
    
    def visit_UnaryOp(self,node):
        o = self.visit(node.operand)
        if isinstance(o,list):
            x = o[0:len(o)-1]
            if not self.atomic(o[-1]):
                temp = self.getTemp(ast.Store())
                x.append(ast.Assign([temp],o[-1]))
                x.append(ast.UnaryOp(node.op,temp))
            else:
                x.append(ast.UnaryOp(node.op,o[len(o)-1]))
            return x
        else:
            x = []
            if not self.atomic(o):
                temp = self.getTemp(ast.Store())
                x.append(ast.Assign([temp],o))
                x.append(ast.UnaryOp(node.op,temp))
            else:
                x.append(node)
        return x
    
    
    def visit_Lambda(self,node):
        temp = self.getTemp(ast.Store())
        x=[]
        retval=ast.Return(node.body)
        newbody=self.visit(retval)
        if not isinstance(newbody, list):
            newbody=[newbody]
        x.append(ast.FunctionDef(temp.id,node.args,newbody,[]))
        x.append(temp)
        return x
        
    def visit_Dict(self,node):
        x = []
        for i in range(len(node.keys)):
            e = self.visit(node.keys[i])
            b = self.visit(node.values[i])
            if isinstance(e,list):
                x.extend(e[0:len(e)-1])
                if not self.atomic(e[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],e[-1]))
                    node.keys[i] = temp
                else:
                    node.keys[i] = e[-1]                
            if isinstance(b,list):
                x.extend(b[0:len(b)-1])
                if not self.atomic(b[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],b[-1]))
                    node.values[i] = temp
                else:
                    node.values[i] = b[-1]
        x.append(node)
        return x                    
    
    def visit_ListComp(self,node):
        temp = self.getTemp(ast.Store())
        x = [ast.Assign([temp],ast.List([],ast.Load()))]
        node.generators.reverse()
        node.elt = self.visit(node.elt)
        body = []
        if self.atomic(node.elt):
            body.append(ast.Call(ast.Attribute(temp,'append',ast.Load()),[node.elt],[],None,None))
        else:
            if isinstance(node.elt,list):
                body.extend(node.elt[0:len(node.elt)-1])
                if not self.atomic(node.elt[-1]):
                    temp = self.getTemp(ast.Store())
                    body.append(ast.Assign([temp],node.elt[-1]))
                    body.append(ast.Call(ast.Attribute(temp,'append',ast.Load()),[temp],[],None,None))
                else:
                    body.append(ast.Call(ast.Attribute(temp,'append',ast.Load()),[node.elt[-1]],[],None,None))
            elif not self.atomic(node.elt):
                temp2 = self.getTemp(ast.Store())
                body.append(ast.Assign([temp2],node.elt))
                body.append(ast.Call(ast.Attribute(temp,'append',ast.Load()),[temp2],[],None,None))
        for g in node.generators:
            for i in g.ifs:
                v = self.visit(i)
                current = []
                if isinstance(v,list):
                    current.extend(v[0:len(v)-1])
                    current.append(ast.If(v[-1],body,[]))
                    body = current
                elif not self.atomic(v):
                    temp2 = self.getTemp(ast.Store())
                    current.append(ast.Assign([temp2],v))
                    current.append(ast.If(temp2,body,[]))
                    body = current
            i = self.visit(g.iter)
            current = []
            if isinstance(i,list):
                current.extend(i[0:len(i)-1])
                current.append(ast.For(g.target,i[-1],body,[]))
                body = current
            elif not self.atomic(i):
                temp2 = self.getTemp(ast.Store())
                current.append(ast.Assign([temp2],i))
                current.append(ast.For(g.target,temp2,body,[]))
                body = current
            else:
                body = [ast.For(g.target,i,body,[])]
        x.extend(body)
        x.append(temp)
        return x
    
    def visit_GeneratorExp(self,node):
        return self.visit_ListComp(node)
        #@TODO: FiX THE BELOW
        x = []
        realarglist = []
        node.generators.reverse()
        node.elt = self.visit(node.elt)
        body = []
        if self.atomic(node.elt):
            body.append(ast.Yield(node.elt))
        else:
            if isinstance(node.elt,list):
                body.extend(node.elt[0:len(node.elt)-1])
                if not self.atomic(node.elt[-1]):
                    temp = self.getTemp(ast.Store())
                    body.append(ast.Assign([temp],node.elt[-1]))
                    body.append(ast.Yield(temp))
                else:
                    body.append(ast.Yield(node.elt[-1]))
            elif not self.atomic(node.elt):
                temp2 = self.getTemp(ast.Store())
                body.append(ast.Assign([temp2],node.elt))
                body.append(ast.Yield(temp2))
        for num,g in enumerate(node.generators):
            for i in g.ifs:
                v = self.visit(i)
                current = []
                if isinstance(v,list):
                    current.extend(v[0:len(v)-1])
                    current.append(ast.If(v[-1],body,[]))
                    body = current
                elif not self.atomic(v):
                    temp2 = self.getTemp(ast.Store())
                    current.append(ast.Assign([temp2],v))
                    current.append(ast.If(temp2,body,[]))
                    body = current
            i = self.visit(g.iter)
            current = []
            if isinstance(i,list):
                x.extend(i[0:len(i)-1])
                current.append(ast.For(g.target,'arg' + repr(num),body,[]))
                realarglist.append(i[-1])
                body = current
            elif not self.atomic(i):
                temp2 = self.getTemp(ast.Store())
                x.append(ast.Assign([temp2],i))
                realarglist.append(temp2)
                current.append(ast.For(g.target,temp2,body,[]))
                body = current
            else:
                realarglist.append(i)
                body = [ast.For(g.target,i,body,[])]
        temp = self.getTemp(ast.Store())
        arglist = [ast.Name('arg' + repr(i),ast.Param()) for i in range(len(node.generators))]
        a = ast.arguments()
        a.args = arglist
        a.defaults = []
        a.vararg = None
        a.kwarg = None
        body = ast.FunctionDef(temp.id,a,body,[])
        x.append(body)
        temp2 = self.getTemp(ast.Store())
        x.append(ast.Assign([temp2],ast.Call(temp,realarglist,[],None,None)))
        x.append(temp2)
        return x
        
    
    def visit_Compare(self,node):
        l = self.visit(node.left)
        c = self.visit(node.comparators[0])
        x = []
        if not self.atomic(l):
            if isinstance(l,list):
                x.extend(l[0:len(l)-1])
                if not self.atomic(l[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],l[-1]))
                    node.left = temp
                else:
                    node.left = l[-1]
            else:
                temp = self.getTemp(ast.Store())
                x.append(ast.Assign([temp],l))
                node.left = temp
        if not self.atomic(c):
            if isinstance(c,list):
                x.extend(c[0:len(c)-1])
                if not self.atomic(c[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],c[-1]))
                    node.comparators[0] = temp
                else:
                    node.comparators[0] = c[-1]
            else:
                temp = self.getTemp(ast.Store())
                x.append(ast.Assign([temp],c))
                node.comparators[0] = temp
        x.append(node)
        return x
    
    def visit_Call(self,node):
        x = []
        f = self.visit(node.func)
        if isinstance(f,list):
            x = f[0:len(f)-1]
            if not self.atomic(f[-1]):
                temp = self.getTemp(ast.Store())
                x.append(ast.Assign([temp],f[-1]))
                node.func = temp
            else:
                node.func = f[-1]
        elif not self.atomic(f):
            temp = self.getTemp(ast.Store())
            x = [ast.Assign([temp],f)]
            node.func = temp
            
        for idx, v in enumerate(node.args):
            if not self.atomic(v):
                a = self.visit(v)
                if isinstance(a, list):
                    x.extend(a[0:len(a)-1])
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],a[len(a)-1]))
                    node.args[idx] = temp
                else:
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],a))
                    node.args[idx] = temp
        for idx, t in enumerate(node.keywords):
            v = t.value
            if not self.atomic(v):
                a = self.visit(v)
                if isinstance(a, list):
                    x.extend(a[0:len(a)-1])
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],a[len(a)-1]))
                    node.keywords[idx].value = temp
                else:
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],a))
                    node.keywords[idx].value = temp
        x.append(node)
        return x
    
    def visit_Attribute(self,node):
        if not self.atomic(node.value):
            v = self.visit(node.value)
            if isinstance(v,list):
                x = v[0:len(v)-1]
                if not self.atomic(v[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],v[len(v)-1]))
                    x.append(ast.Attribute(temp,node.attr,ast.Load()))
                else:
                    x.append(ast.Attribute(v[len(v)-1],node.attr,ast.Load()))
            else:
                temp = self.getTemp(ast.Store())
                x = [ast.Assign([temp],v)]
                x.append(ast.Attribute(temp,node.attr,ast.Load()))
            return x
        else:
            return node
    
    def visit_Raise(self, node):
        ''' For python 3.0, use this: 
        x = []
        if not self.atomic(node.exc):
            v = self.visit(node.exc)
            if isinstance(v,list):
                x.extend(v[0:len(v)-1])
                if not self.atomic(v[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],v[len(v)-1]))
                    node.exc = temp
        if not self.atomic(node.cause):
            v = self.visit(node.cause)
            if isinstance(v,list):
                x.extend(v[0:len(v)-1])
                if not self.atomic(v[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],v[len(v)-1]))
                    node.cause = temp
        x.append(node)
        return x
        '''
        x = []
        if not self.atomic(node.type):
            v = self.visit(node.type)
            if isinstance(v,list):
                x.extend(v[0:len(v)-1])
                if not self.atomic(v[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],v[len(v)-1]))
                    node.type = temp
        if not self.atomic(node.inst):
            v = self.visit(node.inst)
            if isinstance(v,list):
                x.extend(v[0:len(v)-1])
                if not self.atomic(v[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],v[len(v)-1]))
                    node.inst = temp
        
        if not self.atomic(node.tback):
            v = self.visit(node.tback)
            if isinstance(v,list):
                x.extend(v[0:len(v)-1])
                if not self.atomic(v[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],v[len(v)-1]))
                    node.tback = temp
        x.append(node)
        return x
                                
    def visit_Subscript(self,node):
        a1 = a2 = True
        x = []
        final = ast.Subscript(node.value,node.slice,node.ctx)
        if not self.atomic(node.value):
            a1 = False
            v = self.visit(node.value)
            if isinstance(v,list):
                x.extend(v[0:len(v)-1])
                final.value = v[len(v)-1]
                if not self.atomic(final.value):
                    temp1 = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp1],v[len(v)-1]))
                    final.value = temp1
            else:
                temp1 = self.getTemp(ast.Store())
                x.append(ast.Assign([temp1],v))
                final.value = temp1
        if isinstance(node.slice,ast.Index):
            if not self.atomic(node.slice.value):
                a2 = False
                v = self.visit(node.slice.value)
                if isinstance(v,list):
                    x.extend(v[0:len(v)-1])
                    final.slice.value = v[len(v)-1]
                    if not self.atomic(final.slice.value):
                        temp2 = self.getTemp(ast.Store())
                        x.append(ast.Assign([temp2],v[len(v)-1]))
                        final.slice.value = temp2
                else:
                    temp2 = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp2],v))
                    final.slice.value = temp2
        if isinstance(node.slice,ast.Slice):
            if not self.atomic(node.slice.lower):
                a2 = False
                v = self.visit(node.slice.lower)
                if isinstance(v,list):
                    x.extend(v[0:len(v)-1])
                    final.slice.lower = v[len(v)-1]
                    if not self.atomic(final.slice.lower):
                        temp2 = self.getTemp(ast.Store())
                        x.append(ast.Assign([temp2],v[len(v)-1]))
                        final.slice.lower = temp2
                else:
                    temp2 = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp2],v))
                    final.slice.lower = temp2
            if not self.atomic(node.slice.upper):
                a2 = False
                v = self.visit(node.slice.upper)
                if isinstance(v,list):
                    x.extend(v[0:len(v)-1])
                    final.slice.upper = v[len(v)-1]
                    if not self.atomic(final.slice.upper):
                        temp2 = self.getTemp(ast.Store())
                        x.append(ast.Assign([temp2],v[len(v)-1]))
                        final.slice.upper = temp2
                else:
                    temp2 = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp2],v))
                    final.slice.upper = temp2
            if not self.atomic(node.slice.step):
                a2 = False
                v = self.visit(node.slice.step)
                if isinstance(v,list):
                    x.extend(v[0:len(v)-1])
                    final.slice.step = v[len(v)-1]
                    if not self.atomic(final.slice.step):
                        temp2 = self.getTemp(ast.Store())
                        x.append(ast.Assign([temp2],v[len(v)-1]))
                        final.slice.step = temp2
                else:
                    temp2 = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp2],v))
                    final.slice.step = temp2
        if a1 and a2:
            return node
        else:
            x.append(final)
            return x
            
    def visit_List(self,node):
        x = []
        for i,e in enumerate(node.elts):
            v = self.visit(e)
            if isinstance(v,list):
                x.extend(v[0:len(v)-1])
                if not self.atomic(v[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],v[-1]))
                    node.elts[i] = temp
                else:
                    node.elts[i] = v[-1]
        x.append(node)
        return x
        
    def visit_Tuple(self,node):
        x = []
        for i,e in enumerate(node.elts):
            v = self.visit(e)
            if isinstance(v,list):
                x.extend(v[0:len(v)-1])
                if not self.atomic(v[-1]):
                    temp = self.getTemp(ast.Store())
                    x.append(ast.Assign([temp],v[-1]))
                    node.elts[i] = temp
                else:
                    node.elts[i] = v[-1]
        x.append(node)
        #if len(x)==1: #Yes, this is needed. I don't think so :) - tuncay
        #    return x[0]
        return x        
    
    def visit_TryExcept(self,node):
        newbody = []
        for b in node.body:
            v = self.visit(b)
            if isinstance(v,list):
                newbody.extend(v)
            else:
                newbody.append(v)
        node.body = newbody
        
        neworelse = []
        for b in node.orelse:
            v = self.visit(b)
            if isinstance(v,list):
                neworelse.extend(v)
            else:
                neworelse.append(v)
        node.orelse = neworelse
        
        node.handlers = [self.visit(node.handlers[i]) for i in xrange(len(node.handlers))]
        return node
    
    def visit_ExceptHandler(self,node):
        newbody = []
        for b in node.body:
            v = self.visit(b)
            if isinstance(v,list):
                newbody.extend(v)
            else:
                newbody.append(v)
        node.body = newbody
        return node 
        
def simplify(file):
    node = ast.parse(open(file).read(),filename=file)
    node = ast.fix_missing_locations(Decomposer().visit(node))
    return codegen.to_source(node)        
    
    
    
        

