# author: annie liu.  all rights reserved.

from RBAC import coreRBAC
CoreRBAC = coreRBAC

# hierarchical RBAC
class GeneralHierRBAC(CoreRBAC):
    def __init__(self):
        CoreRBAC.__init__(self)
        self.INH = set() # INH subset ROLES * ROLES

    # transitive-reflexive closure of INH and ROLES
    def trans(self, INH):
        T = set(INH)
        W = set((x,b) for (x,y) in T for (h,b) in INH if y==h) - T
        while bool(W):
            T.add(W.pop())
            W = set((x,b) for (x,y) in T for (h,b) in INH if y==h) - T
        return T | set((r,r) for r in self.ROLES)

# administrative commands: 4 new ones defined

    def AddInheritance(self, heir, bearer):
        assert heir in self.ROLES
        assert bearer in self.ROLES
        assert (heir,bearer) not in self.INH
        assert heir != bearer 
	# to check acyclicity:
        assert (bearer,heir) not in self.trans(self.INH)
        self.INH.add((heir,bearer))

    def DeleteInheritance(self, heir, bearer):
        assert heir in self.ROLES
        assert bearer in self.ROLES
        assert (heir,bearer) in self.INH
        self.INH.remove((heir,bearer))

    def AddAscendant(self, heir, bearer):
        self.AddRole(heir)
        self.AddInheritance(heir,bearer)

    def AddDescendant(self, bearer, heir):
        self.AddRole(bearer)
        self.AddInheritance(heir,bearer)

# supporting system functions: 2 redefined, but same as in CoreRBAC except
# that, in the precondition, AssignedRoles is replaced with AuthorizedRoles

    def CreateSession(self, user, session, ars):
        assert user in self.USERS
        assert session not in self.SESSIONS
        assert ars.issubset(self.AuthorizedRoles(user))
        self.SU.add((session,user))
        self.SR |= set((session,r) for r in ars)
        self.SESSIONS.add(session)

    def AddActiveRole(self, user, session, role):
        assert user in self.USERS
        assert session in self.SESSIONS
        assert role in self.ROLES
        assert (session,user) in self.SU
        assert (session,role) not in self.SR
        assert role in self.AuthorizedRoles(user)
        self.SR.add((session,role))

# review functions: 2 new ones defined, but same as AssignedUsers and
# AssignedRoles in CoreRBAC except for adding use of self.trans(self.INH)

    def AuthorizedUsers(self, role):
        assert role in self.ROLES
        return set(u for heir in self.ROLES for u in self.USERS
                   if (heir,role) in self.trans(self.INH) 
                   and (u,heir) in self.UR)

    def AuthorizedRoles(self, user):
        assert user in self.USERS
        return set(r for heir in self.ROLES for r in self.ROLES
                   if (user,heir) in self.UR 
                   and (heir,r) in self.trans(self.INH))

# advanced review functions: four redefined but same as in CoreRBAC except
# for adding use of self.trans(self.INH)

    def RolePermissions(self, role):
        assert role in self.ROLES
        return set((op,obj) for bearer in self.ROLES 
                   for op in self.OPS for obj in self.OBJS
                   if (role,bearer) in self.trans(self.INH)
                   and ((op,obj),bearer) in self.PR)

    def UserPermissions(self, user):
        assert user in self.USERS
        return set((op,obj) for heir in self.ROLES for bearer in self.ROLES
                   for op in self.OPS for obj in self.OBJS
                   if (user,heir) in self.UR
                   and (heir,bearer) in self.trans(self.INH)
                   and ((op,obj),bearer) in self.PR)

    def RoleOperationsOnObject(self, role, object):
        assert role in self.ROLES, object in self.OBJS
        return set(op for bearer in self.ROLES for op in self.OPS
                   if (role,bearer) in self.trans(self.INH) 
                   and ((op,object),bearer) in self.PR)

    def UserOperationsOnObject(self, user, object):
        assert user in self.USERS, object in self.OBJS
        return set(op for heir in self.ROLES
                   for bearer in self.ROLES for op in self.OPS
                   if (user,heir) in self.UR
                   and (heir,bearer) in self.trans(self.INH)
                   and ((op,object),bearer) in self.PR)


