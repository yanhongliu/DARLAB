# author: annie liu.  all rights reserved.

from coreRBAC import CoreRBAC

# hierarchical RBAC with general role hierarchies
class GeneralHierRBAC(CoreRBAC):
    def __init__(self):
	CoreRBAC.__init__(self)
	self.RH = set()  # RH subset ROLES * ROLES, where asc inh desc 

    # transitive-reflexive closure of a relation E and ROLES
    def transclo(self, E):
	T = set(E)
	W = set((x,d) for (x,y) in T for (a,d) in E if y==a) - T
	while bool(W):
	    T.add(W.pop())
	    W = set((x,d) for (x,y) in T for (a,d) in E if y==a) - T
	return T | set((r,r) for r in self.ROLES)

    # transitive reduction of a relation E, unique for acyclic graphs
    def transred(self, E):
	T = set(E)
	W = set((a,d) for (a,d) in T 
		if (a,d) in self.transclo(T - set([(a,d)])))
	while bool(W):
	    T.remove(W.pop())
	    W = set((a,d) for (a,d) in T 
		    if (a,d) in self.transclo(T - set([(a,d)])))
	return 

# administrative commands: four new ones defined

    def AddInheritance(self, asc, desc):
	assert asc in self.ROLES
	assert desc in self.ROLES
#std-R  assert (asc,desc) not in self.transred(self.RH)
	assert (asc,desc) not in self.RH
	assert (desc,asc) not in self.RH
	self.RH |= set((r1,r2) for r1 in self.ROLES for r2 in self.ROLES
		       if (r1,desc) in self.RH and (asc,r2) in self.RH)

    def DeleteInheritance(self,asc,desc):
    	assert asc in self.ROLES
    	assert desc in self.ROLES
    	assert (asc,desc) in self.transred(self.RH)
	self.RH = self.transclo(self.transred(RH) - set([(asc,desc)]))

    def AddAsccendant(self,asc,desc):
	self.AddRole(asc)
	self.AddInheritance(asc,desc)    
	   
    def AddDescendant(self,asc,desc):
	self.AddRole(desc)
	self.AddInheritance(asc,desc)

# supporting system functions: two redefined, but same as in CoreRBAC except
# that, in the precondition, AssignedRoles is replaced with AuthorizedRoles

    def CreateSession(self, user, session, ars):
	assert user in self.USERS
	assert session not in self.SESSIONS
	assert ars.issubset(self.AuthorizedRoles(user))
	self.SESSIONS.add(session)
	self.SU.add((session,user))
	self.SR |= set((session,r) for r in ars)

    def AddActiveRole(self, user, session, role):
	assert user in self.USERS
	assert session in self.SESSIONS
	assert role in self.ROLES
	assert (session,user) in self.SU
	assert (session,role) not in self.SR
	assert role in self.AuthorizedRoles(user)
	self.SR.add((session,role))

# review functions: two new ones defined, but same as AssignedUsers and
# AssignedRoles in CoreRBAC except for adding use of asc and self.RH

    def AuthorizedUsers(self, role):
	assert role in self.ROLES
	return set(u for u in self.USERS for asc in self.ROLES 
		   if (asc,role) in self.RH and (u,asc) in self.UR)
	
    def AuthorizedRoles(self, user):
	assert user in self.USERS
	return set(r for r in self.ROLES for asc in self.ROLES 
		   if (user,asc) in self.UR and (asc,r) in self.RH)
		
# advanced review functions: four redefined, but same as in CoreRBAC except
# for adding use of acs and/or desc and self.RH

    def RolePermissions(self, role):
	assert role in self.ROLES
	return set((op,obj) for desc in self.ROLES 
		   for op in self.OPS for obj in self.OBJS 
		   if (role,desc) in self.RH and ((op,obj),desc) in self.PR)

    def UserPermissions(self, user):
	assert user in self.USERS
	return set((op,obj) for asc in self.ROLES for desc in self.ROLES
		   for op in self.OPS for opb in self.OBJS 
		   if (user,asc) in self.UR and (asc,desc) in self.RH
		   and ((op,obj),desc) in self.PR)

    def RoleOperationsOnObject(self, role, object):
	assert role in self.ROLES
	assert object in self.OBJS
	return set(op for desc in self.ROLES for op in self.OPS 
		   if (role,desc) in self.RH and ((op,object),desc) in self.PR)

    def UserOperationsOnObject(self, user, object):
	assert user in self.USERS
	assert object in self.OBJS
	return set(op for asc in self.ROLES for desc in self.ROLES 
		   for op in self.OPS 
		   if(user,asc) in self.UR and (asc,desc) in self.RH 
		   and ((op,object),desc) in self.PR)


