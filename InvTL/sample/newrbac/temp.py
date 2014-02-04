from CoreRBAC import CoreRBAC
class MultiMap:
    def __init__(self):
        self.dct = {}  
        
    def get(self, k):
        try:
            if k in self.dct:
                return self.dct[k]
            else:
                return set()
            
        except:
            return set()
        
        
    def add(self, k, v):
        if k not in self.dct:
            self.dct[k] = s = set() 
            s.add(v)
            
        else:
            self.dct[k].add(v)
            
        
    def remove(self, k, v):
        if k in self.dct:
            s = self.dct[k] 
            s.remove(v)
            if  not s:
                del self.dct[k]
                
            
        
    
class GeneralHierRBAC(CoreRBAC):
    def __init__(self):
        self.OBJS = set() 
        self.OPS = set() 
        self.USERS = set() 
        self.MAP1_0_0_1__EXPR__ = MultiMap() 
        self.ROLES = set() 
        self.MAP1_0_0_1__EXPR__ = MultiMap() 
        self.PR = set() 
        self.UR = set() 
        self.MAP2_0_0_1__EXPR__ = MultiMap() 
        self.MAP4_0_0_1__EXPR__ = MultiMap() 
        self.MAP1_0_0_1__EXPR__ = MultiMap() 
        self.SESSIONS = set() 
        self.SU = set() 
        self.SR = set() 
        self.INH = set() 
        self.TRANS_0_0_1__EXPR__ = self.trans(self.INH) 
        self.MAP3_0_0_1__EXPR__ = MultiMap() 
        self.MAP1_0_0_1__EXPR__ = MultiMap() 
        self.TRANS_0_0_1__EXPR__ = set() 
        self.MAP1_0_0_1__EXPR__ = MultiMap() 
        self.MAP2_0_0_1__EXPR__ = MultiMap() 
        self.MAP3_0_0_1__EXPR__ = MultiMap() 
        self.MAP4_0_0_1__EXPR__ = MultiMap() 
        
    def AddUser(self, user):
        assert user not in self.USERS
        self.USERS.add(user)
        
    def DeleteUser(self, user):
        assert user in self.USERS
        self.UR -= set(((user,r) for r in self.ROLES))
        for s in set((s for s in self.SESSIONS if (s,user) in self.SU)):
            self.DeleteSession(user, s)
            
        self.USERS.remove(user)
        
    def AddRole(self, role):
        assert role not in self.ROLES
        self.ROLES.add(role)
        for u in self.MAP2_0_0_1__EXPR__.get(role):
            if u in self.USERS:
                for r in self.MAP3_0_0_1__EXPR__.get(role):
                    if u not in self.MAP1_0_0_1__EXPR__.get(r):
                        self.MAP1_0_0_1__EXPR__.add(r, u)
                        
                    
                
            
        
    def DeleteRole(self, role):
        assert role in self.ROLES
        for u in self.MAP2_0_0_1__EXPR__.get(role):
            if u in self.USERS:
                for r in self.MAP3_0_0_1__EXPR__.get(role):
                    if u in self.MAP1_0_0_1__EXPR__.get(r):
                        self.MAP1_0_0_1__EXPR__.remove(r, u)
                        
                    
                
            
        self.ROLES.remove(role)
        self.PR -= set((((op,obj),role) for op in self.OPS for obj in self.OBJS))
        self.UR -= set(((u,role) for u in self.USERS))
        for (s,u,) in set(((s,u) for s in self.SESSIONS for u in self.USERS if (s,u) in self.SU and (s,role) in self.SR)):
            self.DeleteSession(u, s)
            
        
    def AssignUser(self, user, role):
        assert user in self.USERS
        assert role in self.ROLES
        assert (user,role) not in self.UR
        self.UR.add((user,role))
        
    def DeassignUser(self, user, role):
        assert user in self.USERS
        assert role in self.ROLES
        assert (user,role) in self.UR
        self.UR.remove((user,role))
        for s in set((s for s in self.SESSIONS if (s,user) in self.SU and (s,role) in self.SR)):
            self.DeleteSession(user, s)
            
        
    def GrantPermission(self, operation, object, role):
        assert operation in self.OPS and object in self.OBJS
        assert role in self.ROLES
        assert ((operation,object),role) not in self.PR
        self.PR.add(((operation,object),role))
        
    def RevokePermission(self, operation, object, role):
        assert operation in self.OPS and object in self.OBJS
        assert role in self.ROLES
        assert ((operation,object),role) in self.PR
        self.PR.remove(((operation,object),role))
        
    def CreateSession(self, user, session, ars):
        assert user in self.USERS
        assert session not in self.SESSIONS
        assert ars.issubset(self.AssignedRoles(user))
        self.SU.add((session,user))
        for r in ars:
            self.SR.add((session,r))
            
        self.SESSIONS.add(session)
        
    def DeleteSession(self, user, session):
        assert user in self.USERS
        assert session in self.SESSIONS
        assert (session,user) in self.SU
        self.SU.remove((session,user))
        self.SR -= set(((session,r) for r in self.ROLES))
        self.SESSIONS.remove(session)
        
    def AddActiveRole(self, user, session, role):
        assert user in self.USERS
        assert session in self.SESSIONS
        assert role in self.ROLES
        assert (session,user) in self.SU
        assert (session,role) not in self.SR
        assert role in self.AssignedRoles(user)
        self.SR.add((session,role))
        
    def DropActiveRole(self, user, session, role):
        assert user in self.USERS
        assert session in self.SESSIONS
        assert role in self.ROLES
        assert (session,user) in self.SU
        assert (session,role) in self.SR
        self.SR.remove((session,role))
        
    def CheckAccess(self, session, operation, object):
        assert session in self.SESSIONS
        assert operation in self.OPS
        assert object in self.OBJS
        return bool(set((r for r in self.ROLES if (session,r) in self.SR and ((operation,object),r) in self.PR)))
    def AssignedUsers(self, role):
        assert role in self.ROLES
        return set((u for u in self.USERS if (u,role) in self.UR))
    def AssignedRoles(self, user):
        assert user in self.USERS
        return set((r for r in self.ROLES if (user,r) in self.UR))
    def RolePermissions(self, role):
        assert role in self.ROLES
        return set(((op,obj) for op in self.OPS for obj in self.OBJS if ((op,obj),role) in self.PR))
    def UserPermissions(self, user):
        assert user in self.USERS
        return set(((op,obj) for r in self.ROLES for op in self.OPS for obj in self.OBJS if (user,r) in self.UR and ((op,obj),r) in self.PR))
    def SessionRoles(self, session):
        assert session in self.SESSIONS
        return set((r for r in self.ROLES if (session,r) in self.SR))
    def SessionPermissions(self, session):
        assert session in self.SESSIONS
        return set(((op,obj) for r in self.ROLES for op in self.OPS for obj in self.OBJS if (session,r) in self.SR and ((op,obj),r) in self.PR))
    def RoleOperationsOnObject(self, role, obj):
        assert role in self.ROLES
        assert obj in self.OBJS
        return set((op for op in self.OPS if ((op,obj),role) in self.PR))
    def UserOperationsOnObject(self, user, obj):
        assert user in self.USERS
        assert obj in self.OBJS
        return set((op for op in self.OPS for r in self.ROLES if (user,r) in self.UR and ((op,obj),r) in self.PR))
    def AddOperation(self, operation):
        self.OPS.add(operation)
        
    def AddObject(self, OBJ):
        self.OBJS.add(OBJ)
        
    def AddPermission(self, operation, obj):
        pass 
    def trans(self, INH):
        T = set(INH) 
        W = set(((x,b) for (x,y,) in T for (h,b,) in INH if y == h)) - T 
        while bool(W):
            T.add(W.pop())
            W = set(((x,b) for (x,y,) in T for (h,b,) in INH if y == h)) - T 
            
        return T | set(((r,r) for r in self.ROLES))
    def AddInheritance(self, heir, bearer):
        assert heir in self.ROLES
        assert bearer in self.ROLES
        assert (heir,bearer) not in self.INH
        assert heir != bearer
        assert (bearer,heir) not in self.trans(self.INH)
        self.INH.add((heir,bearer))
        TNEW_0_0_1__EXPR__ = self.trans(self.INH) 
        TDIFF1_0_0_1__EXPR__ = TNEW_0_0_1__EXPR__ - self.TRANS_0_0_1__EXPR__ 
        TDIFF2_0_0_1__EXPR__ = self.TRANS_0_0_1__EXPR__ - TNEW_0_0_1__EXPR__ 
        for (s,r,) in TDIFF1_0_0_1__EXPR__:
            for u in self.MAP2_0_0_1__EXPR__.get(s):
                if s in self.ROLES:
                    if u in self.USERS:
                        if u not in self.MAP1_0_0_1__EXPR__.get(r):
                            self.MAP1_0_0_1__EXPR__.add(r, u)
                            
                        
                    
                
            
        for (s,r,) in TDIFF2_0_0_1__EXPR__:
            for u in self.MAP2_0_0_1__EXPR__.get(s):
                if s in self.ROLES:
                    if u in self.USERS:
                        if u in self.MAP1_0_0_1__EXPR__.get(r):
                            self.MAP1_0_0_1__EXPR__.remove(r, u)
                            
                        
                    
                
            
        self.TRANS_0_0_1__EXPR__ = TNEW_0_0_1__EXPR__ 
        
    def DeleteInheritance(self, heir, bearer):
        assert heir in self.ROLES
        assert bearer in self.ROLES
        assert (heir,bearer) in self.INH
        self.INH.remove((heir,bearer))
        TNEW_0_0_1__EXPR__ = self.trans(self.INH) 
        TDIFF1_0_0_1__EXPR__ = TNEW_0_0_1__EXPR__ - self.TRANS_0_0_1__EXPR__ 
        TDIFF2_0_0_1__EXPR__ = self.TRANS_0_0_1__EXPR__ - TNEW_0_0_1__EXPR__ 
        for (s,r,) in TDIFF1_0_0_1__EXPR__:
            for u in self.MAP2_0_0_1__EXPR__.get(s):
                if s in self.ROLES:
                    if u in self.USERS:
                        if u not in self.MAP1_0_0_1__EXPR__.get(r):
                            self.MAP1_0_0_1__EXPR__.add(r, u)
                            
                        
                    
                
            
        for (s,r,) in TDIFF2_0_0_1__EXPR__:
            for u in self.MAP2_0_0_1__EXPR__.get(s):
                if s in self.ROLES:
                    if u in self.USERS:
                        if u in self.MAP1_0_0_1__EXPR__.get(r):
                            self.MAP1_0_0_1__EXPR__.remove(r, u)
                            
                        
                    
                
            
        self.TRANS_0_0_1__EXPR__ = TNEW_0_0_1__EXPR__ 
        
    def AddAscendant(self, heir, bearer):
        self.AddRole(heir)
        self.AddInheritance(heir, bearer)
        
    def AddDescendant(self, bearer, heir):
        self.AddRole(bearer)
        self.AddInheritance(heir, bearer)
        
    def CreateSession(self, user, session, ars):
        assert user in self.USERS
        assert session not in self.SESSIONS
        assert ars.issubset(self.AuthorizedRoles(user))
        self.SU.add((session,user))
        for r in ars:
            self.SR.add((session,r))
            
        self.SESSIONS.add(session)
        
    def AddActiveRole(self, user, session, role):
        assert user in self.USERS
        assert session in self.SESSIONS
        assert role in self.ROLES
        assert (session,user) in self.SU
        assert (session,role) not in self.SR
        assert role in self.AuthorizedRoles(user)
        self.SR.add((session,role))
        
    def AuthorizedUsers(self, role):
        assert role in self.ROLES
        return self.MAP1_0_0_1__EXPR__.get(role)
    def AuthorizedRoles(self, user):
        assert user in self.USERS
        return set((r for heir in self.ROLES for r in self.ROLES if (user,heir) in self.UR and (heir,r) in self.trans(self.INH)))
    def RolePermissions(self, role):
        assert role in self.ROLES
        return set(((op,obj) for bearer in self.ROLES for op in self.OPS for obj in self.OBJS if (role,bearer) in self.trans(self.INH) and ((op,obj),bearer) in self.PR))
    def UserPermissions(self, user):
        assert user in self.USERS
        return set(((op,obj) for heir in self.ROLES for bearer in self.ROLES for op in self.OPS for obj in self.OBJS if (user,heir) in self.UR and (heir,bearer) in self.trans(self.INH) and ((op,obj),bearer) in self.PR))
    def RoleOperationsOnObject(self, role, object):
        assert role in self.ROLES, object in self.OBJS
        return set((op for bearer in self.ROLES for op in self.OPS if (role,bearer) in self.trans(self.INH) and ((op,object),bearer) in self.PR))
    def UserOperationsOnObject(self, user, object):
        assert user in self.USERS, object in self.OBJS
        return set((op for heir in self.ROLES for bearer in self.ROLES for op in self.OPS if (user,heir) in self.UR and (heir,bearer) in self.trans(self.INH) and ((op,object),bearer) in self.PR))
    
