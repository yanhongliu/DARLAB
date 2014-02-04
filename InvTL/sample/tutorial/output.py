import collections
import sets
def incr(query, o):
    rv = rcset() 
    for i in (a for a in o.S for a in o.T):
        rv.add(i)
        
    return rv
def incr(query, o):
    rv = rcset() 
    for i in (a for a in o.S for a in o.T):
        rv.add(i)
        
    return rv
class rcset(dict):
    def add(self, v):
        self[v] = (self.get(v, 0) + 1) 
        
    def add(self, v):
        self[v] = (self.get(v, 0) + 1) 
        
    def add(self, v):
        self[v] = (self.get(v, 0) + 1) 
        
    def remove(self, v):
        c = self.get(v) - 1 
        if c:
            self[v] -= 1
            
        else:
            del self[v]
            
        
    
class multimap(collections.defaultdict):
    def __init__(self, container):
        collections.defaultdict.__init__(self, container)
        
    def add(self, k, v):
        self[k].add(v)
        
    def remove(self, k, v):
        self[k].remove(v)
        
    
q_reverse_T = multimap(sets.Set) 
q_reverse_membership = multimap(sets.Set) 
q_reverse_S = multimap(sets.Set) 
q_R = multimap(rcset) 
q_D = dict() 
class C(object):
    def __init__(self):
        self.S = sets.Set() 
        self.T = sets.Set() 
        
    def __init__(self):
        if hasattr(self, 'S'):
            q_reverse_S.remove(id(self), self.S)
            
        for (a_inc_q_0_0_1__EXPR__,o_inc_q_0_0_1__EXPR__,o_S_inc_q_0_0_1__EXPR__,o_T_inc_q_0_0_1__EXPR__,) in q_D.values():
            q_R[id(o_inc_q_0_0_1__EXPR__)].remove(a_inc_q_0_0_1__EXPR__)
            
        q_D.clear()
        o_T__0_0_1__EXPR__ = self.T 
        for a__0_0_1__EXPR__ in o_S__0_0_1__EXPR__:
            if a__0_0_1__EXPR__ in o_T__0_0_1__EXPR__:
                q_D[(id(a__0_0_1__EXPR__),id(self),id(o_S__0_0_1__EXPR__),id(o_T__0_0_1__EXPR__))] = (a__0_0_1__EXPR__,self,o_S__0_0_1__EXPR__,o_T__0_0_1__EXPR__) 
                
            
        if hasattr(self, 'S'):
            q_reverse_S.remove(id(self), self.S)
            
        for (a_inc_q_0_1_1__EXPR__,o_inc_q_0_1_1__EXPR__,o_S_inc_q_0_1_1__EXPR__,o_T_inc_q_0_1_1__EXPR__,) in q_D.values():
            q_R[id(o_inc_q_0_1_1__EXPR__)].remove(a_inc_q_0_1_1__EXPR__)
            
        q_D.clear()
        o_T__0_1_1__EXPR__ = self.T 
        for a__0_1_1__EXPR__ in o_S__0_1_1__EXPR__:
            if a__0_1_1__EXPR__ in o_T__0_1_1__EXPR__:
                q_D[(id(a__0_1_1__EXPR__),id(self),id(o_S__0_1_1__EXPR__),id(o_T__0_1_1__EXPR__))] = (a__0_1_1__EXPR__,self,o_S__0_1_1__EXPR__,o_T__0_1_1__EXPR__) 
                
            
        self.S = sets.Set() 
        q_reverse_S.add(id(self), self.S)
        for (a_inc_q_0_1_1__EXPR__,o_inc_q_0_1_1__EXPR__,o_S_inc_q_0_1_1__EXPR__,o_T_inc_q_0_1_1__EXPR__,) in q_D.values():
            q_R[id(o_inc_q_0_1_1__EXPR__)].add(a_inc_q_0_1_1__EXPR__)
            
        q_D.clear()
        o_T__0_1_1__EXPR__ = self.T 
        for a__0_1_1__EXPR__ in o_S__0_1_1__EXPR__:
            if a__0_1_1__EXPR__ in o_T__0_1_1__EXPR__:
                q_D[(id(a__0_1_1__EXPR__),id(self),id(o_S__0_1_1__EXPR__),id(o_T__0_1_1__EXPR__))] = (a__0_1_1__EXPR__,self,o_S__0_1_1__EXPR__,o_T__0_1_1__EXPR__) 
                
            
        q_reverse_S.add(id(self), self.S)
        for (a_inc_q_0_0_1__EXPR__,o_inc_q_0_0_1__EXPR__,o_S_inc_q_0_0_1__EXPR__,o_T_inc_q_0_0_1__EXPR__,) in q_D.values():
            q_R[id(o_inc_q_0_0_1__EXPR__)].add(a_inc_q_0_0_1__EXPR__)
            
        q_D.clear()
        o_T__0_0_1__EXPR__ = self.T 
        for a__0_0_1__EXPR__ in o_S__0_0_1__EXPR__:
            if a__0_0_1__EXPR__ in o_T__0_0_1__EXPR__:
                q_D[(id(a__0_0_1__EXPR__),id(self),id(o_S__0_0_1__EXPR__),id(o_T__0_0_1__EXPR__))] = (a__0_0_1__EXPR__,self,o_S__0_0_1__EXPR__,o_T__0_0_1__EXPR__) 
                
            
        for (a_inc_q_0_0_1__EXPR__,o_inc_q_0_0_1__EXPR__,o_S_inc_q_0_0_1__EXPR__,o_T_inc_q_0_0_1__EXPR__,) in q_D.values():
            q_R[id(o_inc_q_0_0_1__EXPR__)].remove(a_inc_q_0_0_1__EXPR__)
            
        q_D.clear()
        o_S__0_0_1__EXPR__ = self.S 
        for a__0_0_1__EXPR__ in o_T__0_0_1__EXPR__:
            if a__0_0_1__EXPR__ in o_S__0_0_1__EXPR__:
                q_D[(id(a__0_0_1__EXPR__),id(self),id(o_S__0_0_1__EXPR__),id(o_T__0_0_1__EXPR__))] = (a__0_0_1__EXPR__,self,o_S__0_0_1__EXPR__,o_T__0_0_1__EXPR__) 
                
            
        q_reverse_T.remove(id(self), self.T)
        for (a_inc_q_0_1_1__EXPR__,o_inc_q_0_1_1__EXPR__,o_S_inc_q_0_1_1__EXPR__,o_T_inc_q_0_1_1__EXPR__,) in q_D.values():
            q_R[id(o_inc_q_0_1_1__EXPR__)].remove(a_inc_q_0_1_1__EXPR__)
            
        q_D.clear()
        o_S__0_1_1__EXPR__ = self.S 
        for a__0_1_1__EXPR__ in o_T__0_1_1__EXPR__:
            if a__0_1_1__EXPR__ in o_S__0_1_1__EXPR__:
                q_D[(id(a__0_1_1__EXPR__),id(self),id(o_S__0_1_1__EXPR__),id(o_T__0_1_1__EXPR__))] = (a__0_1_1__EXPR__,self,o_S__0_1_1__EXPR__,o_T__0_1_1__EXPR__) 
                
            
        q_reverse_T.remove(id(self), self.T)
        self.T = sets.Set() 
        o_S__0_1_1__EXPR__ = self.S 
        for a__0_1_1__EXPR__ in o_T__0_1_1__EXPR__:
            if a__0_1_1__EXPR__ in o_S__0_1_1__EXPR__:
                q_D[(id(a__0_1_1__EXPR__),id(self),id(o_S__0_1_1__EXPR__),id(o_T__0_1_1__EXPR__))] = (a__0_1_1__EXPR__,self,o_S__0_1_1__EXPR__,o_T__0_1_1__EXPR__) 
                
            
        for (a_inc_q_0_1_1__EXPR__,o_inc_q_0_1_1__EXPR__,o_S_inc_q_0_1_1__EXPR__,o_T_inc_q_0_1_1__EXPR__,) in q_D.values():
            q_R[id(o_inc_q_0_1_1__EXPR__)].add(a_inc_q_0_1_1__EXPR__)
            
        q_D.clear()
        q_reverse_T.add(id(self), self.T)
        o_S__0_0_1__EXPR__ = self.S 
        for a__0_0_1__EXPR__ in o_T__0_0_1__EXPR__:
            if a__0_0_1__EXPR__ in o_S__0_0_1__EXPR__:
                q_D[(id(a__0_0_1__EXPR__),id(self),id(o_S__0_0_1__EXPR__),id(o_T__0_0_1__EXPR__))] = (a__0_0_1__EXPR__,self,o_S__0_0_1__EXPR__,o_T__0_0_1__EXPR__) 
                
            
        for (a_inc_q_0_0_1__EXPR__,o_inc_q_0_0_1__EXPR__,o_S_inc_q_0_0_1__EXPR__,o_T_inc_q_0_0_1__EXPR__,) in q_D.values():
            q_R[id(o_inc_q_0_0_1__EXPR__)].add(a_inc_q_0_0_1__EXPR__)
            
        q_D.clear()
        q_reverse_T.add(id(self), self.T)
        
    