# hierarchical RBAC with limited role hierarchies
class LimitedHierRBAC(GeneralHierRBAC):
    def __init__(self):
	GeneralHierRBAC.__init__(self)

# one administrative command refined: add check for single inheritance

    def AddInheritance(self, asc, desc):
#std-D  assert asc in self.ROLES
#std-D  assert desc in self.ROLES
#need to replace transred with RH as in GeneralHierRBAC.AddInheritance?
	assert not bool(set(r for r in self.ROLES
			    if (asc,r) in self.transred(self.RH)))
#std-D  assert (desc,asc) not in self.RH
	GeneralHierRBAC.AddInheritance(self,asc,desc)


# statically constrained RBAC
class CoreRBACwithSSD(CoreRBAC):
    def __init__(self):
	CoreRBAC.__init__(self)
	self.SsdNAMES = set()
	self.SsdNR = set()    # SsdNR subset SsdNAMES * ROLES
	self.SsdNC = set()    # SsdNC subset SsdNAMES * int
	# forall n in SsdNAMES:
	# 2 <= self.SsdRoleSetCardinality(n) <= len(self.SsdRoleSetRoles(n))

    # SSD constraint
    def checkSSD(self, SsdNR, SsdNC):
	return not bool(set(True for u in self.USERS for (n,c) in SsdNC
			    if not len(set(r for r in self.AssignedRoles(u)
					   if (n,r) in SsdNR))
				   <= c-1))

# administrative commands: one redefined, but just add check for SSD;
# and five new ones defined, where non-deletion ones check SSD

    def AssignUser(self, user, role):
#std-D  assert user in self.USERS
#std-D	assert role in self.ROLES
#std-D  assert (user,role) not in self.UR
	# check SSD, but calling checkSSD is no good
	assert not bool(set(True for (n,c) in self.SsdNC
			    if not len(set(r for r in self.ROLES
					   if (user,r) in self.UR|
					   set([(user,role)])
					   and (n,r) in self.SsdNR)) 
				  <= c-1))
	CoreRBAC.AssignUser(self,user,role)

    def CreateSsdSet(self, name, roles, c):
	assert name not in self.SsdNAMES
	assert roles.issubset(self.ROLES)
	assert 2 <= c <= len(roles)
	assert self.checkSSD(self.SsdNR | set((name,r) for r in roles),
			     self.SsdNC | set([(name,c)]))
	self.SsdNAMES.add(name)
	self.SsdNR |= set((name,r) for r in roles)
	self.SsdNC.add((name,c))

    def DeleteSsdSet(self, name):
	assert name in self.SsdNAMES
	self.SsdNR -= set((name,r) for r in self.SsdRoleSetRoles(name))
	self.SsdNC.remove((name,self.SsdRoleSetCardinality(name)))
	self.SsdNAMES.remove(name)		      # delete ssd name last

    def AddSsdRoleMember(self, name, role):
	assert name in self.SsdNAMES
	assert role in self.ROLES
	assert role not in self.SsdRoleSetRoles(name)
	assert self.checkSSD(self.SsdNR | set([(name,role)]),self.SsdNC)
	self.SsdNR.add((name,role))

    def DeleteSsdRoleMember(self, name, role):
	assert name in self.SsdNAMES
	assert role in self.SsdRoleSetRoles(name)
	assert \
	self.SsdRoleSetCardinality(name) <= len(self.SsdRoleSetRoles(name))-1
	self.SsdNR.remove((name,role))

    def SetSsdSetCardinality(self, name, c):
	assert name in self.SsdNAMES
	assert 2 <= c <= len(self.SsdRoleSetRoles(name))
	assert self.checkSSD(self.SsdNR,
			     self.SsdNC
			     - set((name,self.SsdRoleSetCardinality(name)))
			     | set([(name,c)]))
	self.SsdNC.remove((name,self.SsdRoleSetCardinality(name)))
	self.SsdNC.add((name,c))

