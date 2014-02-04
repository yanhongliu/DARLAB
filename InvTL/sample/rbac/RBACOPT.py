class MultiMap:
    def __init__(self):
        self.dct = {}  
        
    def get(self, k):
        if k in self.dct:
            return self.dct[k]
        else:
            return set()
        
    def __getitem__(self, k):
        return self.get(k)
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
                
            
        
    
class coreRBAC:
    def __init__(self):
        self.OBJS = set() 
        self.MapR2P_12_0_1__EXPR__ = MultiMap() 
        self.OPS = set() 
        self.MapRO2A_13_1_1__EXPR__ = MultiMap() 
        self.MapRO2A_13_0_1__EXPR__ = MultiMap() 
        self.MapR2P_12_0_1__EXPR__ = MultiMap() 
        self.USERS = set() 
        self.MapR2SU_16_0_1__EXPR__ = MultiMap() 
        self.V_5_1_1__EXPR__ = MultiMap() 
        self.Y_5_1_1__EXPR__ = MultiMap() 
        self.X_5_1_1__EXPR__ = MultiMap() 
        self.V_5_0_1__EXPR__ = MultiMap() 
        self.Y_5_0_1__EXPR__ = MultiMap() 
        self.X_5_0_1__EXPR__ = MultiMap() 
        self.ROLES = set() 
        self.MapS2P_18_0_1__EXPR__ = MultiMap() 
        self.SRMapR2S_18_0_1__EXPR__ = MultiMap() 
        self.PRMapR2P_18_0_1__EXPR__ = MultiMap() 
        self.MapU2P_17_0_1__EXPR__ = MultiMap() 
        self.URMapR2U = MultiMap() 
        self.PRMapR2P_17_0_1__EXPR__ = MultiMap() 
        self.MapS2R_10_0_1__EXPR__ = MultiMap() 
        self.MapU2R_9_0_1__EXPR__ = MultiMap() 
        self.MapSP2R = MultiMap() 
        self.PR = set() 
        self.MapS2P_18_0_1__EXPR__ = MultiMap() 
        self.PRMapR2P_18_0_1__EXPR__ = MultiMap() 
        self.MapU2P_17_0_1__EXPR__ = MultiMap() 
        self.PRMapR2P_17_0_1__EXPR__ = MultiMap() 
        self.MapRO2A_13_1_1__EXPR__ = MultiMap() 
        self.MapRO2A_13_0_1__EXPR__ = MultiMap() 
        self.MapR2P_12_0_1__EXPR__ = MultiMap() 
        self.MapSP2R = MultiMap() 
        self.PRMapR2P = MultiMap() 
        self.UR = set() 
        self.MapU2P_17_0_1__EXPR__ = MultiMap() 
        self.URMapR2U = MultiMap() 
        self.MapU2R_9_0_1__EXPR__ = MultiMap() 
        self.URMapR2U = MultiMap() 
        self.MapR2U_5_1_1__EXPR__ = MultiMap() 
        self.MapR2U_5_0_1__EXPR__ = MultiMap() 
        self.SESSIONS = set() 
        self.MapR2SU_16_0_1__EXPR__ = MultiMap() 
        self.MapUR2S_15_0_1__EXPR__ = MultiMap() 
        self.MapU2S_14_0_1__EXPR__ = MultiMap() 
        self.SU = set() 
        self.SUMapS2U_16_0_1__EXPR__ = MultiMap() 
        self.SUMapU2S_16_0_1__EXPR__ = MultiMap() 
        self.MapR2SU_16_0_1__EXPR__ = MultiMap() 
        self.MapUR2S_15_0_1__EXPR__ = MultiMap() 
        self.SUMapS2U_15_0_1__EXPR__ = MultiMap() 
        self.MapU2S_14_0_1__EXPR__ = MultiMap() 
        self.SUMapS2U_14_0_1__EXPR__ = MultiMap() 
        self.SR = set() 
        self.MapU2P_18_0_1__EXPR__ = MultiMap() 
        self.SRMapR2S_18_0_1__EXPR__ = MultiMap() 
        self.SRMapS2R = MultiMap() 
        self.MapR2SU_16_0_1__EXPR__ = MultiMap() 
        self.MapUR2S_15_0_1__EXPR__ = MultiMap() 
        self.SRMapS2R = MultiMap() 
        self.MapS2R_10_0_1__EXPR__ = MultiMap() 
        self.SRMapR2S_10_0_1__EXPR__ = MultiMap() 
        self.MapSP2R = MultiMap() 
        self.SRMapR2S = MultiMap() 
        self.SsdNAMES = set() 
        self.SsdNR = set() 
        self.MapN2R_6_0_1__EXPR__ = MultiMap() 
        self.MapR2N_5_1_1__EXPR__ = MultiMap() 
        self.MapR2N_5_0_1__EXPR__ = MultiMap() 
        self.SsdNC = set() 
        self.MapN2C_7_0_1__EXPR__ = MultiMap() 
        self.MapN2C_5_1_1__EXPR__ = MultiMap() 
        self.MapN2C_5_0_1__EXPR__ = MultiMap() 
        
    def AddUser(self, user):
        assert user not in self.USERS
        self.USERS.add(user)
        for s in self.SUMapU2S_16_0_1__EXPR__.get(user):
            if s in self.SESSIONS:
                for r in self.SRMapS2R.get(s):
                    if (s,user) not in self.MapR2SU_16_0_1__EXPR__.get(r):
                        self.MapR2SU_16_0_1__EXPR__.add(r, (s,user))
                        
                    
                
            
        for (name_5_1_1__EXPR__,c_5_1_1__EXPR__,) in self.SsdNC:
            if len(self.X_5_1_1__EXPR__[(user,name_5_1_1__EXPR__)]) > c_5_1_1__EXPR__:
                self.V_5_1_1__EXPR__.add(user)
                
            
        for (name_5_0_1__EXPR__,c_5_0_1__EXPR__,) in self.SsdNC:
            if len(self.X_5_0_1__EXPR__[(user,name_5_0_1__EXPR__)]) > c_5_0_1__EXPR__:
                self.V_5_0_1__EXPR__.add(user)
                
            
        
    def DeleteUser(self, user):
        assert user in self.USERS
        for r in self.URMapU2R.get(user).copy():
            if r in self.ROLES:
                if r in self.Y_5_0_1__EXPR__[user]:
                    for name_5_0_1__EXPR__ in self.MapR2N_5_0_1__EXPR__[r]:
                        if user in self.USERS:
                            for c_5_0_1__EXPR__ in self.MapN2C_5_0_1__EXPR__[name_5_0_1__EXPR__]:
                                if len(self.X_5_0_1__EXPR__[(user,name_5_0_1__EXPR__)]) > c_5_0_1__EXPR__:
                                    self.V_5_0_1__EXPR__.remove(user)
                                    
                                
                            
                        self.X_5_0_1__EXPR__.remove((user,name_5_0_1__EXPR__), r)
                        
                    
                self.Y_5_0_1__EXPR__.remove(user, r)
                
            self.MapR2U_5_0_1__EXPR__.remove(r, user)
            if r in self.ROLES:
                if r in self.Y_5_1_1__EXPR__[user]:
                    for name_5_1_1__EXPR__ in self.MapR2N_5_1_1__EXPR__[r]:
                        if user in self.USERS:
                            for c_5_1_1__EXPR__ in self.MapN2C_5_1_1__EXPR__[name_5_1_1__EXPR__]:
                                if len(self.X_5_1_1__EXPR__[(user,name_5_1_1__EXPR__)]) > c_5_1_1__EXPR__:
                                    self.V_5_1_1__EXPR__.remove(user)
                                    
                                
                            
                        self.X_5_1_1__EXPR__.remove((user,name_5_1_1__EXPR__), r)
                        
                    
                self.Y_5_1_1__EXPR__.remove(user, r)
                
            self.MapR2U_5_1_1__EXPR__.remove(r, user)
            if r in self.ROLES:
                if r in self.MapU2R_9_0_1__EXPR__.get(user):
                    self.MapU2R_9_0_1__EXPR__.remove(user, r)
                    
                
            self.URMapR2U.remove(r, user)
            for (op,obj,) in self.PRMapR2P_17_0_1__EXPR__.get(r):
                if op in self.OPS:
                    if obj in self.OBJS:
                        if (op,obj) in self.MapU2P_17_0_1__EXPR__.get(user):
                            self.MapU2P_17_0_1__EXPR__.remove(user, (op,obj))
                            
                        
                    
                
            self.URMapR2U.remove(r, user)
            self.UR.remove((user,r))
            
        for s in self.MapU2S_14_0_1__EXPR__.get(user):
            self.DeleteSession(user, s)
            
        for (name_5_0_1__EXPR__,c_5_0_1__EXPR__,) in self.SsdNC:
            if len(self.X_5_0_1__EXPR__[(user,name_5_0_1__EXPR__)]) > c_5_0_1__EXPR__:
                self.V_5_0_1__EXPR__.remove(user)
                
            
        for (name_5_1_1__EXPR__,c_5_1_1__EXPR__,) in self.SsdNC:
            if len(self.X_5_1_1__EXPR__[(user,name_5_1_1__EXPR__)]) > c_5_1_1__EXPR__:
                self.V_5_1_1__EXPR__.remove(user)
                
            
        for s in self.SUMapU2S_16_0_1__EXPR__.get(user):
            if s in self.SESSIONS:
                for r in self.SRMapS2R.get(s):
                    if (s,user) in self.MapR2SU_16_0_1__EXPR__.get(r):
                        self.MapR2SU_16_0_1__EXPR__.remove(r, (s,user))
                        
                    
                
            
        self.USERS.remove(user)
        
    def AddRole(self, role):
        assert role not in self.ROLES
        self.ROLES.add(role)
        for (op,obj,) in self.PRMapR2P_18_0_1__EXPR__.get(role):
            for s in self.SRMapR2S_18_0_1__EXPR__.get(role):
                if op in self.OPS:
                    if obj in self.OBJS:
                        if (op,obj) not in self.MapS2P_18_0_1__EXPR__.get(s):
                            self.MapS2P_18_0_1__EXPR__.add(s, (op,obj))
                            
                        
                    
                
            
        for (op,obj,) in self.PRMapR2P_17_0_1__EXPR__.get(role):
            for u in self.URMapR2U.get(role):
                if op in self.OPS:
                    if obj in self.OBJS:
                        if (op,obj) not in self.MapU2P_17_0_1__EXPR__.get(u):
                            self.MapU2P_17_0_1__EXPR__.add(u, (op,obj))
                            
                        
                    
                
            
        for s in self.SRMapR2S_10_0_1__EXPR__.get(role):
            if role not in self.MapS2R_10_0_1__EXPR__.get(s):
                self.MapS2R_10_0_1__EXPR__.add(s, role)
                
            
        for u in self.URMapR2U.get(role):
            if role not in self.MapU2R_9_0_1__EXPR__.get(u):
                self.MapU2R_9_0_1__EXPR__.add(u, role)
                
            
        for s in self.SRMapR2S.get(role):
            for (op,obj,) in self.PRMapR2P.get(role):
                if role not in self.MapSP2R.get((s,op,obj)):
                    self.MapSP2R.add((s,op,obj), role)
                    
                
            
        for u_5_1_1__EXPR__ in self.MapR2U_5_1_1__EXPR__[role]:
            self.Y_5_1_1__EXPR__.add(u_5_1_1__EXPR__, role)
            if role in self.Y_5_1_1__EXPR__[u_5_1_1__EXPR__]:
                for name_5_1_1__EXPR__ in MapR2N[role]:
                    self.X_5_1_1__EXPR__.add((u_5_1_1__EXPR__,name_5_1_1__EXPR__), role)
                    if u_5_1_1__EXPR__ in self.USERS:
                        for c_5_1_1__EXPR__ in MapN2C[name_5_1_1__EXPR__]:
                            if len(self.X_5_1_1__EXPR__.get(u_5_1_1__EXPR__, name_5_1_1__EXPR__)) > c_5_1_1__EXPR__:
                                self.V_5_1_1__EXPR__.add(u_5_1_1__EXPR__)
                                
                            
                        
                    
                
            
        for u_5_0_1__EXPR__ in self.MapR2U_5_0_1__EXPR__[role]:
            self.Y_5_0_1__EXPR__.add(u_5_0_1__EXPR__, role)
            if role in self.Y_5_0_1__EXPR__[u_5_0_1__EXPR__]:
                for name_5_0_1__EXPR__ in MapR2N[role]:
                    self.X_5_0_1__EXPR__.add((u_5_0_1__EXPR__,name_5_0_1__EXPR__), role)
                    if u_5_0_1__EXPR__ in self.USERS:
                        for c_5_0_1__EXPR__ in MapN2C[name_5_0_1__EXPR__]:
                            if len(self.X_5_0_1__EXPR__.get(u_5_0_1__EXPR__, name_5_0_1__EXPR__)) > c_5_0_1__EXPR__:
                                self.V_5_0_1__EXPR__.add(u_5_0_1__EXPR__)
                                
                            
                        
                    
                
            
        
    def DeleteRole(self, role):
        assert role in self.ROLES
        for u_5_0_1__EXPR__ in self.MapR2U_5_0_1__EXPR__[role]:
            if role in self.Y_5_0_1__EXPR__[u_5_0_1__EXPR__]:
                for name_5_0_1__EXPR__ in MapR2N[role]:
                    if u_5_0_1__EXPR__ in self.USERS:
                        for c_5_0_1__EXPR__ in MapN2C[name_5_0_1__EXPR__]:
                            if len(self.X_5_0_1__EXPR__.get(u_5_0_1__EXPR__, name_5_0_1__EXPR__)) > c:
                                self.V_5_0_1__EXPR__.remove(u_5_0_1__EXPR__)
                                
                            
                        
                    self.X_5_0_1__EXPR__.remove((u_5_0_1__EXPR__,name_5_0_1__EXPR__), role)
                    
                
            self.Y_5_0_1__EXPR__.remove(u_5_0_1__EXPR__, role)
            
        for u_5_1_1__EXPR__ in self.MapR2U_5_1_1__EXPR__[role]:
            if role in self.Y_5_1_1__EXPR__[u_5_1_1__EXPR__]:
                for name_5_1_1__EXPR__ in MapR2N[role]:
                    if u_5_1_1__EXPR__ in self.USERS:
                        for c_5_1_1__EXPR__ in MapN2C[name_5_1_1__EXPR__]:
                            if len(self.X_5_1_1__EXPR__.get(u_5_1_1__EXPR__, name_5_1_1__EXPR__)) > c:
                                self.V_5_1_1__EXPR__.remove(u_5_1_1__EXPR__)
                                
                            
                        
                    self.X_5_1_1__EXPR__.remove((u_5_1_1__EXPR__,name_5_1_1__EXPR__), role)
                    
                
            self.Y_5_1_1__EXPR__.remove(u_5_1_1__EXPR__, role)
            
        for s in self.SRMapR2S.get(role):
            for (op,obj,) in self.PRMapR2P.get(role):
                if role in self.MapSP2R.get((s,op,obj)):
                    self.MapSP2R.remove((s,op,obj), role)
                    
                
            
        for u in self.URMapR2U.get(role):
            if role in self.MapU2R_9_0_1__EXPR__.get(u):
                self.MapU2R_9_0_1__EXPR__.remove(u, role)
                
            
        for s in self.SRMapR2S_10_0_1__EXPR__.get(role):
            if role in self.MapS2R_10_0_1__EXPR__.get(s):
                self.MapS2R_10_0_1__EXPR__.remove(s, role)
                
            
        for (op,obj,) in self.PRMapR2P_17_0_1__EXPR__.get(role):
            for u in self.URMapR2U.get(role):
                if op in self.OPS:
                    if obj in self.OBJS:
                        if (op,obj) in self.MapU2P_17_0_1__EXPR__.get(u):
                            self.MapU2P_17_0_1__EXPR__.remove(u, (op,obj))
                            
                        
                    
                
            
        for (op,obj,) in self.PRMapR2P_18_0_1__EXPR__.get(role):
            for s in self.SRMapR2S_18_0_1__EXPR__.get(role):
                if op in self.OPS:
                    if obj in self.OBJS:
                        if (op,obj) in self.MapS2P_18_0_1__EXPR__.get(s):
                            self.MapS2P_18_0_1__EXPR__.remove(s, (op,obj))
                            
                        
                    
                
            
        self.ROLES.remove(role)
        for (op,obj,) in self.PRMapR2P.get(role).copy():
            if role in self.ROLES:
                for s in self.SRMapR2S.get(role):
                    if role in self.MapSP2R.get((s,op,obj)):
                        self.MapSP2R.add((s,op,obj), role)
                        
                    
                
            self.PRMapR2P.remove(role, (op,obj))
            if op in self.OPS:
                if obj in self.OBJS:
                    if (op,obj) in self.MapR2P_12_0_1__EXPR__.get(role):
                        self.MapR2P_12_0_1__EXPR__.remove(role, (op,obj))
                        
                    
                
            if op in self.OPS:
                if op in self.MapRO2A_13_0_1__EXPR__.get((role,obj)):
                    self.MapRO2A_13_0_1__EXPR__.remove((role,obj), op)
                    
                
            if op in self.OPS:
                if op in self.MapRO2A_13_1_1__EXPR__.get((role,obj)):
                    self.MapRO2A_13_1_1__EXPR__.remove((role,obj), op)
                    
                
            for u in self.URMapR2U.get(role):
                if op in self.OPS:
                    if obj in self.OBJS:
                        if (op,obj) in self.MapU2P_17_0_1__EXPR__.get(u):
                            self.MapU2P_17_0_1__EXPR__.remove(u, (op,obj))
                            
                        
                    
                
            self.PRMapR2P_17_0_1__EXPR__.remove(role, (op,obj))
            if role in self.ROLES:
                for s in self.SRMapR2S_18_0_1__EXPR__.get(role):
                    if op in self.OPS:
                        if obj in self.OBJS:
                            if (op,obj) in self.MapS2P_18_0_1__EXPR__.get(s):
                                self.MapS2P_18_0_1__EXPR__.remove(s, (op,obj))
                                
                            
                        
                    
                self.PRMapR2P_18_0_1__EXPR__.remove(role, (op,obj))
                
            self.PR.remove(((op,obj),role))
            
        for u in self.URMapR2U.get(role).copy():
            if role in self.ROLES:
                if role in self.Y_5_0_1__EXPR__[u]:
                    for name_5_0_1__EXPR__ in self.MapR2N_5_0_1__EXPR__[role]:
                        if u in self.USERS:
                            for c_5_0_1__EXPR__ in self.MapN2C_5_0_1__EXPR__[name_5_0_1__EXPR__]:
                                if len(self.X_5_0_1__EXPR__[(u,name_5_0_1__EXPR__)]) > c_5_0_1__EXPR__:
                                    self.V_5_0_1__EXPR__.remove(u)
                                    
                                
                            
                        self.X_5_0_1__EXPR__.remove((u,name_5_0_1__EXPR__), role)
                        
                    
                self.Y_5_0_1__EXPR__.remove(u, role)
                
            self.MapR2U_5_0_1__EXPR__.remove(role, u)
            if role in self.ROLES:
                if role in self.Y_5_1_1__EXPR__[u]:
                    for name_5_1_1__EXPR__ in self.MapR2N_5_1_1__EXPR__[role]:
                        if u in self.USERS:
                            for c_5_1_1__EXPR__ in self.MapN2C_5_1_1__EXPR__[name_5_1_1__EXPR__]:
                                if len(self.X_5_1_1__EXPR__[(u,name_5_1_1__EXPR__)]) > c_5_1_1__EXPR__:
                                    self.V_5_1_1__EXPR__.remove(u)
                                    
                                
                            
                        self.X_5_1_1__EXPR__.remove((u,name_5_1_1__EXPR__), role)
                        
                    
                self.Y_5_1_1__EXPR__.remove(u, role)
                
            self.MapR2U_5_1_1__EXPR__.remove(role, u)
            if role in self.ROLES:
                if role in self.MapU2R_9_0_1__EXPR__.get(u):
                    self.MapU2R_9_0_1__EXPR__.remove(u, role)
                    
                
            self.URMapR2U.remove(role, u)
            for (op,obj,) in self.PRMapR2P_17_0_1__EXPR__.get(role):
                if op in self.OPS:
                    if obj in self.OBJS:
                        if (op,obj) in self.MapU2P_17_0_1__EXPR__.get(u):
                            self.MapU2P_17_0_1__EXPR__.remove(u, (op,obj))
                            
                        
                    
                
            self.URMapR2U.remove(role, u)
            self.UR.remove((u,role))
            
        for (s,u,) in self.MapR2SU_16_0_1__EXPR__.get(role):
            self.DeleteSession(u, s)
            
        
    def DeassignUser(self, user, role):
        assert user in self.USERS
        assert role in self.ROLES
        assert (user,role) in self.UR
        if role in self.ROLES:
            if role in self.Y_5_0_1__EXPR__[user]:
                for name_5_0_1__EXPR__ in self.MapR2N_5_0_1__EXPR__[role]:
                    if user in self.USERS:
                        for c_5_0_1__EXPR__ in self.MapN2C_5_0_1__EXPR__[name_5_0_1__EXPR__]:
                            if len(self.X_5_0_1__EXPR__[(user,name_5_0_1__EXPR__)]) > c_5_0_1__EXPR__:
                                self.V_5_0_1__EXPR__.remove(user)
                                
                            
                        
                    self.X_5_0_1__EXPR__.remove((user,name_5_0_1__EXPR__), role)
                    
                
            self.Y_5_0_1__EXPR__.remove(user, role)
            
        self.MapR2U_5_0_1__EXPR__.remove(role, user)
        if role in self.ROLES:
            if role in self.Y_5_1_1__EXPR__[user]:
                for name_5_1_1__EXPR__ in self.MapR2N_5_1_1__EXPR__[role]:
                    if user in self.USERS:
                        for c_5_1_1__EXPR__ in self.MapN2C_5_1_1__EXPR__[name_5_1_1__EXPR__]:
                            if len(self.X_5_1_1__EXPR__[(user,name_5_1_1__EXPR__)]) > c_5_1_1__EXPR__:
                                self.V_5_1_1__EXPR__.remove(user)
                                
                            
                        
                    self.X_5_1_1__EXPR__.remove((user,name_5_1_1__EXPR__), role)
                    
                
            self.Y_5_1_1__EXPR__.remove(user, role)
            
        self.MapR2U_5_1_1__EXPR__.remove(role, user)
        if role in self.ROLES:
            if role in self.MapU2R_9_0_1__EXPR__.get(user):
                self.MapU2R_9_0_1__EXPR__.remove(user, role)
                
            
        self.URMapR2U.remove(role, user)
        for (op,obj,) in self.PRMapR2P_17_0_1__EXPR__.get(role):
            if op in self.OPS:
                if obj in self.OBJS:
                    if (op,obj) in self.MapU2P_17_0_1__EXPR__.get(user):
                        self.MapU2P_17_0_1__EXPR__.remove(user, (op,obj))
                        
                    
                
            
        self.URMapR2U.remove(role, user)
        self.UR.remove((user,role))
        for s in self.MapUR2S_15_0_1__EXPR__.get((user,role)):
            self.DeleteSession(user, s)
            
        
    def GrantPermission(self, operation, object, role):
        assert operation in self.OPS and object in self.OBJS
        assert role in self.ROLES
        assert ((operation,object),role) not in self.PR
        self.PR.add(((operation,object),role))
        if role in self.ROLES:
            for s in self.SRMapR2S_18_0_1__EXPR__.get(role):
                if operation in self.OPS:
                    if object in self.OBJS:
                        if (operation,object) not in self.MapS2P_18_0_1__EXPR__.get(s):
                            self.MapS2P_18_0_1__EXPR__.add(s, (operation,object))
                            
                        
                    
                
            self.PRMapR2P_18_0_1__EXPR__.add(role, (operation,object))
            
        for u in self.URMapR2U.get(role):
            if operation in self.OPS:
                if object in self.OBJS:
                    if (operation,object) not in self.MapU2P_17_0_1__EXPR__.get(u):
                        self.MapU2P_17_0_1__EXPR__.add(u, (operation,object))
                        
                    
                
            
        self.PRMapR2P_17_0_1__EXPR__.add(role, (operation,object))
        if operation in self.OPS:
            if operation not in self.MapRO2A_13_1_1__EXPR__.get((role,object)):
                self.MapRO2A_13_1_1__EXPR__.add((role,object), operation)
                
            
        if operation in self.OPS:
            if operation not in self.MapRO2A_13_0_1__EXPR__.get((role,object)):
                self.MapRO2A_13_0_1__EXPR__.add((role,object), operation)
                
            
        if operation in self.OPS:
            if object in self.OBJS:
                if (operation,object) not in self.MapR2P_12_0_1__EXPR__.get(role):
                    self.MapR2P_12_0_1__EXPR__.add(role, (operation,object))
                    
                
            
        if role in self.ROLES:
            for s in self.SRMapR2S.get(role):
                if role not in self.MapSP2R.get((s,operation,object)):
                    self.MapSP2R.add((s,operation,object), role)
                    
                
            
        self.PRMapR2P.add(role, (operation,object))
        
    def RevokePermission(self, operation, object, role):
        assert operation in self.OPS and object in self.OBJS
        assert role in self.ROLES
        assert ((operation,object),role) in self.PR
        if role in self.ROLES:
            for s in self.SRMapR2S.get(role):
                if role in self.MapSP2R.get((s,operation,object)):
                    self.MapSP2R.add((s,operation,object), role)
                    
                
            
        self.PRMapR2P.remove(role, (operation,object))
        if operation in self.OPS:
            if object in self.OBJS:
                if (operation,object) in self.MapR2P_12_0_1__EXPR__.get(role):
                    self.MapR2P_12_0_1__EXPR__.remove(role, (operation,object))
                    
                
            
        if operation in self.OPS:
            if operation in self.MapRO2A_13_0_1__EXPR__.get((role,object)):
                self.MapRO2A_13_0_1__EXPR__.remove((role,object), operation)
                
            
        if operation in self.OPS:
            if operation in self.MapRO2A_13_1_1__EXPR__.get((role,object)):
                self.MapRO2A_13_1_1__EXPR__.remove((role,object), operation)
                
            
        for u in self.URMapR2U.get(role):
            if operation in self.OPS:
                if object in self.OBJS:
                    if (operation,object) in self.MapU2P_17_0_1__EXPR__.get(u):
                        self.MapU2P_17_0_1__EXPR__.remove(u, (operation,object))
                        
                    
                
            
        self.PRMapR2P_17_0_1__EXPR__.remove(role, (operation,object))
        if role in self.ROLES:
            for s in self.SRMapR2S_18_0_1__EXPR__.get(role):
                if operation in self.OPS:
                    if object in self.OBJS:
                        if (operation,object) in self.MapS2P_18_0_1__EXPR__.get(s):
                            self.MapS2P_18_0_1__EXPR__.remove(s, (operation,object))
                            
                        
                    
                
            self.PRMapR2P_18_0_1__EXPR__.remove(role, (operation,object))
            
        self.PR.remove(((operation,object),role))
        
    def CreateSession(self, user, session, ars):
        assert user in self.USERS
        assert session not in self.SESSIONS
        assert ars.issubset(self.AssignedRoles(user))
        self.SU.add((session,user))
        if session in self.SESSIONS:
            if user in self.USERS:
                for r in self.SRMapS2R.get(session):
                    if (session,user) not in self.MapR2SU_16_0_1__EXPR__.get(r):
                        self.MapR2SU_16_0_1__EXPR__.add(r, (session,user))
                        
                    
                
            
        self.SUMapS2U_16_0_1__EXPR__.add(session, user)
        self.SUMapU2S_16_0_1__EXPR__.add(user, session)
        for r in self.SRMapS2R.get(session):
            if session not in self.MapUR2S_15_0_1__EXPR__.get((user,r)):
                self.MapUR2S_15_0_1__EXPR__.add((user,r), session)
                
            
        self.SUMapS2U_15_0_1__EXPR__.add(session, user)
        if session in self.SESSIONS:
            if session not in self.MapU2S_14_0_1__EXPR__.get(user):
                self.MapU2S_14_0_1__EXPR__.add(user, session)
                
            
        self.SUMapS2U_14_0_1__EXPR__.add(session, user)
        for r in ars:
            self.SR.add((session,r))
            for (op,obj,) in self.PRMapR2P_18_0_1__EXPR__.get(r):
                if op in self.OPS:
                    if obj in self.OBJS:
                        if (op,obj) not in self.MapS2P_18_0_1__EXPR__.get(session):
                            self.MapS2P_18_0_1__EXPR__.add(session, (op,obj))
                            
                        
                    
                
            self.SRMapR2S_18_0_1__EXPR__.add(r, session)
            for u in self.SUMapS2U_16_0_1__EXPR__.get(session):
                if session in self.SESSIONS:
                    if u in self.USERS:
                        if (session,u) not in self.MapR2SU_16_0_1__EXPR__.get(r):
                            self.MapR2SU_16_0_1__EXPR__.add(r, (session,u))
                            
                        
                    
                
            for u in self.SUMapS2U_15_0_1__EXPR__.get(session):
                if session not in self.MapUR2S_15_0_1__EXPR__.get((u,r)):
                    self.MapUR2S_15_0_1__EXPR__.add((u,r), session)
                    
                
            self.SRMapS2R.add(session, r)
            if r not in self.MapS2R_10_0_1__EXPR__.get(session):
                self.MapS2R_10_0_1__EXPR__.add(session, r)
                
            self.SRMapR2S_10_0_1__EXPR__.add(r, session)
            if r in self.ROLES:
                for (op,obj,) in self.PRMapR2P.get(r):
                    if r not in self.MapSP2R.get((session,op,obj)):
                        self.MapSP2R.add((session,op,obj), r)
                        
                    
                
            self.SRMapR2S.add(r, session)
            
        self.SESSIONS.add(session)
        for u in self.SUMapS2U_16_0_1__EXPR__.get(session):
            if u in self.USERS:
                for r in self.SRMapS2R.get(session):
                    if (session,u) not in self.MapR2SU_16_0_1__EXPR__.get(r):
                        self.MapR2SU_16_0_1__EXPR__.add(r, (session,u))
                        
                    
                
            
        for u in self.SUMapS2U_15_0_1__EXPR__.get(session):
            for r in self.SRMapS2R.get(session):
                if session not in self.MapUR2S_15_0_1__EXPR__.get((u,r)):
                    self.MapUR2S_15_0_1__EXPR__.add((u,r), session)
                    
                
            
        for u in self.SUMapS2U_14_0_1__EXPR__.get(session):
            if session not in self.MapU2S_14_0_1__EXPR__.get(u):
                self.MapU2S_14_0_1__EXPR__.add(u, session)
                
            
        
    def DeleteSession(self, user, session):
        assert user in self.USERS
        assert session in self.SESSIONS
        assert (session,user) in self.SU
        if session in self.SESSIONS:
            if session in self.MapU2S_14_0_1__EXPR__.get(user):
                self.MapU2S_14_0_1__EXPR__.remove(user, session)
                
            
        self.SUMapS2U_14_0_1__EXPR__.remove(session, user)
        for r in self.SRMapS2R.get(session):
            if session in self.MapUR2S_15_0_1__EXPR__.get((user,r)):
                self.MapUR2S_15_0_1__EXPR__.remove((user,r), session)
                
            
        self.SUMapS2U_15_0_1__EXPR__.remove(session, user)
        if session in self.SESSIONS:
            if user in self.USERS:
                for r in self.SRMapS2R.get(session):
                    if (session,user) in self.MapR2SU_16_0_1__EXPR__.get(r):
                        self.MapR2SU_16_0_1__EXPR__.remove(r, (session,user))
                        
                    
                
            
        self.SUMapS2U_16_0_1__EXPR__.remove(session, user)
        self.SUMapU2S_16_0_1__EXPR__.remove(user, session)
        self.SU.remove((session,user))
        for r in self.SRMapS2R.get(session).copy():
            if r in self.ROLES:
                for (op,obj,) in self.PRMapR2P.get(r):
                    if r in self.MapSP2R.get((session,op,obj)):
                        self.MapSP2R.remove((session,op,obj), r)
                        
                    
                
            self.SRMapR2S.remove(r, session)
            if r in self.MapS2R_10_0_1__EXPR__.get(session):
                self.MapS2R_10_0_1__EXPR__.remove(session, r)
                
            self.SRMapR2S_10_0_1__EXPR__.remove(r, session)
            for u in self.SUMapS2U_15_0_1__EXPR__.get(session):
                if session in self.MapUR2S_15_0_1__EXPR__.get((u,r)):
                    self.MapUR2S_15_0_1__EXPR__.remove((u,r), session)
                    
                
            self.SRMapS2R.remove(session, r)
            for u in self.SUMapS2U_16_0_1__EXPR__.get(session):
                if session in self.SESSIONS:
                    if u in self.USERS:
                        if (session,u) in self.MapR2SU_16_0_1__EXPR__.get(r):
                            self.MapR2SU_16_0_1__EXPR__.remove(r, (session,u))
                            
                        
                    
                
            for (op,obj,) in self.PRMapR2P_18_0_1__EXPR__.get(r):
                if op in self.OPS:
                    if obj in self.OBJS:
                        if (op,obj) in self.MapS2P_18_0_1__EXPR__.get(session):
                            self.MapS2P_18_0_1__EXPR__.remove(session, (op,obj))
                            
                        
                    
                
            self.SRMapR2S_18_0_1__EXPR__.remove(r, session)
            self.SR.remove((session,r))
            
        for u in self.SUMapS2U_14_0_1__EXPR__.get(session):
            if session in self.MapU2S_14_0_1__EXPR__.get(u):
                self.MapU2S_14_0_1__EXPR__.remove(u, session)
                
            
        for u in self.SUMapS2U_15_0_1__EXPR__.get(session):
            for r in self.SRMapS2R.get(session):
                if session in self.MapUR2S_15_0_1__EXPR__.get((u,r)):
                    self.MapUR2S_15_0_1__EXPR__.remove((u,r), session)
                    
                
            
        for u in self.SUMapS2U_16_0_1__EXPR__.get(session):
            if u in self.USERS:
                for r in self.SRMapS2R.get(session):
                    if (session,u) in self.MapR2SU_16_0_1__EXPR__.get(r):
                        self.MapR2SU_16_0_1__EXPR__.remove(r, (session,u))
                        
                    
                
            
        self.SESSIONS.remove(session)
        
    def AddActiveRole(self, user, session, role):
        assert user in self.USERS
        assert session in self.SESSIONS
        assert role in self.ROLES
        assert (session,user) in self.SU
        assert (session,role) not in self.SR
        assert role in self.AssignedRoles(user)
        self.SR.add((session,role))
        for (op,obj,) in self.PRMapR2P_18_0_1__EXPR__.get(role):
            if op in self.OPS:
                if obj in self.OBJS:
                    if (op,obj) not in self.MapS2P_18_0_1__EXPR__.get(session):
                        self.MapS2P_18_0_1__EXPR__.add(session, (op,obj))
                        
                    
                
            
        self.SRMapR2S_18_0_1__EXPR__.add(role, session)
        for u in self.SUMapS2U_16_0_1__EXPR__.get(session):
            if session in self.SESSIONS:
                if u in self.USERS:
                    if (session,u) not in self.MapR2SU_16_0_1__EXPR__.get(role):
                        self.MapR2SU_16_0_1__EXPR__.add(role, (session,u))
                        
                    
                
            
        for u in self.SUMapS2U_15_0_1__EXPR__.get(session):
            if session not in self.MapUR2S_15_0_1__EXPR__.get((u,role)):
                self.MapUR2S_15_0_1__EXPR__.add((u,role), session)
                
            
        self.SRMapS2R.add(session, role)
        if role not in self.MapS2R_10_0_1__EXPR__.get(session):
            self.MapS2R_10_0_1__EXPR__.add(session, role)
            
        self.SRMapR2S_10_0_1__EXPR__.add(role, session)
        if role in self.ROLES:
            for (op,obj,) in self.PRMapR2P.get(role):
                if role not in self.MapSP2R.get((session,op,obj)):
                    self.MapSP2R.add((session,op,obj), role)
                    
                
            
        self.SRMapR2S.add(role, session)
        
    def DropActiveRole(self, user, session, role):
        assert user in self.USERS
        assert session in self.SESSIONS
        assert role in self.ROLES
        assert (session,user) in self.SU
        assert (session,role) in self.SR
        if role in self.ROLES:
            for (op,obj,) in self.PRMapR2P.get(role):
                if role in self.MapSP2R.get((session,op,obj)):
                    self.MapSP2R.remove((session,op,obj), role)
                    
                
            
        self.SRMapR2S.remove(role, session)
        if role in self.MapS2R_10_0_1__EXPR__.get(session):
            self.MapS2R_10_0_1__EXPR__.remove(session, role)
            
        self.SRMapR2S_10_0_1__EXPR__.remove(role, session)
        for u in self.SUMapS2U_15_0_1__EXPR__.get(session):
            if session in self.MapUR2S_15_0_1__EXPR__.get((u,role)):
                self.MapUR2S_15_0_1__EXPR__.remove((u,role), session)
                
            
        self.SRMapS2R.remove(session, role)
        for u in self.SUMapS2U_16_0_1__EXPR__.get(session):
            if session in self.SESSIONS:
                if u in self.USERS:
                    if (session,u) in self.MapR2SU_16_0_1__EXPR__.get(role):
                        self.MapR2SU_16_0_1__EXPR__.remove(role, (session,u))
                        
                    
                
            
        for (op,obj,) in self.PRMapR2P_18_0_1__EXPR__.get(role):
            if op in self.OPS:
                if obj in self.OBJS:
                    if (op,obj) in self.MapS2P_18_0_1__EXPR__.get(session):
                        self.MapS2P_18_0_1__EXPR__.remove(session, (op,obj))
                        
                    
                
            
        self.SRMapR2S_18_0_1__EXPR__.remove(role, session)
        self.SR.remove((session,role))
        
    def CheckAccess(self, session, operation, object):
        assert session in self.SESSIONS
        assert operation in self.OPS
        assert object in self.OBJS
        return bool(self.MapSP2R.get((session,operation,object)))
    def AssignedUsers(self, role):
        assert role in self.ROLES
        return self.V_5_0_1__EXPR__
    def AssignedRoles(self, user):
        assert user in self.USERS
        return self.MapU2R_9_0_1__EXPR__.get(user)
    def RolePermissions(self, role):
        assert role in self.ROLES
        return self.MapR2P_12_0_1__EXPR__.get(role)
    def UserPermissions(self, user):
        assert user in self.USERS
        return self.MapU2P_17_0_1__EXPR__.get(user)
    def SessionRoles(self, session):
        assert session in self.SESSIONS
        return self.MapS2R_10_0_1__EXPR__.get(session)
    def SessionPermissions(self, session):
        assert session in self.SESSIONS
        return self.MapS2P_18_0_1__EXPR__.get(session)
    def RoleOperationsOnObject(self, role, obj):
        assert role in self.ROLES
        assert obj in self.OBJS
        return self.MapRO2A_13_0_1__EXPR__.get((role,object))
    def UserOperationsOnObject(self, user, obj):
        assert user in self.USERS
        assert obj in self.OBJS
        return self.MapRO2A_13_1_1__EXPR__.get((role,object))
    def AddOperation(self, operation):
        self.OPS.add(operation)
        
    def AddObject(self, OBJ):
        self.OBJS.add(OBJ)
        
    def AddPermission(self, operation, obj):
        pass 
    def checkSSD(self):
        return  not bool(self.V_5_1_1__EXPR__)
    def AssignUser(self, user, role):
        assert  not bool(set((True for (name,c,) in self.SsdNC if  not len(set((r for r in self.ROLES if (user,r) in self.UR | set([(user,role)]) and (name,r) in self.SsdNR))) <= c)))
        assert user in self.USERS
        assert role in self.ROLES
        assert (user,role) not in self.UR
        self.UR.add((user,role))
        for (op,obj,) in self.PRMapR2P_17_0_1__EXPR__.get(role):
            if op in self.OPS:
                if obj in self.OBJS:
                    if (op,obj) not in self.MapU2P_17_0_1__EXPR__.get(user):
                        self.MapU2P_17_0_1__EXPR__.add(user, (op,obj))
                        
                    
                
            
        self.URMapR2U.add(role, user)
        if role in self.ROLES:
            if role not in self.MapU2R_9_0_1__EXPR__.get(user):
                self.MapU2R_9_0_1__EXPR__.add(user, role)
                
            
        self.URMapR2U.add(role, user)
        if role in self.ROLES:
            self.Y_5_1_1__EXPR__.add(user, role)
            if role in self.Y_5_1_1__EXPR__[user]:
                for name_5_1_1__EXPR__ in self.MapR2N_5_1_1__EXPR__[role]:
                    self.X_5_1_1__EXPR__.add((user,name_5_1_1__EXPR__), role)
                    if user in self.USERS:
                        for c_5_1_1__EXPR__ in self.MapN2C_5_1_1__EXPR__[name_5_1_1__EXPR__]:
                            if len(self.X_5_1_1__EXPR__[(user,name_5_1_1__EXPR__)]) > c_5_1_1__EXPR__:
                                self.V_5_1_1__EXPR__.add(user)
                                
                            
                        
                    
                
            
        self.MapR2U_5_1_1__EXPR__.add(role, user)
        if role in self.ROLES:
            self.Y_5_0_1__EXPR__.add(user, role)
            if role in self.Y_5_0_1__EXPR__[user]:
                for name_5_0_1__EXPR__ in self.MapR2N_5_0_1__EXPR__[role]:
                    self.X_5_0_1__EXPR__.add((user,name_5_0_1__EXPR__), role)
                    if user in self.USERS:
                        for c_5_0_1__EXPR__ in self.MapN2C_5_0_1__EXPR__[name_5_0_1__EXPR__]:
                            if len(self.X_5_0_1__EXPR__[(user,name_5_0_1__EXPR__)]) > c_5_0_1__EXPR__:
                                self.V_5_0_1__EXPR__.add(user)
                                
                            
                        
                    
                
            
        self.MapR2U_5_0_1__EXPR__.add(role, user)
        
    def CreateSsdSet(self, name, roles, c):
        assert name not in self.SsdNAMES
        assert roles.issubset(self.ROLES)
        assert 1 <= c <= len(roles) - 1
        AddedSsdNR = set() 
        for r in roles:
            if (name,r) not in self.SsdNR:
                AddedSsdNR.add((name,r))
                self.SsdNR.add((name,r))
                self.MapN2R_6_0_1__EXPR__.add((name,r)[0], (name,r)[1])
                if r in self.ROLES:
                    if (name,r) in self.SsdNR:
                        self.X_5_1_1__EXPR__.add((u_5_1_1__EXPR__,name), r)
                        for u_5_1_1__EXPR__ in self.USERS:
                            for c_5_1_1__EXPR__ in self.MapN2C_5_1_1__EXPR__[name]:
                                if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name)]) > c_5_1_1__EXPR__:
                                    self.V_5_1_1__EXPR__.add(u_5_1_1__EXPR__)
                                    
                                
                            
                        
                    
                self.MapR2N_5_1_1__EXPR__.add((name,r))
                if r in self.ROLES:
                    if (name,r) in self.SsdNR:
                        self.X_5_0_1__EXPR__.add((u_5_0_1__EXPR__,name), r)
                        for u_5_0_1__EXPR__ in self.USERS:
                            for c_5_0_1__EXPR__ in self.MapN2C_5_0_1__EXPR__[name]:
                                if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name)]) > c_5_0_1__EXPR__:
                                    self.V_5_0_1__EXPR__.add(u_5_0_1__EXPR__)
                                    
                                
                            
                        
                    
                self.MapR2N_5_0_1__EXPR__.add((name,r))
                
            
        AddedSsdNC = set() 
        if (name,c) not in self.SsdNC:
            AddedSsdNC.add((name,c))
            self.MapN2C_7_0_1__EXPR__.add((name,c)[0], (name,c)[1])
            self.SsdNC.add((name,c))
            
            name_5_1_1__EXPR__ = (name,c)[0] 
            c_5_1_1__EXPR__ = (name,c)[1] 
            for u_5_1_1__EXPR__ in self.USERS:
                if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name_5_1_1__EXPR__)]) > c:
                    self.V_5_1_1__EXPR__.add(u_5_1_1__EXPR__)
                    
                
            self.MapN2C_5_1_1__EXPR__.add((name_5_1_1__EXPR__,c_5_1_1__EXPR__))
            name_5_0_1__EXPR__ = (name,c)[0] 
            c_5_0_1__EXPR__ = (name,c)[1] 
            for u_5_0_1__EXPR__ in self.USERS:
                if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name_5_0_1__EXPR__)]) > c:
                    self.V_5_0_1__EXPR__.add(u_5_0_1__EXPR__)
                    
                
            self.MapN2C_5_0_1__EXPR__.add((name_5_0_1__EXPR__,c_5_0_1__EXPR__))
            
        name_5_1_1__EXPR__ = (name,c)[0] 
        c_5_1_1__EXPR__ = (name,c)[1] 
        for u_5_1_1__EXPR__ in self.USERS:
            if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name_5_1_1__EXPR__)]) > c:
                self.V_5_1_1__EXPR__.add(u_5_1_1__EXPR__)
                
            
        self.MapN2C_5_1_1__EXPR__.add((name_5_1_1__EXPR__,c_5_1_1__EXPR__))
        name_5_0_1__EXPR__ = (name,c)[0] 
        c_5_0_1__EXPR__ = (name,c)[1] 
        for u_5_0_1__EXPR__ in self.USERS:
            if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name_5_0_1__EXPR__)]) > c:
                self.V_5_0_1__EXPR__.add(u_5_0_1__EXPR__)
                
            
        self.MapN2C_5_0_1__EXPR__.add((name_5_0_1__EXPR__,c_5_0_1__EXPR__))
        assert self.checkSSD()
        for (name,r,) in AddedSsdNR:
            if r in self.ROLES:
                if (name,r) in self.SsdNR:
                    for u_5_0_1__EXPR__ in self.USERS:
                        for c_5_0_1__EXPR__ in self.MapN2C_5_0_1__EXPR__[name]:
                            if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name)]) > c_5_0_1__EXPR__:
                                self.V_5_0_1__EXPR__.remove(u_5_0_1__EXPR__)
                                
                            
                        
                    self.X_5_0_1__EXPR__.remove((u_5_0_1__EXPR__,name), r)
                    
                
            self.MapR2N_5_0_1__EXPR__.remove((name,r))
            if r in self.ROLES:
                if (name,r) in self.SsdNR:
                    for u_5_1_1__EXPR__ in self.USERS:
                        for c_5_1_1__EXPR__ in self.MapN2C_5_1_1__EXPR__[name]:
                            if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name)]) > c_5_1_1__EXPR__:
                                self.V_5_1_1__EXPR__.remove(u_5_1_1__EXPR__)
                                
                            
                        
                    self.X_5_1_1__EXPR__.remove((u_5_1_1__EXPR__,name), r)
                    
                
            self.MapR2N_5_1_1__EXPR__.remove((name,r))
            self.SsdNR.remove((name,r))
            self.MapN2R_6_0_1__EXPR__.remove((name,r)[0], (name,r)[1])
            
        for (name,c,) in AddedSsdNC:
            name_5_0_1__EXPR__ = (name,c)[0] 
            c_5_0_1__EXPR__ = (name,c)[1] 
            for u_5_0_1__EXPR__ in self.USERS:
                if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name_5_0_1__EXPR__)]) > c:
                    self.V_5_0_1__EXPR__.remove(u_5_0_1__EXPR__)
                    
                
            self.MapN2C_5_0_1__EXPR__.remove((name_5_0_1__EXPR__,c_5_0_1__EXPR__))
            name_5_1_1__EXPR__ = (name,c)[0] 
            c_5_1_1__EXPR__ = (name,c)[1] 
            for u_5_1_1__EXPR__ in self.USERS:
                if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name_5_1_1__EXPR__)]) > c:
                    self.V_5_1_1__EXPR__.remove(u_5_1_1__EXPR__)
                    
                
            self.MapN2C_5_1_1__EXPR__.remove((name_5_1_1__EXPR__,c_5_1_1__EXPR__))
            self.MapN2C_7_0_1__EXPR__.remove((name,c)[0], (name,c)[1])
            self.SsdNC.remove((name,c))
            
            
        self.SsdNAMES.add(name)
        for tmp_0_0_1__EXPR__ in set(((name,r) for r in roles)):
            if tmp_0_0_1__EXPR__ not in self.SsdNR:
                self.SsdNR.add(tmp_0_0_1__EXPR__)
                self.MapN2R_6_0_1__EXPR__.add(tmp_0_0_1__EXPR__[0], tmp_0_0_1__EXPR__[1])
                
            
        self.MapN2C_7_0_1__EXPR__.add((name,c)[0], (name,c)[1])
        self.SsdNC.add((name,c))
        
        
    def DeleteSsdSet(self, name):
        assert name in self.SsdNAMES
        for tmp_20_0_1__EXPR__ in set(((name,r) for r in self.SsdRoleSetRoles(name))):
            if tmp_20_0_1__EXPR__ in self.SsdNR:
                self.SsdNR.remove(tmp_20_0_1__EXPR__)
                self.MapN2R_6_0_1__EXPR__.remove(tmp_20_0_1__EXPR__[0], tmp_20_0_1__EXPR__[1])
                
            
        name_5_0_1__EXPR__ = (name,self.SsdRoleSetCardinality(name))[0] 
        c_5_0_1__EXPR__ = (name,self.SsdRoleSetCardinality(name))[1] 
        for u_5_0_1__EXPR__ in self.USERS:
            if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name_5_0_1__EXPR__)]) > c:
                self.V_5_0_1__EXPR__.remove(u_5_0_1__EXPR__)
                
            
        self.MapN2C_5_0_1__EXPR__.remove((name_5_0_1__EXPR__,c_5_0_1__EXPR__))
        name_5_1_1__EXPR__ = (name,self.SsdRoleSetCardinality(name))[0] 
        c_5_1_1__EXPR__ = (name,self.SsdRoleSetCardinality(name))[1] 
        for u_5_1_1__EXPR__ in self.USERS:
            if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name_5_1_1__EXPR__)]) > c:
                self.V_5_1_1__EXPR__.remove(u_5_1_1__EXPR__)
                
            
        self.MapN2C_5_1_1__EXPR__.remove((name_5_1_1__EXPR__,c_5_1_1__EXPR__))
        self.MapN2C_7_0_1__EXPR__.remove((name,self.SsdRoleSetCardinality(name))[0], (name,self.SsdRoleSetCardinality(name))[1])
        self.SsdNC.remove((name,self.SsdRoleSetCardinality(name)))
        
        self.SsdNAMES.remove(name)
        
    def AddSsdRoleMember(self, name, role):
        assert name in self.SsdNAMES
        assert role in self.ROLES
        assert role not in self.SsdRoleSetRoles(name)
        AddedSsdNR = set() 
        if (name,role) not in self.SsdNR:
            AddedSsdNR.add((name,role))
            self.SsdNR.add((name,role))
            self.MapN2R_6_0_1__EXPR__.add((name,role)[0], (name,role)[1])
            if role in self.ROLES:
                if (name,role) in self.SsdNR:
                    self.X_5_1_1__EXPR__.add((u_5_1_1__EXPR__,name), role)
                    for u_5_1_1__EXPR__ in self.USERS:
                        for c_5_1_1__EXPR__ in self.MapN2C_5_1_1__EXPR__[name]:
                            if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name)]) > c_5_1_1__EXPR__:
                                self.V_5_1_1__EXPR__.add(u_5_1_1__EXPR__)
                                
                            
                        
                    
                
            self.MapR2N_5_1_1__EXPR__.add((name,role))
            if role in self.ROLES:
                if (name,role) in self.SsdNR:
                    self.X_5_0_1__EXPR__.add((u_5_0_1__EXPR__,name), role)
                    for u_5_0_1__EXPR__ in self.USERS:
                        for c_5_0_1__EXPR__ in self.MapN2C_5_0_1__EXPR__[name]:
                            if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name)]) > c_5_0_1__EXPR__:
                                self.V_5_0_1__EXPR__.add(u_5_0_1__EXPR__)
                                
                            
                        
                    
                
            self.MapR2N_5_0_1__EXPR__.add((name,role))
            
        if role in self.ROLES:
            if (name,role) in self.SsdNR:
                self.X_5_1_1__EXPR__.add((u_5_1_1__EXPR__,name), role)
                for u_5_1_1__EXPR__ in self.USERS:
                    for c_5_1_1__EXPR__ in self.MapN2C_5_1_1__EXPR__[name]:
                        if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name)]) > c_5_1_1__EXPR__:
                            self.V_5_1_1__EXPR__.add(u_5_1_1__EXPR__)
                            
                        
                    
                
            
        self.MapR2N_5_1_1__EXPR__.add((name,role))
        if role in self.ROLES:
            if (name,role) in self.SsdNR:
                self.X_5_0_1__EXPR__.add((u_5_0_1__EXPR__,name), role)
                for u_5_0_1__EXPR__ in self.USERS:
                    for c_5_0_1__EXPR__ in self.MapN2C_5_0_1__EXPR__[name]:
                        if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name)]) > c_5_0_1__EXPR__:
                            self.V_5_0_1__EXPR__.add(u_5_0_1__EXPR__)
                            
                        
                    
                
            
        self.MapR2N_5_0_1__EXPR__.add((name,role))
        assert self.checkSSD()
        for (name,r,) in AddedSsdNR:
            if r in self.ROLES:
                if (name,r) in self.SsdNR:
                    for u_5_0_1__EXPR__ in self.USERS:
                        for c_5_0_1__EXPR__ in self.MapN2C_5_0_1__EXPR__[name]:
                            if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name)]) > c_5_0_1__EXPR__:
                                self.V_5_0_1__EXPR__.remove(u_5_0_1__EXPR__)
                                
                            
                        
                    self.X_5_0_1__EXPR__.remove((u_5_0_1__EXPR__,name), r)
                    
                
            self.MapR2N_5_0_1__EXPR__.remove((name,r))
            if r in self.ROLES:
                if (name,r) in self.SsdNR:
                    for u_5_1_1__EXPR__ in self.USERS:
                        for c_5_1_1__EXPR__ in self.MapN2C_5_1_1__EXPR__[name]:
                            if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name)]) > c_5_1_1__EXPR__:
                                self.V_5_1_1__EXPR__.remove(u_5_1_1__EXPR__)
                                
                            
                        
                    self.X_5_1_1__EXPR__.remove((u_5_1_1__EXPR__,name), r)
                    
                
            self.MapR2N_5_1_1__EXPR__.remove((name,r))
            self.SsdNR.remove((name,r))
            self.MapN2R_6_0_1__EXPR__.remove((name,r)[0], (name,r)[1])
            
        self.SsdNR.add((name,role))
        self.MapN2R_6_0_1__EXPR__.add((name,role)[0], (name,role)[1])
        
    def DeleteSsdRoleMember(self, name, role):
        assert name in self.SsdNAMES
        assert role in self.SsdRoleSetRoles(name)
        assert self.SsdRoleSetCardinality(name) <= len(self.SsdRoleSetRoles(name)) - 2
        if role in self.ROLES:
            if (name,role) in self.SsdNR:
                for u_5_0_1__EXPR__ in self.USERS:
                    for c_5_0_1__EXPR__ in self.MapN2C_5_0_1__EXPR__[name]:
                        if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name)]) > c_5_0_1__EXPR__:
                            self.V_5_0_1__EXPR__.remove(u_5_0_1__EXPR__)
                            
                        
                    
                self.X_5_0_1__EXPR__.remove((u_5_0_1__EXPR__,name), role)
                
            
        self.MapR2N_5_0_1__EXPR__.remove((name,role))
        if role in self.ROLES:
            if (name,role) in self.SsdNR:
                for u_5_1_1__EXPR__ in self.USERS:
                    for c_5_1_1__EXPR__ in self.MapN2C_5_1_1__EXPR__[name]:
                        if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name)]) > c_5_1_1__EXPR__:
                            self.V_5_1_1__EXPR__.remove(u_5_1_1__EXPR__)
                            
                        
                    
                self.X_5_1_1__EXPR__.remove((u_5_1_1__EXPR__,name), role)
                
            
        self.MapR2N_5_1_1__EXPR__.remove((name,role))
        self.SsdNR.remove((name,role))
        self.MapN2R_6_0_1__EXPR__.remove((name,role)[0], (name,role)[1])
        
    def SetSsdSetCardinality(self, name, c):
        assert name in self.SsdNAMES
        assert 1 <= c <= len(self.SsdRoleSetRoles(name)) - 1
        NegSsdNC = set() 
        for (name,c,) in set((name,self.SsdRoleSetCardinality(name))):
            if (name,c) in self.SsdNC:
                name_5_0_1__EXPR__ = (name,c)[0] 
                c_5_0_1__EXPR__ = (name,c)[1] 
                for u_5_0_1__EXPR__ in self.USERS:
                    if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name_5_0_1__EXPR__)]) > c:
                        self.V_5_0_1__EXPR__.remove(u_5_0_1__EXPR__)
                        
                    
                self.MapN2C_5_0_1__EXPR__.remove((name_5_0_1__EXPR__,c_5_0_1__EXPR__))
                name_5_1_1__EXPR__ = (name,c)[0] 
                c_5_1_1__EXPR__ = (name,c)[1] 
                for u_5_1_1__EXPR__ in self.USERS:
                    if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name_5_1_1__EXPR__)]) > c:
                        self.V_5_1_1__EXPR__.remove(u_5_1_1__EXPR__)
                        
                    
                self.MapN2C_5_1_1__EXPR__.remove((name_5_1_1__EXPR__,c_5_1_1__EXPR__))
                self.MapN2C_7_0_1__EXPR__.remove((name,c)[0], (name,c)[1])
                self.SsdNC.remove((name,c))
                
                NegSsdNC.add((name,c))
                
            
        PosSsdNC = set() 
        if (name,c) not in self.SsdNC:
            self.MapN2C_7_0_1__EXPR__.add((name,c)[0], (name,c)[1])
            self.SsdNC.add((name,c))
            
            name_5_1_1__EXPR__ = (name,c)[0] 
            c_5_1_1__EXPR__ = (name,c)[1] 
            for u_5_1_1__EXPR__ in self.USERS:
                if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name_5_1_1__EXPR__)]) > c:
                    self.V_5_1_1__EXPR__.add(u_5_1_1__EXPR__)
                    
                
            self.MapN2C_5_1_1__EXPR__.add((name_5_1_1__EXPR__,c_5_1_1__EXPR__))
            name_5_0_1__EXPR__ = (name,c)[0] 
            c_5_0_1__EXPR__ = (name,c)[1] 
            for u_5_0_1__EXPR__ in self.USERS:
                if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name_5_0_1__EXPR__)]) > c:
                    self.V_5_0_1__EXPR__.add(u_5_0_1__EXPR__)
                    
                
            self.MapN2C_5_0_1__EXPR__.add((name_5_0_1__EXPR__,c_5_0_1__EXPR__))
            PosSsdNC.add((name,c))
            
        name_5_1_1__EXPR__ = (name,c)[0] 
        c_5_1_1__EXPR__ = (name,c)[1] 
        for u_5_1_1__EXPR__ in self.USERS:
            if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name_5_1_1__EXPR__)]) > c:
                self.V_5_1_1__EXPR__.add(u_5_1_1__EXPR__)
                
            
        self.MapN2C_5_1_1__EXPR__.add((name_5_1_1__EXPR__,c_5_1_1__EXPR__))
        name_5_0_1__EXPR__ = (name,c)[0] 
        c_5_0_1__EXPR__ = (name,c)[1] 
        for u_5_0_1__EXPR__ in self.USERS:
            if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name_5_0_1__EXPR__)]) > c:
                self.V_5_0_1__EXPR__.add(u_5_0_1__EXPR__)
                
            
        self.MapN2C_5_0_1__EXPR__.add((name_5_0_1__EXPR__,c_5_0_1__EXPR__))
        assert self.checkSSD()
        for (name,c,) in PosSsdNC:
            name_5_0_1__EXPR__ = (name,c)[0] 
            c_5_0_1__EXPR__ = (name,c)[1] 
            for u_5_0_1__EXPR__ in self.USERS:
                if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name_5_0_1__EXPR__)]) > c:
                    self.V_5_0_1__EXPR__.remove(u_5_0_1__EXPR__)
                    
                
            self.MapN2C_5_0_1__EXPR__.remove((name_5_0_1__EXPR__,c_5_0_1__EXPR__))
            name_5_1_1__EXPR__ = (name,c)[0] 
            c_5_1_1__EXPR__ = (name,c)[1] 
            for u_5_1_1__EXPR__ in self.USERS:
                if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name_5_1_1__EXPR__)]) > c:
                    self.V_5_1_1__EXPR__.remove(u_5_1_1__EXPR__)
                    
                
            self.MapN2C_5_1_1__EXPR__.remove((name_5_1_1__EXPR__,c_5_1_1__EXPR__))
            self.MapN2C_7_0_1__EXPR__.remove((name,c)[0], (name,c)[1])
            self.SsdNC.remove((name,c))
            
            
        for (name,c,) in NegSsdNC:
            self.MapN2C_7_0_1__EXPR__.add((name,c)[0], (name,c)[1])
            self.SsdNC.add((name,c))
            
            name_5_1_1__EXPR__ = (name,c)[0] 
            c_5_1_1__EXPR__ = (name,c)[1] 
            for u_5_1_1__EXPR__ in self.USERS:
                if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name_5_1_1__EXPR__)]) > c:
                    self.V_5_1_1__EXPR__.add(u_5_1_1__EXPR__)
                    
                
            self.MapN2C_5_1_1__EXPR__.add((name_5_1_1__EXPR__,c_5_1_1__EXPR__))
            name_5_0_1__EXPR__ = (name,c)[0] 
            c_5_0_1__EXPR__ = (name,c)[1] 
            for u_5_0_1__EXPR__ in self.USERS:
                if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name_5_0_1__EXPR__)]) > c:
                    self.V_5_0_1__EXPR__.add(u_5_0_1__EXPR__)
                    
                
            self.MapN2C_5_0_1__EXPR__.add((name_5_0_1__EXPR__,c_5_0_1__EXPR__))
            
        name_5_0_1__EXPR__ = (name,self.SsdRoleSetCardinality(name))[0] 
        c_5_0_1__EXPR__ = (name,self.SsdRoleSetCardinality(name))[1] 
        for u_5_0_1__EXPR__ in self.USERS:
            if len(self.X_5_0_1__EXPR__[(u_5_0_1__EXPR__,name_5_0_1__EXPR__)]) > c:
                self.V_5_0_1__EXPR__.remove(u_5_0_1__EXPR__)
                
            
        self.MapN2C_5_0_1__EXPR__.remove((name_5_0_1__EXPR__,c_5_0_1__EXPR__))
        name_5_1_1__EXPR__ = (name,self.SsdRoleSetCardinality(name))[0] 
        c_5_1_1__EXPR__ = (name,self.SsdRoleSetCardinality(name))[1] 
        for u_5_1_1__EXPR__ in self.USERS:
            if len(self.X_5_1_1__EXPR__[(u_5_1_1__EXPR__,name_5_1_1__EXPR__)]) > c:
                self.V_5_1_1__EXPR__.remove(u_5_1_1__EXPR__)
                
            
        self.MapN2C_5_1_1__EXPR__.remove((name_5_1_1__EXPR__,c_5_1_1__EXPR__))
        self.MapN2C_7_0_1__EXPR__.remove((name,self.SsdRoleSetCardinality(name))[0], (name,self.SsdRoleSetCardinality(name))[1])
        self.SsdNC.remove((name,self.SsdRoleSetCardinality(name)))
        
        self.MapN2C_7_0_1__EXPR__.add((name,c)[0], (name,c)[1])
        self.SsdNC.add((name,c))
        
        
    def SsdRoleSets(self):
        return self.SsdNAMES
    def SsdRoleSetRoles(self, name):
        assert name in self.SsdNAMES
        return self.MapN2R_6_0_1__EXPR__.get(name)
    def SsdRoleSetCardinality(self, name):
        assert name in self.SsdNAMES
        return self.MapN2C_7_0_1__EXPR__.get(name).pop()
    
