'Debugger basics'
import sys
import os
import types
__all__ = ['BdbQuit', 'Bdb', 'Breakpoint']


class BdbQuit(Exception):
    'Exception to give up completely'


class Bdb:
    'Generic Python debugger base class.\n\n    This class takes care of details of the trace facility;\n    a derived class should implement user interaction.\n    The standard debugger class (pdb.Pdb) is an example.\n    '

    def __init__(self):
        self.breaks = {1: 2}
        self.fncache = {}

    def canonic(self, filename):
        temp1 = filename[1:-1]
        temp0 = '<' + temp1
        temp2 = temp0 + '>'
        temp3 = (filename == temp2)
        if temp3:
            return filename
        temp5 = temp4.get
        canonic = temp5(filename)
        temp10 = (not canonic)
        if temp10:
            temp7 = temp6.abspath
            canonic = temp7(filename)
            temp9 = temp8.normcase
            canonic = temp9(canonic)
            self.fncache[filename] = canonic
        return canonic

    def reset(self):
        import linecache
        temp11 = linecache.checkcache
        temp11()
        self.botframe = None
        self.stopframe = None
        self.returnframe = None
        self.quitting = 0

    def trace_dispatch(self, frame, event, arg):
        temp12 = self.quitting
        if temp12:
            return 
        temp15 = (event == 'line')
        if temp15:
            temp13 = self.dispatch_line
            temp14 = temp13(frame)
            return temp14
        temp18 = (event == 'call')
        if temp18:
            temp16 = self.dispatch_call
            temp17 = temp16(frame, arg)
            return temp17
        temp21 = (event == 'return')
        if temp21:
            temp19 = self.dispatch_return
            temp20 = temp19(frame, arg)
            return temp20
        temp24 = (event == 'exception')
        if temp24:
            temp22 = self.dispatch_exception
            temp23 = temp22(frame, arg)
            return temp23
        temp26 = (event == 'c_call')
        if temp26:
            temp25 = self.trace_dispatch
            return temp25
        temp28 = (event == 'c_exception')
        if temp28:
            temp27 = self.trace_dispatch
            return temp27
        temp30 = (event == 'c_return')
        if temp30:
            temp29 = self.trace_dispatch
            return temp29
        print 'bdb.Bdb.dispatch: unknown debugging event:'
        temp31 = repr(event)
        print temp31
        temp32 = self.trace_dispatch
        return temp32

    def dispatch_line(self, frame):
        temp33 = self.stop_here
        temp34 = temp33(frame)
        temp35 = self.break_here
        temp36 = temp35(frame)
        temp39 = (temp34 or temp36)
        if temp39:
            temp37 = self.user_line
            temp37(frame)
            temp38 = self.quitting
            if temp38:
                raise BdbQuit
        temp40 = self.trace_dispatch
        return temp40

    def dispatch_call(self, frame, arg):
        temp41 = self.botframe
        temp43 = (temp41 is None)
        if temp43:
            self.botframe = frame.f_back
            temp42 = self.trace_dispatch
            return temp42
        temp44 = self.stop_here
        temp45 = temp44(frame)
        temp46 = self.break_anywhere
        temp47 = temp46(frame)
        temp48 = (temp45 or temp47)
        temp49 = (not temp48)
        if temp49:
            return 
        temp50 = self.user_call
        temp50(frame, arg)
        temp51 = self.quitting
        if temp51:
            raise BdbQuit
        temp52 = self.trace_dispatch
        return temp52

    def dispatch_return(self, frame, arg):
        temp53 = self.stop_here
        temp54 = temp53(frame)
        temp55 = self.returnframe
        temp56 = (frame == temp55)
        temp59 = (temp54 or temp56)
        if temp59:
            temp57 = self.user_return
            temp57(frame, arg)
            temp58 = self.quitting
            if temp58:
                raise BdbQuit
        temp60 = self.trace_dispatch
        return temp60

    def dispatch_exception(self, frame, arg):
        temp61 = self.stop_here
        temp64 = temp61(frame)
        if temp64:
            temp62 = self.user_exception
            temp62(frame, arg)
            temp63 = self.quitting
            if temp63:
                raise BdbQuit
        temp65 = self.trace_dispatch
        return temp65

    def stop_here(self, frame):
        temp66 = self.stopframe
        temp67 = (frame is temp66)
        if temp67:
            return True
        temp68 = (frame is not None)
        temp69 = self.stopframe
        temp70 = (frame is not temp69)
        while (temp68 and temp70):
            temp71 = self.botframe
            temp72 = (frame is temp71)
            if temp72:
                return True
            frame = frame.f_back
            temp68 = (frame is not None)
            temp69 = self.stopframe
            temp70 = (frame is not temp69)
        return False

    def break_here(self, frame):
        temp73 = self.canonic
        temp74 = frame.f_code
        temp75 = temp74.co_filename
        filename = temp73(temp75)
        temp76 = self.breaks
        temp77 = (filename in temp76)
        temp78 = (not temp77)
        if temp78:
            return False
        lineno = frame.f_lineno
        temp79 = self.breaks
        temp80 = temp79[filename]
        temp81 = (lineno in temp80)
        temp87 = (not temp81)
        if temp87:
            temp82 = frame.f_code
            lineno = temp82.co_firstlineno
            temp83 = self.breaks
            temp84 = temp83[filename]
            temp85 = (lineno in temp84)
            temp86 = (not temp85)
            if temp86:
                return False
        (bp, flag) = effective(filename, lineno, frame)
        if bp:
            self.currentbp = bp.number
            temp88 = bp.temporary
            temp92 = (flag and temp88)
            if temp92:
                temp89 = self.do_clear
                temp90 = bp.number
                temp91 = str(temp90)
                temp89(temp91)
            return True
        else:
            return False

    def do_clear(self, arg):
        raise NotImplementedError, 'subclass of bdb must implement do_clear()'

    def break_anywhere(self, frame):
        temp94 = temp93.has_key
        temp95 = self.canonic
        temp96 = frame.f_code
        temp97 = temp96.co_filename
        temp98 = temp95(temp97)
        temp99 = temp94(temp98)
        return temp99

    def user_call(self, frame, argument_list):
        'This method is called when there is the remote possibility\n        that we ever need to stop in this function.'
        pass

    def user_line(self, frame):
        'This method is called when we stop or break at this line.'
        pass

    def user_return(self, frame, return_value):
        'This method is called when a return trap is set here.'
        pass

    def user_exception(self, frame, (exc_type, exc_value, exc_traceback)):
        'This method is called if an exception occurs,\n        but only if we are to stop at or just below this level.'
        pass

    def set_step(self):
        'Stop after one line of code.'
        self.stopframe = None
        self.returnframe = None
        self.quitting = 0

    def set_next(self, frame):
        'Stop on the next line in or below the given frame.'
        self.stopframe = frame
        self.returnframe = None
        self.quitting = 0

    def set_return(self, frame):
        'Stop when returning from the given frame.'
        self.stopframe = frame.f_back
        self.returnframe = frame
        self.quitting = 0

    def set_trace(self, frame=None):
        "Start debugging from `frame`.\n\n        If frame is not specified, debugging starts from caller's frame.\n        "
        temp102 = (frame is None)
        if temp102:
            temp100 = sys._getframe
            temp101 = temp100()
            frame = temp101.f_back
        temp103 = self.reset
        temp103()
        while frame:
            frame.f_trace = self.trace_dispatch
            self.botframe = frame
            frame = frame.f_back
        temp104 = self.set_step
        temp104()
        temp105 = sys.settrace
        temp106 = self.trace_dispatch
        temp105(temp106)

    def set_continue(self):
        self.stopframe = self.botframe
        self.returnframe = None
        self.quitting = 0
        temp107 = self.breaks
        temp113 = (not temp107)
        if temp113:
            temp108 = sys.settrace
            temp108(None)
            temp109 = sys._getframe
            temp110 = temp109()
            frame = temp110.f_back
            temp111 = self.botframe
            temp112 = (frame is not temp111)
            while (frame and temp112):
                del frame.f_trace
                frame = frame.f_back
                temp111 = self.botframe
                temp112 = (frame is not temp111)

    def set_quit(self):
        self.stopframe = self.botframe
        self.returnframe = None
        self.quitting = 1
        temp114 = sys.settrace
        temp114(None)

    def set_break(self, filename, lineno, temporary=0, cond=None, funcname=None):
        temp115 = self.canonic
        filename = temp115(filename)
        import linecache
        temp116 = linecache.getline
        line = temp116(filename, lineno)
        temp119 = (not line)
        if temp119:
            temp117 = (filename, lineno)
            temp118 = 'Line %s:%d does not exist' % temp117
            return temp118
        temp120 = self.breaks
        temp121 = (filename in temp120)
        temp122 = (not temp121)
        if temp122:
            self.breaks[filename] = []
        temp123 = self.breaks
        list = temp123[filename]
        temp124 = (lineno in list)
        temp126 = (not temp124)
        if temp126:
            temp125 = list.append
            temp125(lineno)
        bp = Breakpoint(filename, lineno, temporary, cond, funcname)

    def clear_break(self, filename, lineno):
        temp127 = self.canonic
        filename = temp127(filename)
        temp128 = self.breaks
        temp129 = (filename in temp128)
        temp131 = (not temp129)
        if temp131:
            temp130 = 'There are no breakpoints in %s' % filename
            return temp130
        temp132 = self.breaks
        temp133 = temp132[filename]
        temp136 = (lineno not in temp133)
        if temp136:
            temp134 = (filename, lineno)
            temp135 = 'There is no breakpoint at %s:%d' % temp134
            return temp135
        temp137 = Breakpoint.bplist
        temp138 = (filename, lineno)
        temp139 = temp137[temp138]
        temp141 = temp139[:]
        for bp in temp141:
            temp140 = bp.deleteMe
            temp140()
        temp143 = temp142.has_key
        temp144 = (filename, lineno)
        temp145 = temp143(temp144)
        temp149 = (not temp145)
        if temp149:
            temp148 = temp147.remove
            temp148(lineno)
        temp150 = self.breaks
        temp151 = temp150[filename]
        temp153 = (not temp151)
        if temp153:
            temp152 = self.breaks
            del temp152[filename]

    def clear_bpbynumber(self, arg):
        try:
            number = int(arg)
        except:
            temp154 = 'Non-numeric breakpoint number (%s)' % arg
            return temp154
        try:
            temp155 = Breakpoint.bpbynumber
            bp = temp155[number]
        except IndexError:
            temp156 = 'Breakpoint number (%d) out of range' % number
            return temp156
        temp158 = (not bp)
        if temp158:
            temp157 = 'Breakpoint (%d) already deleted' % number
            return temp157
        temp159 = self.clear_break
        temp160 = bp.file
        temp161 = bp.line
        temp159(temp160, temp161)

    def clear_all_file_breaks(self, filename):
        temp162 = self.canonic
        filename = temp162(filename)
        temp163 = self.breaks
        temp164 = (filename in temp163)
        temp166 = (not temp164)
        if temp166:
            temp165 = 'There are no breakpoints in %s' % filename
            return temp165
        temp167 = self.breaks
        temp171 = temp167[filename]
        for line in temp171:
            temp168 = Breakpoint.bplist
            temp169 = (filename, line)
            blist = temp168[temp169]
            for bp in blist:
                temp170 = bp.deleteMe
                temp170()
        temp172 = self.breaks
        del temp172[filename]

    def clear_all_breaks(self):
        temp173 = self.breaks
        temp174 = (not temp173)
        if temp174:
            return 'There are no breakpoints'
        for bp in Breakpoint.bpbynumber:
            if bp:
                temp175 = bp.deleteMe
                temp175()
        self.breaks = {}

    def get_break(self, filename, lineno):
        temp176 = self.canonic
        filename = temp176(filename)
        temp177 = self.breaks
        temp178 = (filename in temp177)
        temp179 = self.breaks
        temp180 = temp179[filename]
        temp181 = (lineno in temp180)
        temp182 = (temp178 and temp181)
        return temp182

    def get_breaks(self, filename, lineno):
        temp183 = self.canonic
        filename = temp183(filename)
        temp184 = self.breaks
        temp185 = (filename in temp184)
        temp186 = self.breaks
        temp187 = temp186[filename]
        temp188 = (lineno in temp187)
        temp189 = Breakpoint.bplist
        temp190 = (filename, lineno)
        temp191 = temp189[temp190]
        temp192 = (temp185 and temp188 and temp191)
        temp193 = []
        temp194 = (temp192 or temp193)
        return temp194

    def get_file_breaks(self, filename):
        temp195 = self.canonic
        filename = temp195(filename)
        temp196 = self.breaks
        temp200 = (filename in temp196)
        if temp200:
            temp197 = self.breaks
            temp198 = temp197[filename]
            return temp198
        else:
            temp199 = []
            return temp199

    def get_all_breaks(self):
        temp201 = self.breaks
        return temp201

    def get_stack(self, f, t):
        stack = []
        temp202 = t.tb_frame
        temp203 = (temp202 is f)
        temp204 = (t and temp203)
        if temp204:
            t = t.tb_next
        while (f is not None):
            temp205 = stack.append
            temp206 = (f, f.f_lineno)
            temp205(temp206)
            temp207 = self.botframe
            temp208 = (f is temp207)
            if temp208:
                break
            f = f.f_back
        temp209 = stack.reverse
        temp209()
        temp210 = len(stack)
        temp211 = temp210 - 1
        i = max(0, temp211)
        while (t is not None):
            temp212 = stack.append
            temp213 = (t.tb_frame, t.tb_lineno)
            temp212(temp213)
            t = t.tb_next
        temp214 = (stack, i)
        return temp214

    def format_stack_entry(self, frame_lineno, lprefix=': '):
        import linecache
        import repr
        (frame, lineno) = frame_lineno
        temp215 = self.canonic
        temp216 = frame.f_code
        temp217 = temp216.co_filename
        filename = temp215(temp217)
        temp218 = (filename, lineno)
        s = '%s(%r)' % temp218
        temp219 = frame.f_code
        temp222 = temp219.co_name
        if temp222:
            temp221 = frame.f_code
            temp220 = temp221.co_name
            s = s + temp220
        else:
            s = s + '<lambda>'
        temp223 = frame.f_locals
        temp225 = ('__args__' in temp223)
        if temp225:
            temp224 = frame.f_locals
            args = temp224['__args__']
        else:
            args = None
        if args:
            temp227 = repr.repr
            temp226 = temp227(args)
            s = s + temp226
        else:
            s = s + '()'
        temp228 = frame.f_locals
        temp232 = ('__return__' in temp228)
        if temp232:
            temp229 = frame.f_locals
            rv = temp229['__return__']
            s = s + '->'
            temp231 = repr.repr
            temp230 = temp231(rv)
            s = s + temp230
        temp233 = linecache.getline
        line = temp233(filename, lineno)
        if line:
            temp234 = s + lprefix
            temp236 = line.strip
            temp235 = temp236()
            s = temp234 + temp235
        return s

    def run(self, cmd, globals=None, locals=None):
        temp237 = (globals is None)
        if temp237:
            import __main__
            globals = __main__.__dict__
        temp238 = (locals is None)
        if temp238:
            locals = globals
        temp239 = self.reset
        temp239()
        temp240 = sys.settrace
        temp241 = self.trace_dispatch
        temp240(temp241)
        temp242 = types.CodeType
        temp243 = isinstance(cmd, temp242)
        temp244 = (not temp243)
        if temp244:
            cmd = cmd + '\n'
        try:
            try:cmdglobalslocals
            except BdbQuit:
                pass
        finally:
            self.quitting = 1
            temp245 = sys.settrace
            temp245(None)

    def runeval(self, expr, globals=None, locals=None):
        temp246 = (globals is None)
        if temp246:
            import __main__
            globals = __main__.__dict__
        temp247 = (locals is None)
        if temp247:
            locals = globals
        temp248 = self.reset
        temp248()
        temp249 = sys.settrace
        temp250 = self.trace_dispatch
        temp249(temp250)
        temp251 = types.CodeType
        temp252 = isinstance(expr, temp251)
        temp253 = (not temp252)
        if temp253:
            expr = expr + '\n'
        try:
            try:
                temp254 = eval(expr, globals, locals)
                return temp254
            except BdbQuit:
                pass
        finally:
            self.quitting = 1
            temp255 = sys.settrace
            temp255(None)

    def runctx(self, cmd, globals, locals):
        temp256 = self.run
        temp256(cmd, globals, locals)

    def runcall(self, func, *args, **kwds):
        temp257 = self.reset
        temp257()
        temp258 = sys.settrace
        temp259 = self.trace_dispatch
        temp258(temp259)
        res = None
        try:
            try:
                res = func(*args, **kwds)
            except BdbQuit:
                pass
        finally:
            self.quitting = 1
            temp260 = sys.settrace
            temp260(None)
        return res