class LimitedHierRBAC(GeneralHierRBAC):
    def __init__(self):
        GeneralHierRBAC.__init__(self)
        
    def AddInheritance(self, heir, bearer):
        assert  not bool(set((r for r in self.ROLES if (heir,r) in self.INH)))
        GeneralHierRBAC.AddInheritance(self, heir, bearer)
        
    
class CoreRBACwithSSD(CoreRBAC):
    def __init__(self):
        CoreRBAC.__init__(self)
        self.SsdNAMES = set() 
        self.SsdNR = set() 
        self.SsdNC = set() 
        
    def checkSSD(self, SsdNR, SsdNC):
        return  not bool(set((True for u in self.USERS for (name,c,) in SsdNC if  not len(set((r for r in self.AssignedRoles(u) if (name,r) in SsdNR))) <= c)))
    def AssignUser(self, user, role):
        assert  not bool(set((True for (name,c,) in self.SsdNC if  not len(set((r for r in self.ROLES if (user,r) in self.UR | set([(user,role)]) and (name,r) in self.SsdNR))) <= c)))
        CoreRBAC.AssignUser(self, user, role)
        
    def CreateSsdSet(self, name, roles, c):
        assert name not in self.SsdNAMES
        assert roles.issubset(self.ROLES)
        assert 1 <= c <= len(roles) - 1
        assert self.checkSSD(self.SsdNR | set(((name,r) for r in roles)), self.SsdNC | set([(name,c)]))
        self.SsdNAMES.add(name)
        self.SsdNR |= set(((name,r) for r in roles))
        self.SsdNC.add((name,c))
        
    def DeleteSsdSet(self, name):
        assert name in self.SsdNAMES
        self.SsdNR -= set(((name,r) for r in self.SsdRoleSetRoles(name)))
        self.SsdNC.remove((name,self.SsdRoleSetCardinality(name)))
        self.SsdNAMES.remove(name)
        
    def AddSsdRoleMember(self, name, role):
        assert name in self.SsdNAMES
        assert role in self.ROLES
        assert role not in self.SsdRoleSetRoles(name)
        assert self.checkSSD(self.SsdNR | set([(name,role)]), self.SsdNC)
        self.SsdNR.add((name,role))
        
    def DeleteSsdRoleMember(self, name, role):
        assert name in self.SsdNAMES
        assert role in self.SsdRoleSetRoles(name)
        assert self.SsdRoleSetCardinality(name) <= len(self.SsdRoleSetRoles(name)) - 2
        self.SsdNR.remove((name,role))
        
    def SetSsdSetCardinality(self, name, c):
        assert name in self.SsdNAMES
        assert 1 <= c <= len(self.SsdRoleSetRoles(name)) - 1
        assert self.checkSSD(self.SsdNR, self.SsdNC - set((name,self.SsdRoleSetCardinality(name))) | set([(name,c)]))
        self.SsdNC.remove((name,self.SsdRoleSetCardinality(name)))
        self.SsdNC.add((name,c))
        
    def SsdRoleSets(self):
        return self.SsdNAMES
    def SsdRoleSetRoles(self, name):
        assert name in self.SsdNAMES
        return set((r for (n,r,) in self.SsdNR if n == name))
    def SsdRoleSetCardinality(self, name):
        assert name in self.SsdNAMES
        return set((c for (n,c,) in self.SsdNC if n == name)).pop()
    