class LimitedHierRBAC(GeneralHierRBAC):
    def __init__(self):
        GeneralHierRBAC.__init__(self)

# only 1 administrative command refined: just add check for single inheritance

    def AddInheritance(self, heir, bearer):
	# to check single inheritance:
        assert not bool(set(r for r in self.ROLES if (heir,r) in self.INH))
        GeneralHierRBAC.AddInheritance(self,heir,bearer)


# statically constrained RBAC
class CoreRBACwithSSD(CoreRBAC):
    def __init__(self):
        CoreRBAC.__init__(self)
        self.SsdNAMES = set()
        self.SsdNR = set()    # SsdNR subset SsdNAMES * ROLES
        self.SsdNC = set()    # SsdNC subset SsdNAMES * int
        # forall n in SsdNAMES:
        # 1<=self.SsdRoleSetCardinality(n)<=len(self.SsdRoleSetRoles(n))-1

    # SSD constraint
    def checkSSD(self, SsdNR, SsdNC):
	return not bool(set(True for u in self.USERS for (name,c) in SsdNC
                            if not len(set(r for r in self.AssignedRoles(u)
                                           if (name,r) in SsdNR))
                                   <= c))

# administrative commands: 1 redefined, but just add check for SSD;
# and 5 new ones defined, where non-deletion ones check SSD

    def AssignUser(self, user, role):
        # to check SSD, but self.checkSSD(self.SsdNR,self.SsdNC) is no good
        assert not bool(set(True for (name,c) in self.SsdNC
                            if not len(set(r for r in self.ROLES
                                           if (user,r) in self.UR|set([(user,role)])
                                           and (name,r) in self.SsdNR))
                                   <= c))
        CoreRBAC.AssignUser(self,user,role)

    def CreateSsdSet(self, name, roles, c):
        assert name not in self.SsdNAMES
        assert roles.issubset(self.ROLES)
        assert 1<=c<=len(roles)-1
        assert self.checkSSD(self.SsdNR|set((name,r) for r in roles),
                             self.SsdNC|set([(name,c)]))
        self.SsdNAMES.add(name)
        self.SsdNR |= set((name,r) for r in roles)
        self.SsdNC.add((name,c))

    def DeleteSsdSet(self, name):
        assert name in self.SsdNAMES
        self.SsdNR -= set((name,r) for r in self.SsdRoleSetRoles(name))
        self.SsdNC.remove((name,self.SsdRoleSetCardinality(name)))
        self.SsdNAMES.remove(name)                      # delete ssd name last

    def AddSsdRoleMember(self, name, role):
        assert name in self.SsdNAMES
        assert role in self.ROLES
        assert role not in self.SsdRoleSetRoles(name)
        assert self.checkSSD(self.SsdNR|set([(name,role)]),self.SsdNC)
        self.SsdNR.add((name,role))

    def DeleteSsdRoleMember(self, name, role):
        assert name in self.SsdNAMES
        assert role in self.SsdRoleSetRoles(name)
        assert self.SsdRoleSetCardinality(name)<=len(self.SsdRoleSetRoles(name))-2
        self.SsdNR.remove((name,role))

    def SetSsdSetCardinality(self, name, c):
        assert name in self.SsdNAMES
        assert 1<=c<=len(self.SsdRoleSetRoles(name))-1
        assert self.checkSSD(self.SsdNR,
                             self.SsdNC
                             -set((name,self.SsdRoleSetCardinality(name)))
                             |set([(name,c)]))
        self.SsdNC.remove((name,self.SsdRoleSetCardinality(name)))
        self.SsdNC.add((name,c))

# review functions: 3 new ones defined

    def SsdRoleSets(self):
        return self.SsdNAMES

    def SsdRoleSetRoles(self, name):
        assert name in self.SsdNAMES
        return set(r for (n,r) in self.SsdNR if n==name)
#alt    return set(r for r in self.ROLES if (name,r) in self.SsdNR)

    def SsdRoleSetCardinality(self, name):
        assert name in self.SsdNAMES
        return set(c for (n,c) in self.SsdNC if n==name).pop()