def set_trace():
    temp262 = temp261.set_trace
    temp262()


class Breakpoint:
    'Breakpoint class\n\n    Implements temporary breakpoints, ignore counts, disabling and\n    (re)-enabling, and conditionals.\n\n    Breakpoints are indexed by number through bpbynumber and by\n    the file,line tuple using bplist.  The former points to a\n    single instance of class Breakpoint.  The latter points to a\n    list of such instances since there may be more than one\n    breakpoint per line.\n\n    '

    def __init__(self, file, line, temporary=0, cond=None, funcname=None):
        self.bplist = {}
        self.next = 1
        self.bpbynumber = []
        self.funcname = funcname
        self.func_first_executable_line = None
        self.file = file
        self.line = line
        self.temporary = temporary
        self.cond = cond
        self.enabled = 1
        self.ignore = 0
        self.hits = 0
        self.number = self.next
        temp263 = self.next
        self.next = temp263 + 1

    def deleteMe(self):
        index = (self.file, self.line)
        self.bpbynumber[self.number] = None
        temp266 = temp265.remove
        temp266(self)
        temp267 = self.bplist
        temp268 = temp267[index]
        temp270 = (not temp268)
        if temp270:
            temp269 = self.bplist
            del temp269[index]

    def enable(self):
        self.enabled = 1

    def disable(self):
        self.enabled = 0

    def bpprint(self):
        temp271 = self.temporary
        if temp271:
            disp = 'del  '
        else:
            disp = 'keep '
        temp272 = self.enabled
        if temp272:
            disp = disp + 'yes  '
        else:
            disp = disp + 'no   '
        temp273 = (self.number, disp, self.file, self.line)
        temp274 = '%-4dbreakpoint   %s at %s:%d' % temp273
        print temp274
        temp277 = self.cond
        if temp277:
            temp275 = (self.cond,)
            temp276 = '\tstop only if %s' % temp275
            print temp276
        temp280 = self.ignore
        if temp280:
            temp278 = self.ignore
            temp279 = '\tignore next %d hits' % temp278
            print temp279
        temp285 = self.hits
        if temp285:
            temp281 = self.hits
            temp282 = (temp281 > 1)
            if temp282:
                ss = 's'
            else:
                ss = ''
            temp283 = (self.hits, ss)
            temp284 = '\tbreakpoint already hit %d time%s' % temp283
            print temp284