class GeneralHierRBACwithSSD(GeneralHierRBAC,CoreRBACwithSSD):
    def __init__(self):
        GeneralHierRBAC.__init__(self)
        CoreRBACwithSSD.__init__(self)
        
    def checkSSD(self, SsdNR, SsdNC):
        return  not bool(set((True for u in self.USERS for (name,c,) in SsdNC if  not len(set((r for r in self.AuthorizedRoles(u) if (name,r) in SsdNR))) <= c)))
    def AddInheritance(self, heir, bearer):
        assert  not bool(set((True for u in self.USERS for (name,c,) in self.SsdNC if  not len(set((r for heir in self.ROLES for r in self.ROLES if (u,heir) in self.UR and (heir,r) in self.trans(self.INH | set([(heir,bearer)])) and (name,r) in self.SsdNR))) <= c)))
        GeneralHierRBAC.AddInheritance(self, heir, bearer)
        
    
class LimitedHierRBACwithSSD(GeneralHierRBACwithSSD):
    def __init__(self):
        GeneralHierRBACwithSSD.__init__(self)
        
    def AddInheritance(self, heir, bearer):
        assert  not set((r for r in self.ROLES if (heir,r) in self.INH))
        GeneralHierRBACwithSSD.AddInheritance(self, heir, bearer)
        
    