class D(object):
    pass 
d = D() 
o = C() 
o__0_0_1__EXPR__ = o 
o_S__0_0_1__EXPR__ = o__0_0_1__EXPR__.S 
o_T__0_0_1__EXPR__ = o__0_0_1__EXPR__.T 
for a__0_0_1__EXPR__ in o_S__0_0_1__EXPR__:
    if a__0_0_1__EXPR__ in o_T__0_0_1__EXPR__:
        q_D[(id(a__0_0_1__EXPR__),id(o__0_0_1__EXPR__),id(o_S__0_0_1__EXPR__),id(o_T__0_0_1__EXPR__))] = (a__0_0_1__EXPR__,o__0_0_1__EXPR__,o_S__0_0_1__EXPR__,o_T__0_0_1__EXPR__) 
        
    
for (a_inc_q_0_0_1__EXPR__,o_inc_q_0_0_1__EXPR__,o_S_inc_q_0_0_1__EXPR__,o_T_inc_q_0_0_1__EXPR__,) in q_D.values():
    q_R[id(o_inc_q_0_0_1__EXPR__)].add(a_inc_q_0_0_1__EXPR__)
    
q_D.clear()
print q_R[id(o)]
o.S.add(d)
for (a_inc_q_0_1_1__EXPR__,o_inc_q_0_1_1__EXPR__,o_S_inc_q_0_1_1__EXPR__,o_T_inc_q_0_1_1__EXPR__,) in q_D.values():
    q_R[id(o_inc_q_0_1_1__EXPR__)].add(a_inc_q_0_1_1__EXPR__)
    