def checkfuncname(b, frame):
    'Check whether we should break here because of `b.funcname`.'
    temp286 = b.funcname
    temp290 = (not temp286)
    if temp290:
        temp287 = b.line
        temp288 = frame.f_lineno
        temp289 = (temp287 != temp288)
        if temp289:
            return False
        return True
    temp291 = frame.f_code
    temp292 = temp291.co_name
    temp293 = b.funcname
    temp294 = (temp292 != temp293)
    if temp294:
        return False
    temp295 = b.func_first_executable_line
    temp296 = (not temp295)
    if temp296:
        b.func_first_executable_line = frame.f_lineno
    temp297 = b.func_first_executable_line
    temp298 = frame.f_lineno
    temp299 = (temp297 != temp298)
    if temp299:
        return False
    return True

def effective(file, line, frame):
    'Determine which breakpoint for this file:line is to be acted upon.\n\n    Called only if we know there is a bpt at this\n    location.  Returns breakpoint that was triggered and a flag\n    that indicates if it is ok to delete a temporary bp.\n\n    '
    b = Breakpoint('tmp', 1)
    temp319 = range(0, 12)
    for i in temp319:
        temp300 = b.enabled
        temp301 = (temp300 == 0)
        if temp301:
            continue
        temp302 = checkfuncname(b, frame)
        temp303 = (not temp302)
        if temp303:
            continue
        temp304 = b.hits
        b.hits = temp304 + 1
        temp305 = b.cond
        temp318 = (not temp305)
        if temp318:
            temp306 = b.ignore
            temp309 = (temp306 > 0)
            if temp309:
                temp307 = b.ignore
                b.ignore = temp307 - 1
                continue
            else:
                temp308 = (b, 1)
                return temp308
        else:
            try:
                temp310 = b.cond
                temp311 = frame.f_globals
                temp312 = frame.f_locals
                val = eval(temp310, temp311, temp312)
                if val:
                    temp313 = b.ignore
                    temp316 = (temp313 > 0)
                    if temp316:
                        temp314 = b.ignore
                        b.ignore = temp314 - 1
                    else:
                        temp315 = (b, 1)
                        return temp315
            except:
                temp317 = (b, 0)
                return temp317
    temp320 = (None, None)
    return temp320


