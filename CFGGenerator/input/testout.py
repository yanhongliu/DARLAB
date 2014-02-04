import sets


class coreRBAC:

    def __init__(self):
        self.OBJS = sets.Set()
        self.MapR2P_8_1__EXPR__ = sets.MultiMap()
        self.OPS = sets.Set()
        self.MapRO2A_9_1__EXPR__ = sets.MultiMap()
        self.MapRO2A_9_1__EXPR__ = sets.MultiMap()
        self.MapR2P_8_1__EXPR__ = sets.MultiMap()
        self.USERS = sets.Set()
        self.MapR2SU_12_1__EXPR__ = sets.MultiMap()
        self.MapR2U_7_1__EXPR__ = sets.MultiMap()
        self.ROLES = sets.Set()
        self.MapS2P_14_1__EXPR__ = sets.MultiMap()
        self.SRMapR2S_14_1__EXPR__ = sets.MultiMap()
        self.PRMapR2P_14_1__EXPR__ = sets.MultiMap()
        self.MapU2P_13_1__EXPR__ = sets.MultiMap()
        self.URMapR2U = sets.MultiMap()
        self.PRMapR2P_13_1__EXPR__ = sets.MultiMap()
        self.MapS2R_6_1__EXPR__ = sets.MultiMap()
        self.MapU2R_5_1__EXPR__ = sets.MultiMap()
        self.MapSP2R = sets.MultiMap()
        self.PR = sets.Set()
        self.MapS2P_14_1__EXPR__ = sets.MultiMap()
        self.PRMapR2P_14_1__EXPR__ = sets.MultiMap()
        self.MapU2P_13_1__EXPR__ = sets.MultiMap()
        self.PRMapR2P_13_1__EXPR__ = sets.MultiMap()
        self.MapRO2A_9_1__EXPR__ = sets.MultiMap()
        self.MapRO2A_9_1__EXPR__ = sets.MultiMap()
        self.MapR2P_8_1__EXPR__ = sets.MultiMap()
        self.MapSP2R = sets.MultiMap()
        self.PRMapR2P = sets.MultiMap()
        self.UR = sets.Set()
        self.MapU2P_13_1__EXPR__ = sets.MultiMap()
        self.URMapR2U = sets.MultiMap()
        self.MapR2U_7_1__EXPR__ = sets.MultiMap()
        self.URMapU2R_7_1__EXPR__ = sets.MultiMap()
        self.MapU2R_5_1__EXPR__ = sets.MultiMap()
        self.URMapR2U = sets.MultiMap()
        self.SESSIONS = sets.Set()
        self.MapR2SU_12_1__EXPR__ = sets.MultiMap()
        self.MapUR2S_11_1__EXPR__ = sets.MultiMap()
        self.MapU2S_10_1__EXPR__ = sets.MultiMap()
        self.SU = sets.Set()
        self.SUMapS2U_12_1__EXPR__ = sets.MultiMap()
        self.SUMapU2S_12_1__EXPR__ = sets.MultiMap()
        self.MapR2SU_12_1__EXPR__ = sets.MultiMap()
        self.MapUR2S_11_1__EXPR__ = sets.MultiMap()
        self.SUMapS2U_11_1__EXPR__ = sets.MultiMap()
        self.MapU2S_10_1__EXPR__ = sets.MultiMap()
        self.SUMapS2U_10_1__EXPR__ = sets.MultiMap()
        self.SR = sets.Set()
        self.MapU2P_14_1__EXPR__ = sets.MultiMap()
        self.SRMapR2S_14_1__EXPR__ = sets.MultiMap()
        self.SRMapS2R = sets.MultiMap()
        self.MapR2SU_12_1__EXPR__ = sets.MultiMap()
        self.MapUR2S_11_1__EXPR__ = sets.MultiMap()
        self.SRMapS2R = sets.MultiMap()
        self.MapS2R_6_1__EXPR__ = sets.MultiMap()
        self.SRMapR2S_6_1__EXPR__ = sets.MultiMap()
        self.MapSP2R = sets.MultiMap()
        self.SRMapR2S = sets.MultiMap()

    def AddUser(self, user):
        temp0 = self.USERS
        assert (user not in temp0)
        temp1 = self.USERS
        temp1.add(user)
        temp2 = self.SUMapU2S_12_1__EXPR__
        for s in temp2.get(user):
            temp3 = self.SESSIONS
            if (s in temp3):
                temp4 = self.SRMapS2R
                for r in temp4.get(s):
                    temp6 = (s, user)
                    temp5 = self.MapR2SU_12_1__EXPR__
                    temp7 = temp5.get(r)
                    if (temp6 not in temp7):
                        temp8 = self.MapR2SU_12_1__EXPR__
                        temp9 = (s, user)
                        temp8.add(r, temp9)
        temp10 = self.URMapU2R_7_1__EXPR__
        for r in temp10.get(user):
            temp11 = self.MapR2U_7_1__EXPR__
            temp12 = temp11.get(r)
            if (user not in temp12):
                temp13 = self.MapR2U_7_1__EXPR__
                temp13.add(r, user)

    def DeleteUser(self, user):
        temp14 = self.USERS
        assert (user in temp14)
        temp15 = self.URMapU2R
        temp16 = temp15.get(user)
        for r in temp16.copy():
            temp17 = self.ROLES
            if (r in temp17):
                temp18 = self.MapU2R_5_1__EXPR__
                temp19 = temp18.get(user)
                if (r in temp19):
                    temp20 = self.MapU2R_5_1__EXPR__
                    temp20.remove(user, r)
            temp21 = self.URMapR2U
            temp21.remove(r, user)
            temp22 = self.USERS
            if (user in temp22):
                temp23 = self.MapR2U_7_1__EXPR__
                temp24 = temp23.get(r)
                if (user in temp24):
                    temp25 = self.MapR2U_7_1__EXPR__
                    temp25.remove(r, user)
            temp26 = self.URMapU2R_7_1__EXPR__
            temp26.remove(user, r)
            temp27 = self.PRMapR2P_13_1__EXPR__
            for (op, obj) in temp27.get(r):
                temp28 = self.OPS
                if (op in temp28):
                    temp29 = self.OBJS
                    if (obj in temp29):
                        temp31 = (op, obj)
                        temp30 = self.MapU2P_13_1__EXPR__
                        temp32 = temp30.get(user)
                        if (temp31 in temp32):
                            temp33 = self.MapU2P_13_1__EXPR__
                            temp34 = (op, obj)
                            temp33.remove(user, temp34)
            temp35 = self.URMapR2U
            temp35.remove(r, user)
            temp36 = self.UR
            temp37 = (user, r)
            temp36.remove(temp37)
        temp38 = self.MapU2S_10_1__EXPR__
        for s in temp38.get(user):
            self.DeleteSession(user, s)
        temp39 = self.URMapU2R_7_1__EXPR__
        for r in temp39.get(user):
            temp40 = self.MapR2U_7_1__EXPR__
            temp41 = temp40.get(r)
            if (user in temp41):
                temp42 = self.MapR2U_7_1__EXPR__
                temp42.remove(r, user)
        temp43 = self.SUMapU2S_12_1__EXPR__
        for s in temp43.get(user):
            temp44 = self.SESSIONS
            if (s in temp44):
                temp45 = self.SRMapS2R
                for r in temp45.get(s):
                    temp47 = (s, user)
                    temp46 = self.MapR2SU_12_1__EXPR__
                    temp48 = temp46.get(r)
                    if (temp47 in temp48):
                        temp49 = self.MapR2SU_12_1__EXPR__
                        temp50 = (s, user)
                        temp49.remove(r, temp50)
        temp51 = self.USERS
        temp51.remove(user)

    def AddRole(self, role):
        temp52 = self.ROLES
        assert (role not in temp52)
        temp53 = self.ROLES
        temp53.add(role)
        temp54 = self.PRMapR2P_14_1__EXPR__
        for (op, obj) in temp54.get(role):
            temp55 = self.SRMapR2S_14_1__EXPR__
            for s in temp55.get(role):
                temp56 = self.OPS
                if (op in temp56):
                    temp57 = self.OBJS
                    if (obj in temp57):
                        temp59 = (op, obj)
                        temp58 = self.MapS2P_14_1__EXPR__
                        temp60 = temp58.get(s)
                        if (temp59 not in temp60):
                            temp61 = self.MapS2P_14_1__EXPR__
                            temp62 = (op, obj)
                            temp61.add(s, temp62)
        temp63 = self.PRMapR2P_13_1__EXPR__
        for (op, obj) in temp63.get(role):
            temp64 = self.URMapR2U
            for u in temp64.get(role):
                temp65 = self.OPS
                if (op in temp65):
                    temp66 = self.OBJS
                    if (obj in temp66):
                        temp68 = (op, obj)
                        temp67 = self.MapU2P_13_1__EXPR__
                        temp69 = temp67.get(u)
                        if (temp68 not in temp69):
                            temp70 = self.MapU2P_13_1__EXPR__
                            temp71 = (op, obj)
                            temp70.add(u, temp71)
        temp72 = self.SRMapR2S_6_1__EXPR__
        for s in temp72.get(role):
            temp73 = self.MapS2R_6_1__EXPR__
            temp74 = temp73.get(s)
            if (role not in temp74):
                temp75 = self.MapS2R_6_1__EXPR__
                temp75.add(s, role)
        temp76 = self.URMapR2U
        for u in temp76.get(role):
            temp77 = self.MapU2R_5_1__EXPR__
            temp78 = temp77.get(u)
            if (role not in temp78):
                temp79 = self.MapU2R_5_1__EXPR__
                temp79.add(u, role)
        temp80 = self.SRMapR2S
        for s in temp80.get(role):
            temp81 = self.PRMapR2P
            for (op, obj) in temp81.get(role):
                temp82 = self.MapSP2R
                temp83 = (s, op, obj)
                temp84 = temp82.get(temp83)
                if (role not in temp84):
                    temp85 = self.MapSP2R
                    temp86 = (s, op, obj)
                    temp85.add(temp86, role)

    def DeleteRole(self, role):
        temp87 = self.ROLES
        assert (role in temp87)
        temp88 = self.SRMapR2S
        for s in temp88.get(role):
            temp89 = self.PRMapR2P
            for (op, obj) in temp89.get(role):
                temp90 = self.MapSP2R
                temp91 = (s, op, obj)
                temp92 = temp90.get(temp91)
                if (role in temp92):
                    temp93 = self.MapSP2R
                    temp94 = (s, op, obj)
                    temp93.remove(temp94, role)
        temp95 = self.URMapR2U
        for u in temp95.get(role):
            temp96 = self.MapU2R_5_1__EXPR__
            temp97 = temp96.get(u)
            if (role in temp97):
                temp98 = self.MapU2R_5_1__EXPR__
                temp98.remove(u, role)
        temp99 = self.SRMapR2S_6_1__EXPR__
        for s in temp99.get(role):
            temp100 = self.MapS2R_6_1__EXPR__
            temp101 = temp100.get(s)
            if (role in temp101):
                temp102 = self.MapS2R_6_1__EXPR__
                temp102.remove(s, role)
        temp103 = self.PRMapR2P_13_1__EXPR__
        for (op, obj) in temp103.get(role):
            temp104 = self.URMapR2U
            for u in temp104.get(role):
                temp105 = self.OPS
                if (op in temp105):
                    temp106 = self.OBJS
                    if (obj in temp106):
                        temp108 = (op, obj)
                        temp107 = self.MapU2P_13_1__EXPR__
                        temp109 = temp107.get(u)
                        if (temp108 in temp109):
                            temp110 = self.MapU2P_13_1__EXPR__
                            temp111 = (op, obj)
                            temp110.remove(u, temp111)
        temp112 = self.PRMapR2P_14_1__EXPR__
        for (op, obj) in temp112.get(role):
            temp113 = self.SRMapR2S_14_1__EXPR__
            for s in temp113.get(role):
                temp114 = self.OPS
                if (op in temp114):
                    temp115 = self.OBJS
                    if (obj in temp115):
                        temp117 = (op, obj)
                        temp116 = self.MapS2P_14_1__EXPR__
                        temp118 = temp116.get(s)
                        if (temp117 in temp118):
                            temp119 = self.MapS2P_14_1__EXPR__
                            temp120 = (op, obj)
                            temp119.remove(s, temp120)
        temp121 = self.ROLES
        temp121.remove(role)
        temp122 = self.PRMapR2P
        temp123 = temp122.get(role)
        for (op, obj) in temp123.copy():
            temp124 = self.ROLES
            if (role in temp124):
                temp125 = self.SRMapR2S
                for s in temp125.get(role):
                    temp126 = self.MapSP2R
                    temp127 = (s, op, obj)
                    temp128 = temp126.get(temp127)
                    if (role in temp128):
                        temp129 = self.MapSP2R
                        temp130 = (s, op, obj)
                        temp129.add(temp130, role)
            temp131 = self.PRMapR2P
            temp132 = (op, obj)
            temp131.remove(role, temp132)
            temp133 = self.OPS
            if (op in temp133):
                temp134 = self.OBJS
                if (obj in temp134):
                    temp136 = (op, obj)
                    temp135 = self.MapR2P_8_1__EXPR__
                    temp137 = temp135.get(role)
                    if (temp136 in temp137):
                        temp138 = self.MapR2P_8_1__EXPR__
                        temp139 = (op, obj)
                        temp138.remove(role, temp139)
            temp140 = self.OPS
            if (op in temp140):
                temp141 = self.MapRO2A_9_1__EXPR__
                temp142 = (role, obj)
                temp143 = temp141.get(temp142)
                if (op in temp143):
                    temp144 = self.MapRO2A_9_1__EXPR__
                    temp145 = (role, obj)
                    temp144.remove(temp145, op)
            temp146 = self.OPS
            if (op in temp146):
                temp147 = self.MapRO2A_9_1__EXPR__
                temp148 = (role, obj)
                temp149 = temp147.get(temp148)
                if (op in temp149):
                    temp150 = self.MapRO2A_9_1__EXPR__
                    temp151 = (role, obj)
                    temp150.remove(temp151, op)
            temp152 = self.URMapR2U
            for u in temp152.get(role):
                temp153 = self.OPS
                if (op in temp153):
                    temp154 = self.OBJS
                    if (obj in temp154):
                        temp156 = (op, obj)
                        temp155 = self.MapU2P_13_1__EXPR__
                        temp157 = temp155.get(u)
                        if (temp156 in temp157):
                            temp158 = self.MapU2P_13_1__EXPR__
                            temp159 = (op, obj)
                            temp158.remove(u, temp159)
            temp160 = self.PRMapR2P_13_1__EXPR__
            temp161 = (op, obj)
            temp160.remove(role, temp161)
            temp162 = self.ROLES
            if (role in temp162):
                temp163 = self.SRMapR2S_14_1__EXPR__
                for s in temp163.get(role):
                    temp164 = self.OPS
                    if (op in temp164):
                        temp165 = self.OBJS
                        if (obj in temp165):
                            temp167 = (op, obj)
                            temp166 = self.MapS2P_14_1__EXPR__
                            temp168 = temp166.get(s)
                            if (temp167 in temp168):
                                temp169 = self.MapS2P_14_1__EXPR__
                                temp170 = (op, obj)
                                temp169.remove(s, temp170)
                temp171 = self.PRMapR2P_14_1__EXPR__
                temp172 = (op, obj)
                temp171.remove(role, temp172)
            temp173 = self.PR
            temp174 = ((op, obj), role)
            temp173.remove(temp174)
        temp175 = self.URMapR2U
        temp176 = temp175.get(role)
        for u in temp176.copy():
            temp177 = self.ROLES
            if (role in temp177):
                temp178 = self.MapU2R_5_1__EXPR__
                temp179 = temp178.get(u)
                if (role in temp179):
                    temp180 = self.MapU2R_5_1__EXPR__
                    temp180.remove(u, role)
            temp181 = self.URMapR2U
            temp181.remove(role, u)
            temp182 = self.USERS
            if (u in temp182):
                temp183 = self.MapR2U_7_1__EXPR__
                temp184 = temp183.get(role)
                if (u in temp184):
                    temp185 = self.MapR2U_7_1__EXPR__
                    temp185.remove(role, u)
            temp186 = self.URMapU2R_7_1__EXPR__
            temp186.remove(u, role)
            temp187 = self.PRMapR2P_13_1__EXPR__
            for (op, obj) in temp187.get(role):
                temp188 = self.OPS
                if (op in temp188):
                    temp189 = self.OBJS
                    if (obj in temp189):
                        temp191 = (op, obj)
                        temp190 = self.MapU2P_13_1__EXPR__
                        temp192 = temp190.get(u)
                        if (temp191 in temp192):
                            temp193 = self.MapU2P_13_1__EXPR__
                            temp194 = (op, obj)
                            temp193.remove(u, temp194)
            temp195 = self.URMapR2U
            temp195.remove(role, u)
            temp196 = self.UR
            temp197 = (u, role)
            temp196.remove(temp197)
        temp198 = self.MapR2SU_12_1__EXPR__
        for (s, u) in temp198.get(role):
            self.DeleteSession(u, s)

    def AssignUser(self, user, role):
        temp199 = self.USERS
        assert (user in temp199)
        temp200 = self.ROLES
        assert (role in temp200)
        temp201 = (user, role)
        temp202 = self.UR
        assert (temp201 not in temp202)
        temp203 = self.UR
        temp204 = (user, role)
        temp203.add(temp204)
        temp205 = self.PRMapR2P_13_1__EXPR__
        for (op, obj) in temp205.get(role):
            temp206 = self.OPS
            if (op in temp206):
                temp207 = self.OBJS
                if (obj in temp207):
                    temp209 = (op, obj)
                    temp208 = self.MapU2P_13_1__EXPR__
                    temp210 = temp208.get(user)
                    if (temp209 not in temp210):
                        temp211 = self.MapU2P_13_1__EXPR__
                        temp212 = (op, obj)
                        temp211.add(user, temp212)
        temp213 = self.URMapR2U
        temp213.add(role, user)
        temp214 = self.USERS
        if (user in temp214):
            temp215 = self.MapR2U_7_1__EXPR__
            temp216 = temp215.get(role)
            if (user not in temp216):
                temp217 = self.MapR2U_7_1__EXPR__
                temp217.add(role, user)
        temp218 = self.URMapU2R_7_1__EXPR__
        temp218.add(user, role)
        temp219 = self.ROLES
        if (role in temp219):
            temp220 = self.MapU2R_5_1__EXPR__
            temp221 = temp220.get(user)
            if (role not in temp221):
                temp222 = self.MapU2R_5_1__EXPR__
                temp222.add(user, role)
        temp223 = self.URMapR2U
        temp223.add(role, user)

    def DeassignUser(self, user, role):
        temp224 = self.USERS
        assert (user in temp224)
        temp225 = self.ROLES
        assert (role in temp225)
        temp226 = (user, role)
        temp227 = self.UR
        assert (temp226 in temp227)
        temp228 = self.ROLES
        if (role in temp228):
            temp229 = self.MapU2R_5_1__EXPR__
            temp230 = temp229.get(user)
            if (role in temp230):
                temp231 = self.MapU2R_5_1__EXPR__
                temp231.remove(user, role)
        temp232 = self.URMapR2U
        temp232.remove(role, user)
        temp233 = self.USERS
        if (user in temp233):
            temp234 = self.MapR2U_7_1__EXPR__
            temp235 = temp234.get(role)
            if (user in temp235):
                temp236 = self.MapR2U_7_1__EXPR__
                temp236.remove(role, user)
        temp237 = self.URMapU2R_7_1__EXPR__
        temp237.remove(user, role)
        temp238 = self.PRMapR2P_13_1__EXPR__
        for (op, obj) in temp238.get(role):
            temp239 = self.OPS
            if (op in temp239):
                temp240 = self.OBJS
                if (obj in temp240):
                    temp242 = (op, obj)
                    temp241 = self.MapU2P_13_1__EXPR__
                    temp243 = temp241.get(user)
                    if (temp242 in temp243):
                        temp244 = self.MapU2P_13_1__EXPR__
                        temp245 = (op, obj)
                        temp244.remove(user, temp245)
        temp246 = self.URMapR2U
        temp246.remove(role, user)
        temp247 = self.UR
        temp248 = (user, role)
        temp247.remove(temp248)
        temp249 = self.MapUR2S_11_1__EXPR__
        temp250 = (user, role)
        for s in temp249.get(temp250):
            self.DeleteSession(user, s)

    def GrantPermission(self, operation, object, role):
        temp251 = self.OPS
        temp252 = (operation in temp251)
        temp253 = self.OBJS
        temp254 = (object in temp253)
        assert (temp252 and temp254)
        temp255 = self.ROLES
        assert (role in temp255)
        temp256 = ((operation, object), role)
        temp257 = self.PR
        assert (temp256 not in temp257)
        temp258 = self.PR
        temp259 = ((operation, object), role)
        temp258.add(temp259)
        temp260 = self.ROLES
        if (role in temp260):
            temp261 = self.SRMapR2S_14_1__EXPR__
            for s in temp261.get(role):
                temp262 = self.OPS
                if (operation in temp262):
                    temp263 = self.OBJS
                    if (object in temp263):
                        temp265 = (operation, object)
                        temp264 = self.MapS2P_14_1__EXPR__
                        temp266 = temp264.get(s)
                        if (temp265 not in temp266):
                            temp267 = self.MapS2P_14_1__EXPR__
                            temp268 = (operation, object)
                            temp267.add(s, temp268)
            temp269 = self.PRMapR2P_14_1__EXPR__
            temp270 = (operation, object)
            temp269.add(role, temp270)
        temp271 = self.URMapR2U
        for u in temp271.get(role):
            temp272 = self.OPS
            if (operation in temp272):
                temp273 = self.OBJS
                if (object in temp273):
                    temp275 = (operation, object)
                    temp274 = self.MapU2P_13_1__EXPR__
                    temp276 = temp274.get(u)
                    if (temp275 not in temp276):
                        temp277 = self.MapU2P_13_1__EXPR__
                        temp278 = (operation, object)
                        temp277.add(u, temp278)
        temp279 = self.PRMapR2P_13_1__EXPR__
        temp280 = (operation, object)
        temp279.add(role, temp280)
        temp281 = self.OPS
        if (operation in temp281):
            temp282 = self.MapRO2A_9_1__EXPR__
            temp283 = (role, object)
            temp284 = temp282.get(temp283)
            if (operation not in temp284):
                temp285 = self.MapRO2A_9_1__EXPR__
                temp286 = (role, object)
                temp285.add(temp286, operation)
        temp287 = self.OPS
        if (operation in temp287):
            temp288 = self.MapRO2A_9_1__EXPR__
            temp289 = (role, object)
            temp290 = temp288.get(temp289)
            if (operation not in temp290):
                temp291 = self.MapRO2A_9_1__EXPR__
                temp292 = (role, object)
                temp291.add(temp292, operation)
        temp293 = self.OPS
        if (operation in temp293):
            temp294 = self.OBJS
            if (object in temp294):
                temp296 = (operation, object)
                temp295 = self.MapR2P_8_1__EXPR__
                temp297 = temp295.get(role)
                if (temp296 not in temp297):
                    temp298 = self.MapR2P_8_1__EXPR__
                    temp299 = (operation, object)
                    temp298.add(role, temp299)
        temp300 = self.ROLES
        if (role in temp300):
            temp301 = self.SRMapR2S
            for s in temp301.get(role):
                temp302 = self.MapSP2R
                temp303 = (s, operation, object)
                temp304 = temp302.get(temp303)
                if (role not in temp304):
                    temp305 = self.MapSP2R
                    temp306 = (s, operation, object)
                    temp305.add(temp306, role)
        temp307 = self.PRMapR2P
        temp308 = (operation, object)
        temp307.add(role, temp308)

    def RevokePermission(self, operation, object, role):
        temp309 = self.OPS
        temp310 = (operation in temp309)
        temp311 = self.OBJS
        temp312 = (object in temp311)
        assert (temp310 and temp312)
        temp313 = self.ROLES
        assert (role in temp313)
        temp314 = ((operation, object), role)
        temp315 = self.PR
        assert (temp314 in temp315)
        temp316 = self.ROLES
        if (role in temp316):
            temp317 = self.SRMapR2S
            for s in temp317.get(role):
                temp318 = self.MapSP2R
                temp319 = (s, operation, object)
                temp320 = temp318.get(temp319)
                if (role in temp320):
                    temp321 = self.MapSP2R
                    temp322 = (s, operation, object)
                    temp321.add(temp322, role)
        temp323 = self.PRMapR2P
        temp324 = (operation, object)
        temp323.remove(role, temp324)
        temp325 = self.OPS
        if (operation in temp325):
            temp326 = self.OBJS
            if (object in temp326):
                temp328 = (operation, object)
                temp327 = self.MapR2P_8_1__EXPR__
                temp329 = temp327.get(role)
                if (temp328 in temp329):
                    temp330 = self.MapR2P_8_1__EXPR__
                    temp331 = (operation, object)
                    temp330.remove(role, temp331)
        temp332 = self.OPS
        if (operation in temp332):
            temp333 = self.MapRO2A_9_1__EXPR__
            temp334 = (role, object)
            temp335 = temp333.get(temp334)
            if (operation in temp335):
                temp336 = self.MapRO2A_9_1__EXPR__
                temp337 = (role, object)
                temp336.remove(temp337, operation)
        temp338 = self.OPS
        if (operation in temp338):
            temp339 = self.MapRO2A_9_1__EXPR__
            temp340 = (role, object)
            temp341 = temp339.get(temp340)
            if (operation in temp341):
                temp342 = self.MapRO2A_9_1__EXPR__
                temp343 = (role, object)
                temp342.remove(temp343, operation)
        temp344 = self.URMapR2U
        for u in temp344.get(role):
            temp345 = self.OPS
            if (operation in temp345):
                temp346 = self.OBJS
                if (object in temp346):
                    temp348 = (operation, object)
                    temp347 = self.MapU2P_13_1__EXPR__
                    temp349 = temp347.get(u)
                    if (temp348 in temp349):
                        temp350 = self.MapU2P_13_1__EXPR__
                        temp351 = (operation, object)
                        temp350.remove(u, temp351)
        temp352 = self.PRMapR2P_13_1__EXPR__
        temp353 = (operation, object)
        temp352.remove(role, temp353)
        temp354 = self.ROLES
        if (role in temp354):
            temp355 = self.SRMapR2S_14_1__EXPR__
            for s in temp355.get(role):
                temp356 = self.OPS
                if (operation in temp356):
                    temp357 = self.OBJS
                    if (object in temp357):
                        temp359 = (operation, object)
                        temp358 = self.MapS2P_14_1__EXPR__
                        temp360 = temp358.get(s)
                        if (temp359 in temp360):
                            temp361 = self.MapS2P_14_1__EXPR__
                            temp362 = (operation, object)
                            temp361.remove(s, temp362)
            temp363 = self.PRMapR2P_14_1__EXPR__
            temp364 = (operation, object)
            temp363.remove(role, temp364)
        temp365 = self.PR
        temp366 = ((operation, object), role)
        temp365.remove(temp366)

    def CreateSession(self, user, session, ars):
        temp367 = self.USERS
        assert (user in temp367)
        temp368 = self.SESSIONS
        assert (session not in temp368)
        temp369 = self.AssignedRoles(user)
        assert ars.issubset(temp369)
        temp370 = self.SU
        temp371 = (session, user)
        temp370.add(temp371)
        temp372 = self.SESSIONS
        if (session in temp372):
            temp373 = self.USERS
            if (user in temp373):
                temp374 = self.SRMapS2R
                for r in temp374.get(session):
                    temp376 = (session, user)
                    temp375 = self.MapR2SU_12_1__EXPR__
                    temp377 = temp375.get(r)
                    if (temp376 not in temp377):
                        temp378 = self.MapR2SU_12_1__EXPR__
                        temp379 = (session, user)
                        temp378.add(r, temp379)
        temp380 = self.SUMapS2U_12_1__EXPR__
        temp380.add(session, user)
        temp381 = self.SUMapU2S_12_1__EXPR__
        temp381.add(user, session)
        temp382 = self.SRMapS2R
        for r in temp382.get(session):
            temp383 = self.MapUR2S_11_1__EXPR__
            temp384 = (user, r)
            temp385 = temp383.get(temp384)
            if (session not in temp385):
                temp386 = self.MapUR2S_11_1__EXPR__
                temp387 = (user, r)
                temp386.add(temp387, session)
        temp388 = self.SUMapS2U_11_1__EXPR__
        temp388.add(session, user)
        temp389 = self.SESSIONS
        if (session in temp389):
            temp390 = self.MapU2S_10_1__EXPR__
            temp391 = temp390.get(user)
            if (session not in temp391):
                temp392 = self.MapU2S_10_1__EXPR__
                temp392.add(user, session)
        temp393 = self.SUMapS2U_10_1__EXPR__
        temp393.add(session, user)
        for r in ars:
            temp394 = self.SR
            temp395 = (session, r)
            temp394.add(temp395)
            temp396 = self.PRMapR2P_14_1__EXPR__
            for (op, obj) in temp396.get(r):
                temp397 = self.OPS
                if (op in temp397):
                    temp398 = self.OBJS
                    if (obj in temp398):
                        temp400 = (op, obj)
                        temp399 = self.MapS2P_14_1__EXPR__
                        temp401 = temp399.get(session)
                        if (temp400 not in temp401):
                            temp402 = self.MapS2P_14_1__EXPR__
                            temp403 = (op, obj)
                            temp402.add(session, temp403)
            temp404 = self.SRMapR2S_14_1__EXPR__
            temp404.add(r, session)
            temp405 = self.SUMapS2U_12_1__EXPR__
            for u in temp405.get(session):
                temp406 = self.SESSIONS
                if (session in temp406):
                    temp407 = self.USERS
                    if (u in temp407):
                        temp409 = (session, u)
                        temp408 = self.MapR2SU_12_1__EXPR__
                        temp410 = temp408.get(r)
                        if (temp409 not in temp410):
                            temp411 = self.MapR2SU_12_1__EXPR__
                            temp412 = (session, u)
                            temp411.add(r, temp412)
            temp413 = self.SUMapS2U_11_1__EXPR__
            for u in temp413.get(session):
                temp414 = self.MapUR2S_11_1__EXPR__
                temp415 = (u, r)
                temp416 = temp414.get(temp415)
                if (session not in temp416):
                    temp417 = self.MapUR2S_11_1__EXPR__
                    temp418 = (u, r)
                    temp417.add(temp418, session)
            temp419 = self.SRMapS2R
            temp419.add(session, r)
            temp420 = self.MapS2R_6_1__EXPR__
            temp421 = temp420.get(session)
            if (r not in temp421):
                temp422 = self.MapS2R_6_1__EXPR__
                temp422.add(session, r)
            temp423 = self.SRMapR2S_6_1__EXPR__
            temp423.add(r, session)
            temp424 = self.ROLES
            if (r in temp424):
                temp425 = self.PRMapR2P
                for (op, obj) in temp425.get(r):
                    temp426 = self.MapSP2R
                    temp427 = (session, op, obj)
                    temp428 = temp426.get(temp427)
                    if (r not in temp428):
                        temp429 = self.MapSP2R
                        temp430 = (session, op, obj)
                        temp429.add(temp430, r)
            temp431 = self.SRMapR2S
            temp431.add(r, session)
        temp432 = self.SESSIONS
        temp432.add(session)
        temp433 = self.SUMapS2U_12_1__EXPR__
        for u in temp433.get(session):
            temp434 = self.USERS
            if (u in temp434):
                temp435 = self.SRMapS2R
                for r in temp435.get(session):
                    temp437 = (session, u)
                    temp436 = self.MapR2SU_12_1__EXPR__
                    temp438 = temp436.get(r)
                    if (temp437 not in temp438):
                        temp439 = self.MapR2SU_12_1__EXPR__
                        temp440 = (session, u)
                        temp439.add(r, temp440)
        temp441 = self.SUMapS2U_11_1__EXPR__
        for u in temp441.get(session):
            temp442 = self.SRMapS2R
            for r in temp442.get(session):
                temp443 = self.MapUR2S_11_1__EXPR__
                temp444 = (u, r)
                temp445 = temp443.get(temp444)
                if (session not in temp445):
                    temp446 = self.MapUR2S_11_1__EXPR__
                    temp447 = (u, r)
                    temp446.add(temp447, session)
        temp448 = self.SUMapS2U_10_1__EXPR__
        for u in temp448.get(session):
            temp449 = self.MapU2S_10_1__EXPR__
            temp450 = temp449.get(u)
            if (session not in temp450):
                temp451 = self.MapU2S_10_1__EXPR__
                temp451.add(u, session)

    def DeleteSession(self, user, session):
        temp452 = self.USERS
        assert (user in temp452)
        temp453 = self.SESSIONS
        assert (session in temp453)
        temp454 = (session, user)
        temp455 = self.SU
        assert (temp454 in temp455)
        temp456 = self.SESSIONS
        if (session in temp456):
            temp457 = self.MapU2S_10_1__EXPR__
            temp458 = temp457.get(user)
            if (session in temp458):
                temp459 = self.MapU2S_10_1__EXPR__
                temp459.remove(user, session)
        temp460 = self.SUMapS2U_10_1__EXPR__
        temp460.remove(session, user)
        temp461 = self.SRMapS2R
        for r in temp461.get(session):
            temp462 = self.MapUR2S_11_1__EXPR__
            temp463 = (user, r)
            temp464 = temp462.get(temp463)
            if (session in temp464):
                temp465 = self.MapUR2S_11_1__EXPR__
                temp466 = (user, r)
                temp465.remove(temp466, session)
        temp467 = self.SUMapS2U_11_1__EXPR__
        temp467.remove(session, user)
        temp468 = self.SESSIONS
        if (session in temp468):
            temp469 = self.USERS
            if (user in temp469):
                temp470 = self.SRMapS2R
                for r in temp470.get(session):
                    temp472 = (session, user)
                    temp471 = self.MapR2SU_12_1__EXPR__
                    temp473 = temp471.get(r)
                    if (temp472 in temp473):
                        temp474 = self.MapR2SU_12_1__EXPR__
                        temp475 = (session, user)
                        temp474.remove(r, temp475)
        temp476 = self.SUMapS2U_12_1__EXPR__
        temp476.remove(session, user)
        temp477 = self.SUMapU2S_12_1__EXPR__
        temp477.remove(user, session)
        temp478 = self.SU
        temp479 = (session, user)
        temp478.remove(temp479)
        temp480 = self.SRMapS2R
        temp481 = temp480.get(session)
        for r in temp481.copy():
            temp482 = self.ROLES
            if (r in temp482):
                temp483 = self.PRMapR2P
                for (op, obj) in temp483.get(r):
                    temp484 = self.MapSP2R
                    temp485 = (session, op, obj)
                    temp486 = temp484.get(temp485)
                    if (r in temp486):
                        temp487 = self.MapSP2R
                        temp488 = (session, op, obj)
                        temp487.remove(temp488, r)
            temp489 = self.SRMapR2S
            temp489.remove(r, session)
            temp490 = self.MapS2R_6_1__EXPR__
            temp491 = temp490.get(session)
            if (r in temp491):
                temp492 = self.MapS2R_6_1__EXPR__
                temp492.remove(session, r)
            temp493 = self.SRMapR2S_6_1__EXPR__
            temp493.remove(r, session)
            temp494 = self.SUMapS2U_11_1__EXPR__
            for u in temp494.get(session):
                temp495 = self.MapUR2S_11_1__EXPR__
                temp496 = (u, r)
                temp497 = temp495.get(temp496)
                if (session in temp497):
                    temp498 = self.MapUR2S_11_1__EXPR__
                    temp499 = (u, r)
                    temp498.remove(temp499, session)
            temp500 = self.SRMapS2R
            temp500.remove(session, r)
            temp501 = self.SUMapS2U_12_1__EXPR__
            for u in temp501.get(session):
                temp502 = self.SESSIONS
                if (session in temp502):
                    temp503 = self.USERS
                    if (u in temp503):
                        temp505 = (session, u)
                        temp504 = self.MapR2SU_12_1__EXPR__
                        temp506 = temp504.get(r)
                        if (temp505 in temp506):
                            temp507 = self.MapR2SU_12_1__EXPR__
                            temp508 = (session, u)
                            temp507.remove(r, temp508)
            temp509 = self.PRMapR2P_14_1__EXPR__
            for (op, obj) in temp509.get(r):
                temp510 = self.OPS
                if (op in temp510):
                    temp511 = self.OBJS
                    if (obj in temp511):
                        temp513 = (op, obj)
                        temp512 = self.MapS2P_14_1__EXPR__
                        temp514 = temp512.get(session)
                        if (temp513 in temp514):
                            temp515 = self.MapS2P_14_1__EXPR__
                            temp516 = (op, obj)
                            temp515.remove(session, temp516)
            temp517 = self.SRMapR2S_14_1__EXPR__
            temp517.remove(r, session)
            temp518 = self.SR
            temp519 = (session, r)
            temp518.remove(temp519)
        temp520 = self.SUMapS2U_10_1__EXPR__
        for u in temp520.get(session):
            temp521 = self.MapU2S_10_1__EXPR__
            temp522 = temp521.get(u)
            if (session in temp522):
                temp523 = self.MapU2S_10_1__EXPR__
                temp523.remove(u, session)
        temp524 = self.SUMapS2U_11_1__EXPR__
        for u in temp524.get(session):
            temp525 = self.SRMapS2R
            for r in temp525.get(session):
                temp526 = self.MapUR2S_11_1__EXPR__
                temp527 = (u, r)
                temp528 = temp526.get(temp527)
                if (session in temp528):
                    temp529 = self.MapUR2S_11_1__EXPR__
                    temp530 = (u, r)
                    temp529.remove(temp530, session)
        temp531 = self.SUMapS2U_12_1__EXPR__
        for u in temp531.get(session):
            temp532 = self.USERS
            if (u in temp532):
                temp533 = self.SRMapS2R
                for r in temp533.get(session):
                    temp535 = (session, u)
                    temp534 = self.MapR2SU_12_1__EXPR__
                    temp536 = temp534.get(r)
                    if (temp535 in temp536):
                        temp537 = self.MapR2SU_12_1__EXPR__
                        temp538 = (session, u)
                        temp537.remove(r, temp538)
        temp539 = self.SESSIONS
        temp539.remove(session)

    def AddActiveRole(self, user, session, role):
        temp540 = self.USERS
        assert (user in temp540)
        temp541 = self.SESSIONS
        assert (session in temp541)
        temp542 = self.ROLES
        assert (role in temp542)
        temp543 = (session, user)
        temp544 = self.SU
        assert (temp543 in temp544)
        temp545 = (session, role)
        temp546 = self.SR
        assert (temp545 not in temp546)
        temp547 = self.AssignedRoles(user)
        assert (role in temp547)
        temp548 = self.SR
        temp549 = (session, role)
        temp548.add(temp549)
        temp550 = self.PRMapR2P_14_1__EXPR__
        for (op, obj) in temp550.get(role):
            temp551 = self.OPS
            if (op in temp551):
                temp552 = self.OBJS
                if (obj in temp552):
                    temp554 = (op, obj)
                    temp553 = self.MapS2P_14_1__EXPR__
                    temp555 = temp553.get(session)
                    if (temp554 not in temp555):
                        temp556 = self.MapS2P_14_1__EXPR__
                        temp557 = (op, obj)
                        temp556.add(session, temp557)
        temp558 = self.SRMapR2S_14_1__EXPR__
        temp558.add(role, session)
        temp559 = self.SUMapS2U_12_1__EXPR__
        for u in temp559.get(session):
            temp560 = self.SESSIONS
            if (session in temp560):
                temp561 = self.USERS
                if (u in temp561):
                    temp563 = (session, u)
                    temp562 = self.MapR2SU_12_1__EXPR__
                    temp564 = temp562.get(role)
                    if (temp563 not in temp564):
                        temp565 = self.MapR2SU_12_1__EXPR__
                        temp566 = (session, u)
                        temp565.add(role, temp566)
        temp567 = self.SUMapS2U_11_1__EXPR__
        for u in temp567.get(session):
            temp568 = self.MapUR2S_11_1__EXPR__
            temp569 = (u, role)
            temp570 = temp568.get(temp569)
            if (session not in temp570):
                temp571 = self.MapUR2S_11_1__EXPR__
                temp572 = (u, role)
                temp571.add(temp572, session)
        temp573 = self.SRMapS2R
        temp573.add(session, role)
        temp574 = self.MapS2R_6_1__EXPR__
        temp575 = temp574.get(session)
        if (role not in temp575):
            temp576 = self.MapS2R_6_1__EXPR__
            temp576.add(session, role)
        temp577 = self.SRMapR2S_6_1__EXPR__
        temp577.add(role, session)
        temp578 = self.ROLES
        if (role in temp578):
            temp579 = self.PRMapR2P
            for (op, obj) in temp579.get(role):
                temp580 = self.MapSP2R
                temp581 = (session, op, obj)
                temp582 = temp580.get(temp581)
                if (role not in temp582):
                    temp583 = self.MapSP2R
                    temp584 = (session, op, obj)
                    temp583.add(temp584, role)
        temp585 = self.SRMapR2S
        temp585.add(role, session)

    def DropActiveRole(self, user, session, role):
        temp586 = self.USERS
        assert (user in temp586)
        temp587 = self.SESSIONS
        assert (session in temp587)
        temp588 = self.ROLES
        assert (role in temp588)
        temp589 = (session, user)
        temp590 = self.SU
        assert (temp589 in temp590)
        temp591 = (session, role)
        temp592 = self.SR
        assert (temp591 in temp592)
        temp593 = self.ROLES
        if (role in temp593):
            temp594 = self.PRMapR2P
            for (op, obj) in temp594.get(role):
                temp595 = self.MapSP2R
                temp596 = (session, op, obj)
                temp597 = temp595.get(temp596)
                if (role in temp597):
                    temp598 = self.MapSP2R
                    temp599 = (session, op, obj)
                    temp598.remove(temp599, role)
        temp600 = self.SRMapR2S
        temp600.remove(role, session)
        temp601 = self.MapS2R_6_1__EXPR__
        temp602 = temp601.get(session)
        if (role in temp602):
            temp603 = self.MapS2R_6_1__EXPR__
            temp603.remove(session, role)
        temp604 = self.SRMapR2S_6_1__EXPR__
        temp604.remove(role, session)
        temp605 = self.SUMapS2U_11_1__EXPR__
        for u in temp605.get(session):
            temp606 = self.MapUR2S_11_1__EXPR__
            temp607 = (u, role)
            temp608 = temp606.get(temp607)
            if (session in temp608):
                temp609 = self.MapUR2S_11_1__EXPR__
                temp610 = (u, role)
                temp609.remove(temp610, session)
        temp611 = self.SRMapS2R
        temp611.remove(session, role)
        temp612 = self.SUMapS2U_12_1__EXPR__
        for u in temp612.get(session):
            temp613 = self.SESSIONS
            if (session in temp613):
                temp614 = self.USERS
                if (u in temp614):
                    temp616 = (session, u)
                    temp615 = self.MapR2SU_12_1__EXPR__
                    temp617 = temp615.get(role)
                    if (temp616 in temp617):
                        temp618 = self.MapR2SU_12_1__EXPR__
                        temp619 = (session, u)
                        temp618.remove(role, temp619)
        temp620 = self.PRMapR2P_14_1__EXPR__
        for (op, obj) in temp620.get(role):
            temp621 = self.OPS
            if (op in temp621):
                temp622 = self.OBJS
                if (obj in temp622):
                    temp624 = (op, obj)
                    temp623 = self.MapS2P_14_1__EXPR__
                    temp625 = temp623.get(session)
                    if (temp624 in temp625):
                        temp626 = self.MapS2P_14_1__EXPR__
                        temp627 = (op, obj)
                        temp626.remove(session, temp627)
        temp628 = self.SRMapR2S_14_1__EXPR__
        temp628.remove(role, session)
        temp629 = self.SR
        temp630 = (session, role)
        temp629.remove(temp630)

    def CheckAccess(self, session, operation, object):
        temp631 = self.SESSIONS
        assert (session in temp631)
        temp632 = self.OPS
        assert (operation in temp632)
        temp633 = self.OBJS
        assert (object in temp633)
        temp634 = self.MapSP2R
        temp635 = (session, operation, object)
        temp636 = temp634.get(temp635)
        temp637 = len(temp636)
        return (temp637 != 0)

    def AssignedUsers(self, role):
        temp638 = self.ROLES
        assert (role in temp638)
        temp639 = self.MapR2U_7_1__EXPR__
        return temp639.get(role)

    def AssignedRoles(self, user):
        temp640 = self.USERS
        assert (user in temp640)
        temp641 = self.MapU2R_5_1__EXPR__
        return temp641.get(user)

    def RolePermissions(self, role):
        temp642 = self.ROLES
        assert (role in temp642)
        temp643 = self.MapR2P_8_1__EXPR__
        return temp643.get(role)

    def UserPermissions(self, user):
        temp644 = self.USERS
        assert (user in temp644)
        temp645 = self.MapU2P_13_1__EXPR__
        return temp645.get(user)

    def SessionRoles(self, session):
        temp646 = self.SESSIONS
        assert (session in temp646)
        temp647 = self.MapS2R_6_1__EXPR__
        return temp647.get(session)

    def SessionPermissions(self, session):
        temp648 = self.SESSIONS
        assert (session in temp648)
        temp649 = self.MapS2P_14_1__EXPR__
        return temp649.get(session)

    def RoleOperationsOnObject(self, role, obj):
        temp650 = self.ROLES
        assert (role in temp650)
        temp651 = self.OBJS
        assert (obj in temp651)
        temp652 = self.MapRO2A_9_1__EXPR__
        temp653 = (role, object)
        return temp652.get(temp653)

    def UserOperationsOnObject(self, user, obj):
        temp654 = self.USERS
        assert (user in temp654)
        temp655 = self.OBJS
        assert (obj in temp655)
        temp656 = self.MapRO2A_9_1__EXPR__
        temp657 = (role, object)
        return temp656.get(temp657)

    def AddOperation(self, operation):
        temp658 = self.OPS
        temp658.add(operation)

    def AddObject(self, OBJ):
        temp659 = self.OBJS
        temp659.add(OBJ, b, c)

    def AddObject(self, OBJ):
        temp1 = self.OBJS
        temp1.add(OBJ, b, c)

    def AddPermission(self, operation, obj):
        pass
C = coreRBAC()
C.AddUser('mickg')
C.AddUser('zog')
C.AddRole('Backup Operator')
C.AddRole('Restore Operator')
C.AddRole('Grr')
C.AddObject(3)
C.AddObject(2)
C.AddOperation('add')
C.AddOperation('sub')
C.GrantPermission('add', 2, 'Restore Operator')
C.GrantPermission('add', 3, 'Backup Operator')
C.GrantPermission('add', 3, 'Restore Operator')
C.GrantPermission('sub', 2, 'Backup Operator')
C.AssignUser('mickg', 'Backup Operator')
C.AssignUser('mickg', 'Restore Operator')
C.AssignUser('zog', 'Restore Operator')
temp660 = ['Backup Operator']
temp661 = sets.Set(temp660)
C.CreateSession('mickg', 'Adder Session', temp661)
temp662 = ['Restore Operator']
temp663 = sets.Set(temp662)
C.CreateSession('zog', 'Restorer Session', temp663)
C.DeleteRole('Grr')
C.CheckAccess('Adder Session', 'add', 3)
C.CheckAccess('Restorer Session', 'sub', 3)
