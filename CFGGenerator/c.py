class MultiMap:

    def __init__(self):
        self.dct = {}

    def get(self, k):
        temp0 = self.dct
        temp4 = (k in temp0)
        if temp4:
            temp1 = self.dct
            temp2 = temp1[k]
            return temp2
        else:
            temp3 = set()
            return temp3

    def __getitem__(self, k):
        temp5 = self.get
        temp6 = temp5(k)
        return temp6

    def add(self, k, v):
        temp7 = self.dct
        temp12 = (k not in temp7)
        if temp12:
            s = set()
            self.dct[k] = s
            temp8 = s.add
            temp8(v)
        else:
            temp9 = self.dct
            temp10 = temp9[k]
            temp11 = temp10.add
            temp11(v)

    def remove(self, k, v):
        temp13 = self.dct
        temp18 = (k in temp13)
        if temp18:
            temp14 = self.dct
            s = temp14[k]
            temp15 = s.remove
            temp15(v)
            temp17 = (not s)
            if temp17:
                temp16 = self.dct
                del temp16[k]


class coreRBAC:

    def __init__(self):
        self.OBJS = set()
        self.OPS = set()
        self.USERS = set()
        self.ROLES = set()
        self.PR = set()
        self.UR = set()
        self.SESSIONS = set()
        self.SU = set()
        self.SR = set()
        self.SsdNAMES = set()
        self.SsdNR = set()
        self.SsdNC = set()
        self.DsdNAMES = set()
        self.DsdNR = set()
        self.DsdNC = set()

    def AddUser(self, user):
        temp19 = self.USERS
        assert (user not in temp19)
        temp20 = self.USERS
        temp21 = temp20.add
        temp21(user)

    def DeleteUser(self, user):
        temp22 = self.USERS
        assert (user in temp22)
        temp23 = []
        temp25 = self.ROLES
        for r in temp25:
            temp24 = (user, r)
            temp24.append(temp24)
        temp26 = temp24
        self.UR-=set(temp26)
        temp27 = []
        temp30 = self.SESSIONS
        for s in temp30:
            temp28 = (s, user)
            temp29 = self.SU
            if (temp28 in temp29):
                temp27.append(s)
        temp31 = temp27
        temp33 = set(temp31)
        for s in temp33:
            temp32 = self.DeleteSession
            temp32(user, s)
        temp34 = self.USERS
        temp35 = temp34.remove
        temp35(user)

    def AddRole(self, role):
        temp36 = self.ROLES
        assert (role not in temp36)
        temp37 = self.ROLES
        temp38 = temp37.add
        temp38(role)

    def DeleteRole(self, role):
        temp39 = self.ROLES
        assert (role in temp39)
        temp40 = self.ROLES
        temp41 = temp40.remove
        temp41(role)
        temp44 = self.OBJS
        temp45 = self.OPS

        def temp46(arg0, arg1):
            for op in temp45:
                for obj in temp44:
                    temp42 = (op, obj)
                    temp43 = (temp42, role)
                    yield temp43
        temp47 = temp46(temp44, temp45)
        temp48 = temp47
        self.PR-=set(temp48)
        temp50 = self.USERS

        def temp51(arg0):
            for u in temp50:
                temp49 = (u, role)
                yield temp49
        temp52 = temp51(temp50)
        temp53 = temp52
        self.UR-=set(temp53)
        temp61 = self.USERS
        temp62 = self.SESSIONS

        def temp63(arg0, arg1):
            for s in temp62:
                for u in temp61:
                    temp55 = (s, u)
                    temp56 = self.SU
                    temp57 = (temp55 in temp56)
                    temp58 = (s, role)
                    temp59 = self.SR
                    temp60 = (temp58 in temp59)
                    if (temp57 and temp60):
                        temp54 = (s, u)
                        yield temp54
        temp64 = temp63(temp61, temp62)
        temp65 = temp64
        temp67 = set(temp65)
        for (s, u) in temp67:
            temp66 = self.DeleteSession
            temp66(u, s)

    def DeassignUser(self, user, role):
        temp68 = self.USERS
        assert (user in temp68)
        temp69 = self.ROLES
        assert (role in temp69)
        temp70 = (user, role)
        temp71 = self.UR
        assert (temp70 in temp71)
        temp72 = self.UR
        temp73 = temp72.remove
        temp74 = (user, role)
        temp73(temp74)
        temp81 = self.SESSIONS

        def temp82(arg0):
            for s in temp81:
                temp75 = (s, user)
                temp76 = self.SU
                temp77 = (temp75 in temp76)
                temp78 = (s, role)
                temp79 = self.SR
                temp80 = (temp78 in temp79)
                if (temp77 and temp80):
                    yield s
        temp83 = temp82(temp81)
        temp84 = temp83
        temp86 = set(temp84)
        for s in temp86:
            temp85 = self.DeleteSession
            temp85(user, s)

    def GrantPermission(self, operation, object, role):
        temp87 = self.OPS
        temp88 = (operation in temp87)
        temp89 = self.OBJS
        temp90 = (object in temp89)
        assert (temp88 and temp90)
        temp91 = self.ROLES
        assert (role in temp91)
        temp92 = (operation, object)
        temp93 = (temp92, role)
        temp94 = self.PR
        assert (temp93 not in temp94)
        temp95 = self.PR
        temp96 = temp95.add
        temp97 = (operation, object)
        temp98 = (temp97, role)
        temp96(temp98)

    def RevokePermission(self, operation, object, role):
        temp99 = self.OPS
        temp100 = (operation in temp99)
        temp101 = self.OBJS
        temp102 = (object in temp101)
        assert (temp100 and temp102)
        temp103 = self.ROLES
        assert (role in temp103)
        temp104 = (operation, object)
        temp105 = (temp104, role)
        temp106 = self.PR
        assert (temp105 in temp106)
        temp107 = self.PR
        temp108 = temp107.remove
        temp109 = (operation, object)
        temp110 = (temp109, role)
        temp108(temp110)

    def CreateSession(self, user, session, ars):
        added = set()
        for role in ars:
            temp111 = (session, role)
            temp112 = self.SR
            temp118 = (temp111 not in temp112)
            if temp118:
                temp113 = self.SR
                temp114 = temp113.add
                temp115 = (session, role)
                temp114(temp115)
                temp116 = added.add
                temp117 = (session, role)
                temp116(temp117)
        temp119 = self.checkDSD
        good = temp119()
        for k in added:
            temp120 = self.SR
            temp121 = temp120.remove
            temp122 = (k[0], k[1])
            temp121(temp122)
        assert good
        temp123 = self.USERS
        assert (user in temp123)
        temp124 = self.SESSIONS
        assert (session not in temp124)
        temp125 = ars.issubset
        temp126 = self.AssignedRoles
        temp127 = temp126(user)
        assert temp125(temp127)
        temp128 = self.SU
        temp129 = temp128.add
        temp130 = (session, user)
        temp129(temp130)
        for r in ars:
            temp131 = self.SR
            temp132 = temp131.add
            temp133 = (session, r)
            temp132(temp133)
        temp134 = self.SESSIONS
        temp135 = temp134.add
        temp135(session)

    def AddActiveRole(self, user, session, role):
        added = set()
        temp136 = (session, role)
        temp137 = self.SR
        temp143 = (temp136 not in temp137)
        if temp143:
            temp138 = self.SR
            temp139 = temp138.add
            temp140 = (session, role)
            temp139(temp140)
            temp141 = added.add
            temp142 = (session, role)
            temp141(temp142)
        temp144 = self.CheckDSD
        good = temp144()
        for k in added:
            temp145 = self.SR
            temp146 = temp145.remove
            temp147 = (k[0], k[1])
            temp146(temp147)
        assert good
        temp148 = self.USERS
        assert (user in temp148)
        temp149 = self.SESSIONS
        assert (session in temp149)
        temp150 = self.ROLES
        assert (role in temp150)
        temp151 = (session, user)
        temp152 = self.SU
        assert (temp151 in temp152)
        temp153 = (session, role)
        temp154 = self.SR
        assert (temp153 not in temp154)
        temp155 = self.AssignedRoles
        temp156 = temp155(user)
        assert (role in temp156)
        temp157 = self.SR
        temp158 = temp157.add
        temp159 = (session, role)
        temp158(temp159)

    def DeleteSession(self, user, session):
        temp160 = self.USERS
        assert (user in temp160)
        temp161 = self.SESSIONS
        assert (session in temp161)
        temp162 = (session, user)
        temp163 = self.SU
        assert (temp162 in temp163)
        temp164 = self.SU
        temp165 = temp164.remove
        temp166 = (session, user)
        temp165(temp166)
        temp168 = self.ROLES

        def temp169(arg0):
            for r in temp168:
                temp167 = (session, r)
                yield temp167
        temp170 = temp169(temp168)
        temp171 = temp170
        self.SR-=set(temp171)
        temp172 = self.SESSIONS
        temp173 = temp172.remove
        temp173(session)

    def DropActiveRole(self, user, session, role):
        temp174 = self.USERS
        assert (user in temp174)
        temp175 = self.SESSIONS
        assert (session in temp175)
        temp176 = self.ROLES
        assert (role in temp176)
        temp177 = (session, user)
        temp178 = self.SU
        assert (temp177 in temp178)
        temp179 = (session, role)
        temp180 = self.SR
        assert (temp179 in temp180)
        temp181 = self.SR
        temp182 = temp181.remove
        temp183 = (session, role)
        temp182(temp183)

    def CheckAccess(self, session, operation, object):
        temp184 = self.SESSIONS
        assert (session in temp184)
        temp185 = self.OPS
        assert (operation in temp185)
        temp186 = self.OBJS
        assert (object in temp186)
        temp194 = self.ROLES

        def temp195(arg0):
            for r in temp194:
                temp187 = (session, r)
                temp188 = self.SR
                temp189 = (temp187 in temp188)
                temp190 = (operation, object)
                temp191 = (temp190, r)
                temp192 = self.PR
                temp193 = (temp191 in temp192)
                if (temp189 and temp193):
                    yield r
        temp196 = temp195(temp194)
        temp197 = temp196
        temp198 = set(temp197)
        temp199 = bool(temp198)
        return temp199

    def AssignedUsers(self, role):
        temp200 = self.ROLES
        assert (role in temp200)
        temp203 = self.USERS

        def temp204(arg0):
            for u in temp203:
                temp201 = (u, role)
                temp202 = self.UR
                if (temp201 in temp202):
                    yield u
        temp205 = temp204(temp203)
        temp206 = temp205
        temp207 = set(temp206)
        return temp207

    def AssignedRoles(self, user):
        temp208 = self.USERS
        assert (user in temp208)
        temp211 = self.ROLES

        def temp212(arg0):
            for r in temp211:
                temp209 = (user, r)
                temp210 = self.UR
                if (temp209 in temp210):
                    yield r
        temp213 = temp212(temp211)
        temp214 = temp213
        temp215 = set(temp214)
        return temp215

    def RolePermissions(self, role):
        temp216 = self.ROLES
        assert (role in temp216)
        temp221 = self.OBJS
        temp222 = self.OPS

        def temp223(arg0, arg1):
            for op in temp222:
                for obj in temp221:
                    temp218 = (op, obj)
                    temp219 = (temp218, role)
                    temp220 = self.PR
                    if (temp219 in temp220):
                        temp217 = (op, obj)
                        yield temp217
        temp224 = temp223(temp221, temp222)
        temp225 = temp224
        temp226 = set(temp225)
        return temp226

    def UserPermissions(self, user):
        temp227 = self.USERS
        assert (user in temp227)
        temp236 = self.OBJS
        temp237 = self.OPS
        temp238 = self.ROLES

        def temp239(arg0, arg1, arg2):
            for r in temp238:
                for op in temp237:
                    for obj in temp236:
                        temp229 = (user, r)
                        temp230 = self.UR
                        temp231 = (temp229 in temp230)
                        temp232 = (op, obj)
                        temp233 = (temp232, r)
                        temp234 = self.PR
                        temp235 = (temp233 in temp234)
                        if (temp231 and temp235):
                            temp228 = (op, obj)
                            yield temp228
        temp240 = temp239(temp236, temp237, temp238)
        temp241 = temp240
        temp242 = set(temp241)
        return temp242

    def SessionRoles(self, session):
        temp243 = self.SESSIONS
        assert (session in temp243)
        temp246 = self.ROLES

        def temp247(arg0):
            for r in temp246:
                temp244 = (session, r)
                temp245 = self.SR
                if (temp244 in temp245):
                    yield r
        temp248 = temp247(temp246)
        temp249 = temp248
        temp250 = set(temp249)
        return temp250

    def SessionPermissions(self, session):
        temp251 = self.SESSIONS
        assert (session in temp251)
        temp260 = self.OBJS
        temp261 = self.OPS
        temp262 = self.ROLES

        def temp263(arg0, arg1, arg2):
            for r in temp262:
                for op in temp261:
                    for obj in temp260:
                        temp253 = (session, r)
                        temp254 = self.SR
                        temp255 = (temp253 in temp254)
                        temp256 = (op, obj)
                        temp257 = (temp256, r)
                        temp258 = self.PR
                        temp259 = (temp257 in temp258)
                        if (temp255 and temp259):
                            temp252 = (op, obj)
                            yield temp252
        temp264 = temp263(temp260, temp261, temp262)
        temp265 = temp264
        temp266 = set(temp265)
        return temp266

    def RoleOperationsOnObject(self, role, obj):
        temp267 = self.ROLES
        assert (role in temp267)
        temp268 = self.OBJS
        assert (obj in temp268)
        temp272 = self.OPS

        def temp273(arg0):
            for op in temp272:
                temp269 = (op, obj)
                temp270 = (temp269, role)
                temp271 = self.PR
                if (temp270 in temp271):
                    yield op
        temp274 = temp273(temp272)
        temp275 = temp274
        temp276 = set(temp275)
        return temp276

    def UserOperationsOnObject(self, user, obj):
        temp277 = self.USERS
        assert (user in temp277)
        temp278 = self.OBJS
        assert (obj in temp278)
        temp286 = self.ROLES
        temp287 = self.OPS

        def temp288(arg0, arg1):
            for op in temp287:
                for r in temp286:
                    temp279 = (user, r)
                    temp280 = self.UR
                    temp281 = (temp279 in temp280)
                    temp282 = (op, obj)
                    temp283 = (temp282, r)
                    temp284 = self.PR
                    temp285 = (temp283 in temp284)
                    if (temp281 and temp285):
                        yield op
        temp289 = temp288(temp286, temp287)
        temp290 = temp289
        temp291 = set(temp290)
        return temp291

    def AddOperation(self, operation):
        temp292 = self.OPS
        temp293 = temp292.add
        temp293(operation)

    def AddObject(self, OBJ):
        temp294 = self.OBJS
        temp295 = temp294.add
        temp295(OBJ)

    def AddPermission(self, operation, obj):
        pass

    def checkSSD(self):
        temp309 = self.SsdNC
        temp310 = self.USERS

        def temp311(arg0, arg1):
            for u in temp310:
                for (name, c) in temp309:
                    temp300 = self.ROLES

                    def temp301(arg0):
                        for r in temp300:
                            temp298 = (u, r)
                            temp299 = self.UR
                            if (temp298 in temp299):
                                yield r
                    temp302 = temp301(temp300)
                    temp303 = temp302

                    def temp304(arg0):
                        for r in :
                            temp296 = (name, r)
                            temp297 = self.SsdNR
                            if (temp296 in temp297):
                                yield r
                    temp305 = temp304(set(temp303))
                    temp306 = temp305
                    temp307 = set(temp306)
                    temp308 = len(temp307)
                    if (temp308 > c):
                        yield u
        temp312 = temp311(temp309, temp310)
        temp313 = temp312
        temp314 = set(temp313)
        temp315 = bool(temp314)
        temp316 = (not temp315)
        return temp316

    def AssignUser(self, user, role):
        temp317 = self.USERS
        assert (user in temp317)
        temp318 = self.ROLES
        assert (role in temp318)
        temp319 = (user, role)
        temp320 = self.UR
        assert (temp319 not in temp320)
        temp321 = self.UR
        temp322 = temp321.add
        temp323 = (user, role)
        temp322(temp323)
        temp324 = self.checkSSD
        temp324()

    def CreateSsdSet(self, name, roles, c):
        temp325 = self.SsdNAMES
        assert (name not in temp325)
        temp326 = roles.issubset
        temp327 = self.ROLES
        assert temp326(temp327)
        assert (1 <= c <= len(roles) - 1)
        AddedSsdNR = set()
        for r in roles:
            temp328 = (name, r)
            temp329 = self.SsdNR
            temp335 = (temp328 not in temp329)
            if temp335:
                temp330 = AddedSsdNR.add
                temp331 = (name, r)
                temp330(temp331)
                temp332 = self.SsdNR
                temp333 = temp332.add
                temp334 = (name, r)
                temp333(temp334)
        AddedSsdNC = set()
        temp336 = (name, c)
        temp337 = self.SsdNC
        temp343 = (temp336 not in temp337)
        if temp343:
            temp338 = AddedSsdNC.add
            temp339 = (name, c)
            temp338(temp339)
            temp340 = self.SsdNC
            temp341 = temp340.add
            temp342 = (name, c)
            temp341(temp342)
        temp344 = self.checkSSD
        assert temp344()
        for (name, r) in AddedSsdNR:
            temp345 = self.SsdNR
            temp346 = temp345.remove
            temp347 = (name, r)
            temp346(temp347)
        for (name, c) in AddedSsdNC:
            temp348 = self.SsdNC
            temp349 = temp348.remove
            temp350 = (name, c)
            temp349(temp350)
        temp351 = self.SsdNAMES
        temp352 = temp351.add
        temp352(name)

        def temp354(arg0):
            for r in roles:
                temp353 = (name, r)
                yield temp353
        temp355 = temp354(roles)
        temp356 = temp355
        self.SsdNR|=set(temp356)
        temp357 = self.SsdNC
        temp358 = temp357.add
        temp359 = (name, c)
        temp358(temp359)

    def DeleteSsdSet(self, name):
        temp360 = self.SsdNAMES
        assert (name in temp360)
        temp362 = self.SsdRoleSetRoles

        def temp363(arg0):
            for r in :
                temp361 = (name, r)
                yield temp361
        temp364 = temp363(temp362(name))
        temp365 = temp364
        self.SsdNR-=set(temp365)
        temp366 = self.SsdNC
        temp367 = temp366.remove
        temp368 = self.SsdRoleSetCardinality
        temp369 = temp368(name)
        temp370 = (name, temp369)
        temp367(temp370)
        temp371 = self.SsdNAMES
        temp372 = temp371.remove
        temp372(name)

    def AddSsdRoleMember(self, name, role):
        temp373 = self.SsdNAMES
        assert (name in temp373)
        temp374 = self.ROLES
        assert (role in temp374)
        temp375 = self.SsdRoleSetRoles
        temp376 = temp375(name)
        assert (role not in temp376)
        AddedSsdNR = set()
        temp377 = (name, role)
        temp378 = self.SsdNR
        temp384 = (temp377 not in temp378)
        if temp384:
            temp379 = AddedSsdNR.add
            temp380 = (name, role)
            temp379(temp380)
            temp381 = self.SsdNR
            temp382 = temp381.add
            temp383 = (name, role)
            temp382(temp383)
        temp385 = self.checkSSD
        assert temp385()
        for (name, r) in AddedSsdNR:
            temp386 = self.SsdNR
            temp387 = temp386.remove
            temp388 = (name, r)
            temp387(temp388)
        temp389 = self.SsdNR
        temp390 = temp389.add
        temp391 = (name, role)
        temp390(temp391)

    def DeleteSsdRoleMember(self, name, role):
        temp392 = self.SsdNAMES
        assert (name in temp392)
        temp393 = self.SsdRoleSetRoles
        temp394 = temp393(name)
        assert (role in temp394)
        temp395 = self.SsdRoleSetCardinality
        temp399 = temp395(name)
        temp397 = self.SsdRoleSetRoles
        temp398 = temp397(name)
        temp396 = len(temp398)
        temp400 = temp396 - 2
        assert (temp399 <= temp400)
        temp401 = self.SsdNR
        temp402 = temp401.remove
        temp403 = (name, role)
        temp402(temp403)

    def SetSsdSetCardinality(self, name, c):
        temp404 = self.SsdNAMES
        assert (name in temp404)
        assert (1 <= c <= len(self.SsdRoleSetRoles(name)) - 1)
        NegSsdNC = set()
        temp405 = self.SsdRoleSetCardinality
        temp406 = temp405(name)
        temp407 = (name, temp406)
        temp416 = set(temp407)
        for (name, c) in temp416:
            temp408 = (name, c)
            temp409 = self.SsdNC
            temp415 = (temp408 in temp409)
            if temp415:
                temp410 = self.SsdNC
                temp411 = temp410.remove
                temp412 = (name, c)
                temp411(temp412)
                temp413 = NegSsdNC.add
                temp414 = (name, c)
                temp413(temp414)
        PosSsdNC = set()
        temp417 = (name, c)
        temp418 = self.SsdNC
        temp424 = (temp417 not in temp418)
        if temp424:
            temp419 = self.SsdNC
            temp420 = temp419.add
            temp421 = (name, c)
            temp420(temp421)
            temp422 = PosSsdNC.add
            temp423 = (name, c)
            temp422(temp423)
        temp425 = self.checkSSD
        assert temp425()
        for (name, c) in PosSsdNC:
            temp426 = self.SsdNC
            temp427 = temp426.remove
            temp428 = (name, c)
            temp427(temp428)
        for (name, c) in NegSsdNC:
            temp429 = self.SsdNC
            temp430 = temp429.add
            temp431 = (name, c)
            temp430(temp431)
        temp432 = self.SsdNC
        temp433 = temp432.remove
        temp434 = self.SsdRoleSetCardinality
        temp435 = temp434(name)
        temp436 = (name, temp435)
        temp433(temp436)
        temp437 = self.SsdNC
        temp438 = temp437.add
        temp439 = (name, c)
        temp438(temp439)
        pass

    def SsdRoleSets(self):
        temp440 = self.SsdNAMES
        return temp440

    def SsdRoleSetRoles(self, name):
        temp441 = self.SsdNAMES
        assert (name in temp441)
        temp442 = self.SsdNR

        def temp443(arg0):
            for (n, r) in temp442:
                if (n == name):
                    yield r
        temp444 = temp443(temp442)
        temp445 = temp444
        temp446 = set(temp445)
        return temp446

    def SsdRoleSetCardinality(self, name):
        temp447 = self.SsdNAMES
        assert (name in temp447)
        temp448 = self.SsdNC

        def temp449(arg0):
            for (n, c) in temp448:
                if (n == name):
                    yield c
        temp450 = temp449(temp448)
        temp451 = temp450
        temp452 = set(temp451)
        temp453 = temp452.pop
        temp454 = temp453()
        return temp454

    def checkDSD(self):
        temp468 = self.DsdNC
        temp469 = self.SESSIONS

        def temp470(arg0, arg1):
            for s in temp469:
                for (name, c) in temp468:
                    temp459 = self.ROLES

                    def temp460(arg0):
                        for r in temp459:
                            temp457 = (s, r)
                            temp458 = self.UR
                            if (temp457 in temp458):
                                yield r
                    temp461 = temp460(temp459)
                    temp462 = temp461

                    def temp463(arg0):
                        for r in :
                            temp455 = (name, r)
                            temp456 = self.DsdNR
                            if (temp455 in temp456):
                                yield r
                    temp464 = temp463(set(temp462))
                    temp465 = temp464
                    temp466 = set(temp465)
                    temp467 = len(temp466)
                    if (temp467 > c):
                        yield s
        temp471 = temp470(temp468, temp469)
        temp472 = temp471
        temp473 = set(temp472)
        temp474 = bool(temp473)
        temp475 = (not temp474)
        return temp475

    def CreateDsdSet(self, name, roles, c):
        temp476 = self.DsdNAMES
        assert (name not in temp476)
        temp477 = roles.issubset
        temp478 = self.ROLES
        assert temp477(temp478)
        assert (1 <= c <= len(roles) - 1)
        negDsdNR = set()
        for r in roles:
            temp479 = (name, r)
            temp480 = self.DsdNR
            temp486 = (temp479 not in temp480)
            if temp486:
                temp481 = self.DsdNR
                temp482 = temp481.add
                temp483 = (name, r)
                temp482(temp483)
                temp484 = negDsdNR.add
                temp485 = (name, r)
                temp484(temp485)
        negDsdNC = set()
        temp487 = (name, c)
        temp488 = self.DsdNC
        temp494 = (temp487 not in temp488)
        if temp494:
            temp489 = self.DsdNC
            temp490 = temp489.add
            temp491 = (name, c)
            temp490(temp491)
            temp492 = negDsdNC.add
            temp493 = (name, c)
            temp492(temp493)
        temp495 = self.checkDSD
        assert temp495()
        temp496 = self.DsdNAMES
        temp497 = temp496.add
        temp497(name)

    def DeleteDsdSet(self, name):
        temp498 = self.DsdNAMES
        assert (name in temp498)
        temp500 = self.DsdRoleSetRoles

        def temp501(arg0):
            for r in :
                temp499 = (name, r)
                yield temp499
        temp502 = temp501(temp500(name))
        temp503 = temp502
        self.DsdNR-=set(temp503)
        temp504 = self.DsdNC
        temp505 = temp504.remove
        temp506 = self.DsdRoleSetCardinality
        temp507 = temp506(name)
        temp508 = (name, temp507)
        temp505(temp508)
        temp509 = self.DsdNAMES
        temp510 = temp509.remove
        temp510(name)

    def AddDsdRoleMember(self, name, role):
        temp511 = self.DsdNAMES
        assert (name in temp511)
        temp512 = self.ROLES
        assert (role in temp512)
        temp513 = self.DsdRoleSetRoles
        temp514 = temp513(name)
        assert (role not in temp514)
        temp515 = self.DsdNR
        temp516 = temp515.add
        temp517 = (name, role)
        temp516(temp517)
        temp518 = self.checkDSD
        assert temp518()

    def DeleteDsdRoleMember(self, name, role):
        temp519 = self.DsdNAMES
        assert (name in temp519)
        temp520 = self.DsdRoleSetRoles
        temp521 = temp520(name)
        assert (role in temp521)
        temp522 = self.DsdRoleSetCardinality
        temp526 = temp522(name)
        temp524 = self.DsdRoleSetRoles
        temp525 = temp524(name)
        temp523 = len(temp525)
        temp527 = temp523 - 2
        assert (temp526 <= temp527)
        temp528 = self.DsdNR
        temp529 = temp528.remove
        temp530 = (name, role)
        temp529(temp530)

    def SetDsdSetCardinality(self, name, c):
        temp531 = self.DsdNAMES
        assert (name in temp531)
        assert (1 <= c <= len(self.DsdRoleSetRoles(name)) - 1)
        temp532 = self.DsdNC
        temp533 = temp532.remove
        temp534 = self.DsdRoleSetCardinality
        temp535 = temp534(name)
        temp536 = (name, temp535)
        temp533(temp536)
        temp537 = self.DsdNC
        temp538 = temp537.add
        temp539 = (name, c)
        temp538(temp539)
        temp540 = self.checkDSD
        assert temp540()

    def DsdRoleSets(self):
        temp541 = self.DsdNAMES
        return temp541

    def DsdRoleSetRoles(self, name):
        temp542 = self.DsdNAMES
        assert (name in temp542)
        temp543 = self.DsdNR

        def temp544(arg0):
            for (n, r) in temp543:
                if (n == name):
                    yield r
        temp545 = temp544(temp543)
        temp546 = temp545
        temp547 = set(temp546)
        return temp547

    def DsdRoleSetCardinality(self, name):
        temp548 = self.DsdNAMES
        assert (name in temp548)
        temp549 = self.DsdNC

        def temp550(arg0):
            for (n, c) in temp549:
                if (n == name):
                    yield c
        temp551 = temp550(temp549)
        temp552 = temp551
        temp553 = set(temp552)
        temp554 = temp553.pop
        temp555 = temp554()
        return temp555