class CoreRBACwithDSD(CoreRBAC):
    def __init__(self):
        CoreRBAC.__init__(self)
        self.DsdNAMES = set() 
        self.DsdNR = set() 
        self.DsdNC = set() 
        
    def checkDSD(self, DsdNR, DsdNC):
        return  not bool(set((True for s in self.SESSIONS for (name,c,) in DsdNC if  not len(set((r for r in self.SessionRoles(s) if (name,r) in DsdNR))) <= c)))
    def CreateDsdSet(self, name, roles, c):
        assert name not in self.DsdNAMES
        assert roles.issubset(self.ROLES)
        assert 1 <= c <= len(roles) - 1
        assert self.checkDSD(self.DsdNR | set(((name,r) for r in roles)), self.DsdNC | set([(name,c)]))
        self.DsdNAMES.add(name)
        self.DsdNR |= set(((name,r) for r in roles))
        self.DsdNC.add((name,c))
        
    def DeleteDsdSet(self, name):
        assert name in self.DsdNAMES
        self.DsdNR -= set(((name,r) for r in self.DsdRoleSetRoles(name)))
        self.DsdNC.remove((name,self.DsdRoleSetCardinality(name)))
        self.DsdNAMES.remove(name)
        
    def AddDsdRoleMember(self, name, role):
        assert name in self.DsdNAMES
        assert role in self.ROLES
        assert role not in self.DsdRoleSetRoles(name)
        assert self.checkDSD(self.DsdNR | set([(name,role)]), self.DsdNC)
        self.DsdNR.add((name,role))
        
    def DeleteDsdRoleMember(self, name, role):
        assert name in self.DsdNAMES
        assert role in self.DsdRoleSetRoles(name)
        assert self.DsdRoleSetCardinality(name) <= len(self.DsdRoleSetRoles(name)) - 2
        self.DsdNR.remove((name,role))
        
    def SetDsdSetCardinality(self, name, c):
        assert name in self.DsdNAMES
        assert 1 <= c <= len(self.DsdRoleSetRoles(name)) - 1
        assert self.checkDSD(self.DsdNR, self.DsdNC - set((name,self.DsdRoleSetCardinality(name))) | set([(name,c)]))
        self.DsdNC.remove((name,self.DsdRoleSetCardinality(name)))
        self.DsdNC.add((name,c))
        
    def CreateSession(self, user, session, ars):
        assert  not bool(set((True for s in self.SESSIONS for (name,c,) in self.DsdNC if  not len(set((r for r in self.ROLES if (s,r) in self.SR | set(((session,r) for r in ars)) and (name,r) in self.DsdNR))) <= c)))
        CoreRBAC.CreateSession(self, user, session, ars)
        
    def AddActiveRole(self, user, session, role):
        assert  not bool(set((True for s in self.SESSIONS for (name,c,) in self.DsdNC if  not len(set((r for r in self.ROLES if (s,r) in self.SR | set([(session,role)]) and (name,r) in self.DsdNR))) <= c)))
        CoreRBAC.AddActiveRole(self, user, session, role)
        
    def DsdRoleSets(self):
        return self.DsdNAMES
    def DsdRoleSetRoles(self, name):
        assert name in self.DsdNAMES
        return set((r for (n,r,) in self.DsdNR if n == name))
    def DsdRoleSetCardinality(self, name):
        assert name in self.DsdNAMES
        return set((c for (n,c,) in self.DsdNC if n == name)).pop()
    