q_D.clear()
q_reverse_membership.add(id(o.S), d)
for (a_inc_q_0_1_1__EXPR__,o_inc_q_0_1_1__EXPR__,o_S_inc_q_0_1_1__EXPR__,o_T_inc_q_0_1_1__EXPR__,) in q_D.values():
    q_R[id(o_inc_q_0_1_1__EXPR__)].add(a_inc_q_0_1_1__EXPR__)
    
q_D.clear()
for o_S__0_1_1__EXPR__ in q_reverse_membership[id(d)]:
    for o__0_1_1__EXPR__ in q_reverse_T[id(o.S)]:
        o_S__0_1_1__EXPR__ = o__0_1_1__EXPR__.S 
        q_D[(id(d),id(o__0_1_1__EXPR__),id(o_S__0_1_1__EXPR__),id(o.S))] = (d,o__0_1_1__EXPR__,o_S__0_1_1__EXPR__,o.S) 
        
    
for o__0_1_1__EXPR__ in q_reverse_S[id(o.S)]:
    o_T__0_1_1__EXPR__ = o__0_1_1__EXPR__.T 
    if d in o_T__0_1_1__EXPR__:
        q_D[(id(d),id(o__0_1_1__EXPR__),id(o.S),id(o_T__0_1_1__EXPR__))] = (d,o__0_1_1__EXPR__,o.S,o_T__0_1_1__EXPR__) 
        
    
for (a_inc_q_0_0_1__EXPR__,o_inc_q_0_0_1__EXPR__,o_S_inc_q_0_0_1__EXPR__,o_T_inc_q_0_0_1__EXPR__,) in q_D.values():
    q_R[id(o_inc_q_0_0_1__EXPR__)].add(a_inc_q_0_0_1__EXPR__)
    
q_D.clear()
q_reverse_membership.add(id(o.S), d)
for (a_inc_q_0_0_1__EXPR__,o_inc_q_0_0_1__EXPR__,o_S_inc_q_0_0_1__EXPR__,o_T_inc_q_0_0_1__EXPR__,) in q_D.values():
    q_R[id(o_inc_q_0_0_1__EXPR__)].add(a_inc_q_0_0_1__EXPR__)
    
q_D.clear()
for o_S__0_0_1__EXPR__ in q_reverse_membership[id(d)]:
    for o__0_0_1__EXPR__ in q_reverse_T[id(o.S)]:
        o_S__0_0_1__EXPR__ = o__0_0_1__EXPR__.S 
        q_D[(id(d),id(o__0_0_1__EXPR__),id(o_S__0_0_1__EXPR__),id(o.S))] = (d,o__0_0_1__EXPR__,o_S__0_0_1__EXPR__,o.S) 
        
    
for o__0_0_1__EXPR__ in q_reverse_S[id(o.S)]:
    o_T__0_0_1__EXPR__ = o__0_0_1__EXPR__.T 
    if d in o_T__0_0_1__EXPR__:
        q_D[(id(d),id(o__0_0_1__EXPR__),id(o.S),id(o_T__0_0_1__EXPR__))] = (d,o__0_0_1__EXPR__,o.S,o_T__0_0_1__EXPR__) 
        
    
