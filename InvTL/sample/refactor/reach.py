import random
def setGeneralized(L):
    s=0
    #for k in L: s=s+len(k)
    #print "T1",s
    r = set([]) 
    for l in L:
        r.union_update(l)
    #print "T2",len(r)    
    return r

class Reach:
    def __init__ (self):
        self.G=set()
    def findSuc(self,s):
        res=set([v for (k,v) in self.G if k==s])
        return res
    def buildGraph (self,E):
        for k,v in E.items():
            for i in v:
                arg=(k,i)
                self.G.add(arg)
    def Reach(self,start):
        self.reach=set()
        s=0
        s2=0
        while True:
            S=setGeneralized([self.findSuc(y) for y in self.reach if True])
            S = S.union(set([start])) 
            S = S.difference(self.reach) 
            #print len(S)
            for k in S:
                #s=s+1
                self.reach.add(k)
            if len(S)==0:
                break
        #print "S:  ",s
        #print "S2: ",s2
        return self.reach


#test()