# review functions: three new ones defined

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
	return not bool(set(True for u in self.USERS for (n,c) in SsdNC
			    if not len(set(r for r in self.AuthorizedRoles(u)
					   if (n,r) in SsdNR))
				   <= c-1))

# administrative commands: AssignUser redefined, to use AuthorizedRoles;
# AddInheritance also redefined, to add check for SSD;
# and non-deletion ones redefined, to use AuthorizedRoles;
# but use of AuthorizedRoles is automatic after checkSSD is redefined.

    def AddInheritance(self, asc, desc):
#std-D  assert asc in self.ROLES
#std-D  assert desc in self.ROLES
#std-D  assert (asc,desc) not in self.transred(self.RH)
#std-D  assert (desc,asc) not in self.RH
	# check SSD, but self.checkSSD(self.SsdNR,self.SsdNC) is no good
	assert not bool(set(True for u in self.USERS for (n,c) in self.SsdNC
			    if not len(set(r for r in self.ROLES
					   for a in self.ROLES 
					   if (u,a) in self.UR
					   and (a,r) in self.RH |
					   set((r1,r2)
					       for r1 in self.ROLES
					       for r2 in self.ROLES
					       if (r1,desc) in self.RH
					       if (asc,r2) in self.RH)
					   and (n,r) in self.SsdNR))
				   <= c-1))
	GeneralHierRBAC.AddInheritance(self,asc,desc)


# same as LimitedHierRBAC, except to add suffix withSSD to GeneralHierRBAC
class LimitedHierRBACwithSSD(GeneralHierRBACwithSSD):
    def __init__(self):
	GeneralHierRBACwithSSD.__init__(self)

    def AddInheritance(self, asc, desc):
#std-D  assert asc in self.ROLES
#std-D  assert desc in self.ROLES
#std-D	assert not bool(set(r for r in self.ROLES
#std-D			    if (asc,r) in self.transred(self.RH)))
#std-D  assert (desc,asc) not in self.RH
	GeneralHierRBACwithSSD.AddInheritance(self,asc,desc)


# dynamically constrained RBAC
class CoreRBACwithDSD(CoreRBAC):
    def __init__(self):
	# same as in CoreRBACwithSSD, except to use Dsd instead of Ssd
	CoreRBAC.__init__(self)
	self.DsdNAMES = set()
	self.DsdNR = set()    # DsdNR subset DsdNAMES * ROLES
	self.DsdNC = set()    # DsdNC subset DsdNAMES * int
	# forall n in DsdNAMES
	# 2 <= self.DsdRoleSetCardinality(n) <= len(self.DsdRoleSetRoles(n))

    # DSD constraint, as in CoreRBACwithSSD and GeneralHierRBACwithSSD,
    # except to use SESSIONS, SessionRoles, and use Dsd/DSD instead of Ssd/SSD
    def checkDSD(self, DsdNR, DsdNC):
	return not bool(set(True for s in self.SESSIONS for (n,c) in DsdNC
			    if not len(set(r for r in self.SessionRoles(s)
					   if (n,r) in DsdNR))
				   <= c-1))

# administrative commands: 5 new ones added, where non-deletion ones check DSD,
# same as in CoreRBACwithSSD, except to use Dsd/DSD instead of Ssd/SSD

    def CreateDsdSet(self, name, roles, c):
	assert name not in self.DsdNAMES
	assert roles.issubset(self.ROLES)
	assert 2 <= c <= len(roles)
	assert self.checkDSD(self.DsdNR | set((name,r) for r in roles),
			     self.DsdNC | set([(name,c)]))
	self.DsdNAMES.add(name)
	self.DsdNR |= set((name,r) for r in roles)
	self.DsdNC.add((name,c))

    def DeleteDsdSet(self, name):
	assert name in self.DsdNAMES
	self.DsdNR -= set((name,r) for r in self.DsdRoleSetRoles(name))
	self.DsdNC.remove((name,self.DsdRoleSetCardinality(name)))
	self.DsdNAMES.remove(name)		      # delete dsd name last

    def AddDsdRoleMember(self, name, role):
	assert name in self.DsdNAMES
	assert role in self.ROLES
	assert role not in self.DsdRoleSetRoles(name)
	assert self.checkDSD(self.DsdNR | set([(name,role)]),self.DsdNC)
	self.DsdNR.add((name,role))

    def DeleteDsdRoleMember(self, name, role):
	assert name in self.DsdNAMES
	assert role in self.DsdRoleSetRoles(name)
	assert \
	self.DsdRoleSetCardinality(name) <= len(self.DsdRoleSetRoles(name))-1
	self.DsdNR.remove((name,role))

    def SetDsdSetCardinality(self, name, c):
	assert name in self.DsdNAMES
	assert 2 <= c <= len(self.DsdRoleSetRoles(name))
	assert self.checkDSD(self.DsdNR,
			     self.DsdNC
			     - set((name,self.DsdRoleSetCardinality(name)))
			     | set([(name,c)]))
	self.DsdNC.remove((name,self.DsdRoleSetCardinality(name)))
	self.DsdNC.add((name,c))