class GeneralHierRBACwithSSD(GeneralHierRBAC, CoreRBACwithSSD):
    def __init__(self):
        GeneralHierRBAC.__init__(self)
        CoreRBACwithSSD.__init__(self)        

    # SSD constraint, as in CoreRBACwithSSD, except to use AuthorizeRoles
    def checkSSD(self, SsdNR, SsdNC):
	return not bool(set(True for u in self.USERS for (name,c) in SsdNC
                            if not len(set(r for r in self.AuthorizedRoles(u)
                                           if (name,r) in SsdNR))
                                   <= c))

# administrative commands: AssignUser redefined, to use AuthorizedRoles;
# AddInheritance also redefined, to add check for SSD;
# and non-deletion ones redefined, to use AuthorizedRoles,
# but use of AuthorizedRoles is automatic after checkSSD is redefined.

    def AddInheritance(self, heir, bearer):
        # to check SSD, but self.checkSSD(self.SsdNR,self.SsdNC) is no good
        assert not bool(set(True for u in self.USERS for (name,c) in self.SsdNC
                            if not len(set(r for heir in self.ROLES 
                                           for r in self.ROLES
                                           if (u,heir) in self.UR
                                           and (heir,r) in self.trans(self.INH|set([(heir,bearer)]))
                                           and (name,r) in self.SsdNR))
                                   <= c))
        GeneralHierRBAC.AddInheritance(self,heir,bearer)


# same as in LimitedHierRBAC, except to add withSSD after RBAC
class LimitedHierRBACwithSSD(GeneralHierRBACwithSSD):
    def __init__(self):
        GeneralHierRBACwithSSD.__init__(self)

#only 1 administrative command refined: just add check for single inheritance

    def AddInheritance(self, heir, bearer):
	# to check single inheritance:
        assert not set(r for r in self.ROLES if (heir,r) in self.INH)
        GeneralHierRBACwithSSD.AddInheritance(self,heir,bearer)


# dynamically constrained RBAC
class CoreRBACwithDSD(CoreRBAC):
    def __init__(self):
        # same as in CoreRBACwithSSD, except to use Dsd instead of Ssd
        CoreRBAC.__init__(self)
        self.DsdNAMES = set()
        self.DsdNR = set()    # DsdNR subset DsdNAMES * ROLES
        self.DsdNC = set()    # DsdNC subset DsdNAMES * int
        # forall n in DsdNAMES
        # 1<=self.DsdRoleSetCardinality(n)<=len(self.DsdRoleSetRoles(n))-1

    # DSD constraint, as in CoreRBACwithSSD and GeneralHierRBACwithSSD,
    # except to use SESSIONS, SessionRoles, and use Dsd/DSD instead of Ssd/SSD
    def checkDSD(self, DsdNR, DsdNC):
	return not bool(set(True for s in self.SESSIONS for (name,c) in DsdNC
                            if not len(set(r for r in self.SessionRoles(s)
                                           if (name,r) in DsdNR))
                                   <= c))

# administrative commands: 5 new ones added, where non-deletion ones check DSD,
# same as in CoreRBACwithSSD, except to use Dsd/DSD instead of Ssd/SSD

    def CreateDsdSet(self, name, roles, c):
        assert name not in self.DsdNAMES
        assert roles.issubset(self.ROLES)
        assert 1<=c<=len(roles)-1
        assert self.checkDSD(self.DsdNR|set((name,r) for r in roles),
                             self.DsdNC|set([(name,c)]))
        self.DsdNAMES.add(name)
        self.DsdNR |= set((name,r) for r in roles)
        self.DsdNC.add((name,c))

    def DeleteDsdSet(self, name):
        assert name in self.DsdNAMES
        self.DsdNR -= set((name,r) for r in self.DsdRoleSetRoles(name))
        self.DsdNC.remove((name,self.DsdRoleSetCardinality(name)))
        self.DsdNAMES.remove(name)                      # delete dsd name last

    def AddDsdRoleMember(self, name, role):
        assert name in self.DsdNAMES
        assert role in self.ROLES
        assert role not in self.DsdRoleSetRoles(name)
        assert self.checkDSD(self.DsdNR|set([(name,role)]),self.DsdNC)
        self.DsdNR.add((name,role))

    def DeleteDsdRoleMember(self, name, role):
        assert name in self.DsdNAMES
        assert role in self.DsdRoleSetRoles(name)
        assert self.DsdRoleSetCardinality(name)<=len(self.DsdRoleSetRoles(name))-2
        self.DsdNR.remove((name,role))

    def SetDsdSetCardinality(self, name, c):
        assert name in self.DsdNAMES
        assert 1<=c<=len(self.DsdRoleSetRoles(name))-1
        assert self.checkDSD(self.DsdNR,
                             self.DsdNC
                             -set((name,self.DsdRoleSetCardinality(name)))
                             |set([(name,c)]))
        self.DsdNC.remove((name,self.DsdRoleSetCardinality(name)))
        self.DsdNC.add((name,c))