class GeneralHierRBACwithDSD(GeneralHierRBAC,CoreRBACwithDSD):
    def __init__(self):
        GeneralHierRBAC.__init__(self)
        CoreRBACwithDSD.__init__(self)
        
    def CreateSession(self, user, session, ars):
        print user, session, ars, self.SESSIONS, self.SR, self.DsdNC, self.DsdNR
        assert  not bool(set((True for (name,c,) in self.DsdNC if  not len(set((r for r in self.ROLES if (session,r) in self.SR | set(((session,r) for r in ars)) and (name,r) in self.DsdNR))) <= c)))
        GeneralHierRBAC.CreateSession(self, user, session, ars)
        
    def AddActiveRole(self, user, session, role):
        assert  not bool(set((True for s in self.SESSIONS for (name,c,) in self.DsdNC if  not len(set((r for r in self.ROLES if (s,r) in self.SR | set([(session,role)]) and (name,r) in self.DsdNR))) <= c)))
        GeneralHierRBAC.AddActiveRole(self, user, session, role)
        
    
class LimitedHierRBACwithDSD(GeneralHierRBACwithDSD):
    def __init__(self):
        GeneralHierRBACwithDSD.__init__(self)
        
    def AddInheritance(self, heir, bearer):
        LimitedHierRBAC.AddInheritance(self, heir, bearer)
        
    

