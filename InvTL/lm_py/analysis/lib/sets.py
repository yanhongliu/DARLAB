class Set:
    def __init__(self):
        self.next = None
        self.last = self

    def add(self, value):
        eval_code_in_interpreter="""
for t in handler.locals['self']: 
    if not hasattr(t,'types'):
        t.types=set()
    for T in handler.locals['value']:
        t.types.add(T)
"""
        eval_code_in_interpreter="""
for t in handler.locals['self']: 
    if not hasattr(t,'values'):
        t.values=set()
    for T in handler.locals['value']:
        t.values.add(T)
"""
        n=self        
        while n.next is not None:
            if n.value==value:
                break 
            n = n.next
        if n.next==None:
            n = self.last
            n.value = value
            n.next = self.__class__()
            self.last = n.next
    def remove(self, value):
        pass
    def pop(self):
        n=self
        assert n.next is not None, "Popping from empty set!"

        while n.next is not None:
            n = n.next
        ret=n.next
        self.last=n
        n.next=None
        return ret

    def __len__(self):
        i = 0
        n = self
        while n.next is not None:
            n = n.next
            i += 1
        return i
    def issubset(self,s):
        """
        NATIVE
        INTERCHANGEABLE
        """
        return boolean()

    def copy(self):
        return self
        #x=Set()
        #n = self
        #while n.next is not None:
        #    n = n.next
        #    x.add(n)
            
    def __str__(self):
        output = ["("]
        n = self
        first = 1
        while n.next is not None:
            if not first:
                output.append(", ")
            else:
                first = 0
            output.append(str(n.value))
            n = n.next
        output.append(")")
        return "".join(output)

    def __iter__(self):
        return setiterator(self)

    def __true__(self):
        return self.__len__() != 0
    def str(self):
        return self.__str__a
    def __contains__(self,a):
        return True
    def __notcontains__(self,a):
        return False

class Dict:
    def __init__(self):
        self.next = None
        self.last = self
    def get(self,k,default):
        n=self        
        while n.next is not None:
            if n.value==value:
                return n.key
            n = n.next
        return default

    def __setitem__(self, k,value):
        n=self        
        while n.next is not None:
            if n.value==value:
                n.key=k
            n = n.next
        if n.next==None:
            n = self.last
            n.value = value
            n.key=k
            n.next = self.__class__()
            self.last = n.next

    def __getitem__(self,key):
        n=self        
        while n.next is not None:
            if n.value==value:
                return n.key
            n = n.next

    def __delitem__(self, key):
        pass

    def __len__(self):
        i = 0
        n = self
        while n.next is not None:
            n = n.next
            i += 1
        return i

    def __true__(self):
        return self.__len__() != 0
    def __contains__(self,a):
        return True
    def __notcontains__(self,a):
        return False
    
class setiterator:
    def __init__(self, l):
        self.l = l

    def next(self):
        l = self.l
        next = l.next
        if next is not None:
            self.l = next
            return l.value
        else:
            raise StopIteration() # NOTE: Make this compliant with Python!

    def __iter__(self):
        return setiterator(self.l)

    def __true__(self):
        """
        NAME: IMPL.builtins.int.__true__
        NATIVE
        """
        return boolean()
class ReverseMap():
    def __init__(self):
        pass

class RCMultiMap():
    def __init__(self):
        pass
    def __getitem__(self,param):
        return Set()


class MultiMap:

    def __init__(self):
        self.dct = {}

    def get(self, k):
        temp0 = self.dct
        if (k in temp0):
            temp1 = self.dct
            return temp1[k]
        else:
            return sets.Set()

    def add(self, k, v):
        temp2 = self.dct
        if (k in temp2):
            s = sets.Set()
            self.dct[k] = s
            s.add(v)
        else:
            temp3 = self.dct
            temp4 = temp3[k]
            temp4.add(v)

    def remove(self, k, v):
        temp5 = self.dct
        if (k in temp5):
            temp6 = self.dct
            s = temp6[k]
            s.remove(v)
            temp8 = (not s)
            if temp8:
                temp7 = self.dct
#                del temp7[k]


class MultiMap:
    def __init__(self):
        """
        NATIVE
        """
        self.dct=Dict()
        pass
    def get(self, k):
        """
        NATIVE
        """
        #temp0 = self.dct
        return Set()
        #if (k in temp0):
        #    pdb.set_trace()
        #    temp1 = self.dct
        #    return temp1[k]
        #else:
        #    return sets.Set()
        #temp0 = self.dct
        #if (k in temp0):
        #    temp1 = self.dct
        #    return temp1[k]
        #else:
        #    return Set()

    def add(self, k, v):
        eval_code_in_interpreter="""
for t in handler.locals['self']: 
    if not hasattr(t,'values'):
        t.values=set()
    for K in handler.locals['k']:
        for V in handler.locals['v']:
            t.values.add((K,V))
"""        

    def remove(self, k, v):
        """
        NATIVE
        INTERCHANGEABLE
        """
        pass