# supporting system functions: 2 redefined, but same as in CoreRBAC, except
# to add check for DSD

    def CreateSession(self, user, session, ars):
        # to check DSD, but self.checkDSD(self.DsdNR,self.DsdNC) is no good
        assert not bool(set(True for s in self.SESSIONS for (name,c) in self.DsdNC
                            if not len(set(r for r in self.ROLES
                                           if (s,r) in self.SR|set((session,r) for r in ars)
                                           and (name,r) in self.DsdNR))
                                   <= c))
        CoreRBAC.CreateSession(self,user,session,ars)

    def AddActiveRole(self, user, session, role):
        # to check DSD, as in CreateSession except to | one pair
        assert not bool(set(True for s in self.SESSIONS for (name,c) in self.DsdNC
                            if not len(set(r for r in self.ROLES
                                           if (s,r) in self.SR|set([(session,role)])
                                           and (name,r) in self.DsdNR))
                                   <= c))
        CoreRBAC.AddActiveRole(self, user, session, role)

# review functions: 3 new ones defined, same as in CoreRBACwithSSD, except
# to use Dsd instead of Ssd

    def DsdRoleSets(self):
        return self.DsdNAMES

    def DsdRoleSetRoles(self, name):
        assert name in self.DsdNAMES
        return set(r for (n,r) in self.DsdNR if n==name)

    def DsdRoleSetCardinality(self, name):
        assert name in self.DsdNAMES
        return set(c for (n,c) in self.DsdNC if n==name).pop()


class GeneralHierRBACwithDSD(GeneralHierRBAC, CoreRBACwithDSD):
    def __init__(self):
        # same as in GeneralRBACwithSSD, except to use DSD instead of SSD
        GeneralHierRBAC.__init__(self)
        CoreRBACwithDSD.__init__(self)

# supporting system functions: 2 redefined, but same as in CoreRBACwithSSD
# except to use AuthorizedRoles, by using GeneralHierRBAC instead of CoreRBAC

    def CreateSession(self, user, session, ars):
        # to check DSD, but self.checkDSD(self.DsdNR,self.DsdNC) is no good
        print user,session,ars,self.SESSIONS,self.SR,self.DsdNC,self.DsdNR
        assert not bool(set(True for (name,c) in self.DsdNC
                            if not len(set(r for r in self.ROLES
                                           if (session,r) in self.SR|set((session,r) for r in ars)
                                           and (name,r) in self.DsdNR))
                                   <= c))
        GeneralHierRBAC.CreateSession(self,user,session,ars)

    def AddActiveRole(self, user, session, role):
        # to check DSD, as in CreateSession except to | one pair
        assert not bool(set(True for s in self.SESSIONS for (name,c) in self.DsdNC
                            if not len(set(r for r in self.ROLES
                                           if (s,r) in self.SR|set([(session,role)])
                                           and (name,r) in self.DsdNR))
                                   <= c))
        GeneralHierRBAC.AddActiveRole(self,user,session,role)


class LimitedHierRBACwithDSD(GeneralHierRBACwithDSD):
    def __init__(self):
        # same as in LimitedHierRBAC, except to add withDSD after RBAC
        GeneralHierRBACwithDSD.__init__(self)

# only 1 administrative command redefined: to be same as in LimitedHierRBAC

    def AddInheritance(self, heir, bearer):
        LimitedHierRBAC.AddInheritance(self,heir,bearer)