class Tdb(Bdb):

    def user_call(self, frame, args):
        temp321 = frame.f_code
        name = temp321.co_name
        temp322 = (not name)
        if temp322:
            name = '???'
        print '+++ call'
        print name
        print args

    def user_line(self, frame):
        import linecache
        temp323 = frame.f_code
        name = temp323.co_name
        temp324 = (not name)
        if temp324:
            name = '???'
        temp325 = self.canonic
        temp326 = frame.f_code
        temp327 = temp326.co_filename
        fn = temp325(temp327)
        temp328 = linecache.getline
        temp329 = frame.f_lineno
        line = temp328(fn, temp329)
        print '+++'
        print fn
        print frame.f_lineno
        print name
        print ':'
        temp330 = line.strip
        temp331 = temp330()
        print temp331

    def user_return(self, frame, retval):
        print '+++ return'
        print retval

    def user_exception(self, frame, exc_stuff):
        print '+++ exception'
        print exc_stuff
        temp332 = self.set_continue
        temp332()

def foo(n):
    print 'foo('
    print n
    print ')'
    temp333 = n * 10
    x = bar(temp333)
    print 'bar returned'
    print x

def bar(a):
    print 'bar('
    print a
    print ')'
    temp334 = a / 2
    return temp334

def test():
    t = Tdb()
    temp335 = t.run
    temp335('import bdb; bdb.foo(10)')
t = Bdb()
temp336 = t.reset
temp336()
temp337 = t.canonic
temp337('das')
temp338 = t.reset
temp338()
temp339 = t.run
temp339('1')
temp340 = t.dispatch_line
temp341 = sys._getframe
temp342 = temp341()
temp340(temp342)
temp343 = t.break_here
temp344 = sys._getframe
temp345 = temp344()
temp343(temp345)
test()