# supporting system functions: 2 redefined, but same as in CoreRBAC, except
# to add check for DSD

    def CreateSession(self, user, session, ars):
#std-D	assert user in self.USERS
#std-D	assert session not in self.SESSIONS
#std-D  assert ars.issubset(self.AssignedRoles(user))
	# check DSD, but self.checkDSD(self.DsdNR,self.DsdNC) is no good
	assert not bool(set(True for s in self.SESSIONS
			    for (n,c) in self.DsdNC
			    if not len(set(r for r in self.ROLES
					   if (s,r) in self.SR |
					   set((session,r) for r in ars)
					   and (n,r) in self.DsdNR))
				   <= c-1))
	CoreRBAC.CreateSession(self,user,session,ars)

    def AddActiveRole(self, user, session, role):
#std-D  assert user in self.USERS
#std-D  assert session in self.SESSIONS
#std-D  assert role in self.ROLES
#std-D  assert (session,user) in self.SU
#std-D  assert (session,role) not in self.SR
#std-D  assert role in self.AssignedRoles(user)
	# check DSD, but call no good, as in CreateSession except to | one pair
	assert not bool(set(True for s in self.SESSIONS
			    for (n,c) in self.DsdNC
			    if not len(set(r for r in self.ROLES
					   if (s,r) in self.SR |
					   set([(session,role)])
					   and (n,r) in self.DsdNR))
				   <= c-1))
	CoreRBAC.AddActiveRole(self, user, session, role)

# review functions: three new ones defined, same as in CoreRBACwithSSD, except
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

# supporting system functions: two redefined, but same as in CoreRBACwithSSD,
# except to use AuthorizedRoles and use GeneralHierRBAC instead of CoreRBAC

    def CreateSession(self, user, session, ars):
#std-D	assert user in self.USERS
#std-D	assert session not in self.SESSIONS
#std-D	assert ars.issubset(self.AuthorizedRoles(user))
#       print user,session,ars,self.SESSIONS,self.SR,self.DsdNC,self.DsdNR
	# check DSD, but self.checkDSD(self.DsdNR,self.DsdNC) is no good
	assert not bool(set(True for s in self.SESSIONS
			    for (n,c) in self.DsdNC
			    if not len(set(r for r in self.ROLES
					   if (s,r) in self.SR |
					   set((session,r) for r in ars)
					   and (n,r) in self.DsdNR))
				   <= c-1))
	GeneralHierRBAC.CreateSession(self,user,session,ars)

    def AddActiveRole(self, user, session, role):
#std-D  assert user in self.USERS
#std-D  assert session in self.SESSIONS
#std-D  assert role in self.ROLES
#std-D  assert (session,user) in self.SU
#std-D  assert (session,role) not in self.SR
#std-D  assert role in self.AuthorizedRoles(user)
	# check DSD, call no good, as in CreateSession except to | one pair
	assert not bool(set(True for s in self.SESSIONS
			    for (n,c) in self.DsdNC
			    if not len(set(r for r in self.ROLES
					   if (s,r) in self.SR |
					   set([(session,role)])
					   and (n,r) in self.DsdNR))
				   <= c-1))
	GeneralHierRBAC.AddActiveRole(self,user,session,role)


class LimitedHierRBACwithDSD(GeneralHierRBACwithDSD):
    def __init__(self):
	# same as in LimitedHierRBAC, except to add suffix withDSD to name RBAC
	GeneralHierRBACwithDSD.__init__(self)

# only one administrative command redefined: to be same as in LimitedHierRBAC

    def AddInheritance(self, asc, desc):
	LimitedHierRBAC.AddInheritance(self,asc,desc)