o.T.add(d)
for (a_inc_q_0_1_1__EXPR__,o_inc_q_0_1_1__EXPR__,o_S_inc_q_0_1_1__EXPR__,o_T_inc_q_0_1_1__EXPR__,) in q_D.values():
    q_R[id(o_inc_q_0_1_1__EXPR__)].add(a_inc_q_0_1_1__EXPR__)
    
q_D.clear()
q_reverse_membership.add(id(o.T), d)
for (a_inc_q_0_1_1__EXPR__,o_inc_q_0_1_1__EXPR__,o_S_inc_q_0_1_1__EXPR__,o_T_inc_q_0_1_1__EXPR__,) in q_D.values():
    q_R[id(o_inc_q_0_1_1__EXPR__)].add(a_inc_q_0_1_1__EXPR__)
    
q_D.clear()
for o_S__0_1_1__EXPR__ in q_reverse_membership[id(d)]:
    for o__0_1_1__EXPR__ in q_reverse_T[id(o.T)]:
        o_S__0_1_1__EXPR__ = o__0_1_1__EXPR__.S 
        q_D[(id(d),id(o__0_1_1__EXPR__),id(o_S__0_1_1__EXPR__),id(o.T))] = (d,o__0_1_1__EXPR__,o_S__0_1_1__EXPR__,o.T) 
        
    
for o__0_1_1__EXPR__ in q_reverse_S[id(o.T)]:
    o_T__0_1_1__EXPR__ = o__0_1_1__EXPR__.T 
    if d in o_T__0_1_1__EXPR__:
        q_D[(id(d),id(o__0_1_1__EXPR__),id(o.T),id(o_T__0_1_1__EXPR__))] = (d,o__0_1_1__EXPR__,o.T,o_T__0_1_1__EXPR__) 
        
    
for (a_inc_q_0_0_1__EXPR__,o_inc_q_0_0_1__EXPR__,o_S_inc_q_0_0_1__EXPR__,o_T_inc_q_0_0_1__EXPR__,) in q_D.values():
    q_R[id(o_inc_q_0_0_1__EXPR__)].add(a_inc_q_0_0_1__EXPR__)
    
q_D.clear()
q_reverse_membership.add(id(o.T), d)
for (a_inc_q_0_0_1__EXPR__,o_inc_q_0_0_1__EXPR__,o_S_inc_q_0_0_1__EXPR__,o_T_inc_q_0_0_1__EXPR__,) in q_D.values():
    q_R[id(o_inc_q_0_0_1__EXPR__)].add(a_inc_q_0_0_1__EXPR__)
    
q_D.clear()
for o_S__0_0_1__EXPR__ in q_reverse_membership[id(d)]:
    for o__0_0_1__EXPR__ in q_reverse_T[id(o.T)]:
        o_S__0_0_1__EXPR__ = o__0_0_1__EXPR__.S 
        q_D[(id(d),id(o__0_0_1__EXPR__),id(o_S__0_0_1__EXPR__),id(o.T))] = (d,o__0_0_1__EXPR__,o_S__0_0_1__EXPR__,o.T) 
        
    
for o__0_0_1__EXPR__ in q_reverse_S[id(o.T)]:
    o_T__0_0_1__EXPR__ = o__0_0_1__EXPR__.T 
    if d in o_T__0_0_1__EXPR__:
        q_D[(id(d),id(o__0_0_1__EXPR__),id(o.T),id(o_T__0_0_1__EXPR__))] = (d,o__0_0_1__EXPR__,o.T,o_T__0_0_1__EXPR__) 
        
    
o__0_1_1__EXPR__ = o 
o_S__0_1_1__EXPR__ = o__0_1_1__EXPR__.S 
o_T__0_1_1__EXPR__ = o__0_1_1__EXPR__.T 
for a__0_1_1__EXPR__ in o_S__0_1_1__EXPR__:
    if a__0_1_1__EXPR__ in o_T__0_1_1__EXPR__:
        q_D[(id(a__0_1_1__EXPR__),id(o__0_1_1__EXPR__),id(o_S__0_1_1__EXPR__),id(o_T__0_1_1__EXPR__))] = (a__0_1_1__EXPR__,o__0_1_1__EXPR__,o_S__0_1_1__EXPR__,o_T__0_1_1__EXPR__) 
        
    
for (a_inc_q_0_1_1__EXPR__,o_inc_q_0_1_1__EXPR__,o_S_inc_q_0_1_1__EXPR__,o_T_inc_q_0_1_1__EXPR__,) in q_D.values():
    q_R[id(o_inc_q_0_1_1__EXPR__)].add(a_inc_q_0_1_1__EXPR__)
    
q_D.clear()
print q_R[id(o)]
