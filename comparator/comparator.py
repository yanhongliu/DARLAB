import re
import random
from collections import defaultdict
import sys
import __builtin__


#SET MODULES HERE
MODULES=[("RBAC",lambda module: module.coreRBAC())]



class RollbackImporter:
    def __init__(self):
        self.previousModules = sys.modules.copy()
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import
        self.newModules = {}
        
    def _import(self, name, globals=None, locals=None, fromlist=[]):
        result = apply(self.realImport, (name, globals, locals, fromlist))
        self.newModules[name] = 1
        return result
    def stop(self):
        __builtin__.__import__ = self.realImport
    def start(self):
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import

    def uninstall(self):
        for modname in self.newModules.keys():
            if not self.previousModules.has_key(modname):
                # Force reload when modname next imported
                try:
                    del(sys.modules[modname])
                except:
                    print "Cannot unload module: %s"%modname
                    pass
        __builtin__.__import__ = self.realImport

OpsQueue=[]


try:
    loaded_rollbackImporter["\\\\"]=None
except:
    loaded_rollbackImporter={}


users = set("U%d"%i for i in range(10000))
roles = set("R%d"%i for i in range(10000))
ops =   set("ob%d"%i for i in range(1000)) 
objs =  set("op%d"%i for i in range(1000000))

def seq(objs,count):
    return random.sample(objs,count)

def runScenario(S):
    modules=[i[1](__import__(i[0]))  for i in MODULES]
    for s in S:
        res=[eval("m.%s"%s[1])(*(s[2:][0])) for m in modules]
        if s[0]=='s':
            pass
        if s[0]=='c':
            first=res[0]
            print first
            return all([first==i for i in res])

def scenario1():
    U  = seq(users,100)
    R  = seq(roles,10)
    OP =seq(ops,100)
    OB =seq(objs,1000)

    state=defaultdict(set)
    checkstate=[False]

    Q=[]
    def rand(key):
        return random.sample(state[key],1)[0] 
    def queue(action,target,RBAC):
        checkstate[0]=False
        def add(key,val):
            state[key].add(val)
        def remove(key,val):
            state[key].remove(val)
        def run(args):
            def rand(key):
                return random.sample(state[key],1)[0][0]
            if isinstance(args,list):
                return eval(args[0])(*[run(arg) for arg in args[1:]])
            return args
        def check(*args):
            checkstate[0]=True

        flattened=False
        args=tuple([run(arg) for arg in RBAC[1:]])
        #if len(args)==1:
        #    flattened=True
        #    args=args[0]
        #print target,tuple(args)
        eval(action)(target,args)
        if checkstate[0]:
            Q.append(("c",RBAC[0],tuple(args))) #Check
        else:
            Q.append(("s",RBAC[0],tuple(args))) #Synchro execution
        
        
    for i in U:          queue('add','U',["AddUser",i])
    for i in R:          queue('add','R',["AddRole",i])
    for i in OP:         queue('add','OP',["AddOperation",i])
    for i in OB:         queue('add','OB',["AddObject",i])
    
    for i in range(10):  queue('add','P',
                              ["GrantPermission",
                               ['rand','OP'],
                               ['rand','OB'],
                               ['rand','R'],
                              ]
                              )

    for i in range(10): queue('add','UR',
                                    ['AssignUser',
                                     ['rand','U'],
                                     ['rand','R']
                                    ]
                              )

    for i in range(10): 
        (u,r) = rand('UR')
        queue('add','S', 
                               ["CreateSession",
                                u,
                                'S%d'%i,
                                frozenset((r,))
                               ]
             )


    for i in range(1000000): 
                (u,sname,rs)=rand('S')
                queue('check',None,
                    ["CheckAccess",
                     sname,
                     ['rand','OP'],
                     ['rand','OB']
                    ]
                   )

    return Q

    
#z=re.sub(r"\$(.*?)\$(.*?)\$",replfunc,execstring)
#print z

s=scenario1()

runScenario(s)

