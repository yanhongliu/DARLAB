#!/usr/bin/env python
"""
Fortran 2003 Syntax Rules.

-----
Permission to use, modify, and distribute this software is given under the
terms of the NumPy License. See http://scipy.org.

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
Author: Pearu Peterson <pearu@cens.ioc.ee>
Created: Oct 2006
-----
"""

import re
from splitline import string_replace_map
import pattern_tools as pattern

import re
import os
import sys
from cStringIO import StringIO

def yellow_text(s):
    return s
def red_text(s):
    return s
def blue_text(s):
    return s


from sourceinfo import get_source_info
from splitline import String, string_replace_map, splitquote

_spacedigits=' 0123456789'
_cf2py_re = re.compile(r'(?P<indent>\s*)!f2py(?P<rest>.*)')
def asdf(line): 
    return line and len(line)>5 and line[5]!=' ' and line[:5]==5*' '

def asdf2(line):
    return boolean

_is_fix_cont = asdf
_is_f90_cont = asdf
_f90label_re = re.compile(r'\s*(?P<label>(\w+\s*:|\d+))\s*(\b|(?=&)|\Z)')
_is_include_line = re.compile(r'\s*include\s*("[^"]+"|\'[^\']+\')\s*\z').match
_hollerith_start_search = re.compile(r'(?P<pre>\A|,\s*)(?P<num>\d+)h').search
_is_fix_comment = asdf2
_is_call_stmt = re.compile(r'call\b').match

class FortranReaderError: # TODO: may be derive it from Exception
    def __init__(self, message):
        self.message = message

class Line:
    """ Holds a Fortran source line.
    """

    
    def __init__(self, line, linenospan, label, reader):
        self.f2py_strmap_findall = re.compile(r'(_F2PY_STRING_CONSTANT_\d+_|F2PY_EXPR_TUPLE_\d+)').findall
        self.line = line.strip()
        self.span = linenospan
        self.label = label
        self.reader = reader
        self.strline = None
        self.is_f2py_directive = linenospan[0] in reader.f2py_comment_lines

    def has_map(self):
        return not not (hasattr(self,'strlinemap') and self.strlinemap)

    def apply_map(self, line):
        if not hasattr(self,'strlinemap') or not self.strlinemap:
            return line
        findall = self.f2py_strmap_findall
        str_map = self.strlinemap
        keys = findall(line)
        for k in keys:
            line = line.replace(k, str_map[k])
        return line

    def copy(self, line = None, apply_map = False):
        if line is None:
            line = self.line
        if apply_map:
            line = self.apply_map(line)
        return Line(line, self.span, self.label, self.reader)

    def clone(self, line):
        self.line = self.apply_map(line)
        self.strline = None
        return

    def __repr__(self):
        return self.__class__.__name__+'(%r,%s,%r)' \
               % (self.line, self.span, self.label)

    def isempty(self, ignore_comments=False):
        return not (self.line.strip() or self.label)

    def get_line(self):
        if self.strline is not None:
            return self.strline
        line = self.line
        if self.reader.isfix77:
            # Handle Hollerith constants by replacing them
            # with char-literal-constants.
            # H constants may appear only in DATA statements and
            # in the argument list of CALL statement.
            # Holleriht constants were removed from the Fortran 77 standard.
            # The following handling is not perfect but works for simple
            # usage cases.
            # todo: Handle hollerith constants in DATA statement
            if _is_call_stmt(line):
                l2 = self.line[4:].lstrip()
                i = l2.find('(')
                if i != -1 and l2[-1]==')':
                    substrings = ['call '+l2[:i+1]]
                    start_search = _hollerith_start_search
                    l2 = l2[i+1:-1].strip()
                    m = start_search(l2)
                    while m:
                        substrings.append(l2[:m.start()])
                        substrings.append(m.group('pre'))
                        num = int(m.group('num'))
                        substrings.append("'"+l2[m.end():m.end()+num]+"'")
                        l2 = l2[m.end()+num:]
                        m = start_search(l2)
                    substrings.append(l2)
                    substrings.append(')')
                    line = ''.join(substrings)

        line, str_map = string_replace_map(line, lower=not self.reader.ispyf)
        self.strline = line
        self.strlinemap = str_map
        return line

class SyntaxErrorLine(Line, FortranReaderError):
    def __init__(self, line, linenospan, label, reader, message):
        Line.__init__(self, line, linenospan, label, reader)
        FortranReaderError.__init__(self, message)

class Comment:
    """ Holds Fortran comment.
    """
    def __init__(self, comment, linenospan, reader):
        self.comment = comment
        self.span = linenospan
        self.reader = reader
    def __repr__(self):
        return self.__class__.__name__+'(%r,%s)' \
               % (self.comment, self.span)
    def isempty(self, ignore_comments=False):
        return ignore_comments or len(self.comment)<2

class MultiLine:
    """ Holds (prefix, line list, suffix) representing multiline
    syntax in .pyf files:
      prefix+'''+lines+'''+suffix.
    """
    def __init__(self, prefix, block, suffix, linenospan, reader):
        self.prefix = prefix
        self.block  = block
        self.suffix = suffix
        self.span = linenospan
        self.reader = reader
    def __repr__(self):
        return self.__class__.__name__+'(%r,%r,%r,%s)' \
               % (self.prefix,self.block,self.suffix,
                  self.span)
    def isempty(self, ignore_comments=False):
        return not (self.prefix or self.block or self.suffix)

class SyntaxErrorMultiLine(MultiLine, FortranReaderError):
    def __init__(self, prefix, block, suffix, linenospan, reader, message):
        MultiLine.__init__(self, prefix, block, suffix, linenospan, reader)
        FortranReaderError.__init__(self, message)


class FortranReaderBase:

    def __init__(self, source, isfree, isstrict):
        """
        source - file-like object with .next() method
                 used to retrive a line.
        source may contain
          - Fortran 77 code
          - fixed format Fortran 90 code
          - free format Fortran 90 code
          - .pyf signatures - extended free format Fortran 90 syntax
        """

        self.linecount = 0
        self.source = source
        self.isclosed = False

        self.filo_line = []
        self.fifo_item = []
        self.source_lines = []

        self.f2py_comment_lines = [] # line numbers that contain f2py directives

        self.reader = None
        self.include_dirs = ['.']

        self.set_mode(isfree, isstrict)
        return

    def set_mode(self, isfree, isstrict):
        self.isfree90 = isfree and not isstrict
        self.isfix90 = not isfree and not isstrict
        self.isfix77 = not isfree and isstrict
        self.ispyf   = isfree and isstrict
        self.isfree  = isfree
        self.isfix   = not isfree
        self.isstrict = isstrict

        if self.isfree90: mode = 'free90'
        elif self.isfix90: mode = 'fix90'
        elif self.isfix77: mode = 'fix77'
        else: mode = 'pyf'
        self.mode = mode
        self.name = '%s mode=%s' % (self.source, mode)
        return

    def close_source(self):
        # called when self.source.next() raises StopIteration.
        pass

    # For handling raw source lines:

    def put_single_line(self, line):
        self.filo_line.append(line)
        self.linecount -= 1
        return

    def get_single_line(self):
        try:
            line = self.filo_line.pop()
            self.linecount += 1
            return line
        except IndexError:
            pass
        if self.isclosed:
            return None
        try:
            line = self.source.next()
        except StopIteration:
            self.isclosed = True
            self.close_source()
            return None
        self.linecount += 1
        # expand tabs, replace special symbols, get rid of nl characters
        line = line.expandtabs().replace('\xa0',' ').rstrip()
        self.source_lines.append(line)
        if not line:
            return self.get_single_line()
        return line

    def get_next_line(self):
        line = self.get_single_line()
        if line is None: return
        self.put_single_line(line)
        return line

    # Parser methods:
    def get_item(self):
        try:
            return self.next(ignore_comments = True)
        except StopIteration:
            pass
        return

    def put_item(self, item):
        self.fifo_item.insert(0, item)
        return
    # Iterator methods:

    def __iter__(self):
        return self

    def next(self, ignore_comments = False):

        try:
            if self.reader is not None:
                try:
                    return self.reader.next()
                except StopIteration:
                    self.reader = None
            item = self._next(ignore_comments)
            if isinstance(item, Line) and _is_include_line(item.line):
                reader = item.reader
                filename = item.line.strip()[7:].lstrip()[1:-1]
                include_dirs = self.include_dirs[:]
                path = filename
                for incl_dir in include_dirs:
                    path = os.path.join(incl_dir, filename)
                    if os.path.exists(path):
                        break
                if not os.path.isfile(path):
                    dirs = os.pathsep.join(include_dirs)
                    message = reader.format_message(\
                        'WARNING',
                        'include file %r not found in %r,'\
                        ' ignoring.' % (filename, dirs),
                        item.span[0], item.span[1])
                    reader.show_message(message, sys.stdout)
                    return self.next(ignore_comments = ignore_comments)
                message = reader.format_message('INFORMATION',
                                              'found file %r' % (path),
                                              item.span[0], item.span[1])
                reader.show_message(message, sys.stdout)
                self.reader = FortranFileReader(path, include_dirs = include_dirs)
                return self.reader.next(ignore_comments = ignore_comments)
            return item
        except StopIteration:
            raise
        except:
            message = self.format_message('FATAL ERROR',
                                          'while processing line',
                                          self.linecount, self.linecount)
            self.show_message(message, sys.stdout)
            self.show_message(red_text('STOPPED READING'), sys.stdout)
            raise StopIteration

    def _next(self, ignore_comments = False):
        fifo_item_pop = self.fifo_item.pop
        while 1:
            try:
                item = fifo_item_pop(0)
            except IndexError:
                item = self.get_source_item()
                if item is None:
                    raise StopIteration
            if not item.isempty(ignore_comments):
                break
            # else ignore empty lines and comments
        if not isinstance(item, Comment):
            if not self.ispyf and isinstance(item, Line) \
                   and not item.is_f2py_directive \
                   and ';' in item.get_line():
                # ;-separator not recognized in pyf-mode
                items = []
                for line in item.get_line().split(';'):
                    line = line.strip()
                    items.append(item.copy(line, apply_map=True))
                items.reverse()
                for newitem in items:
                    self.fifo_item.insert(0, newitem)
                return fifo_item_pop(0)
            return item
        # collect subsequent comments to one comment instance
        comments = []
        start = item.span[0]
        while isinstance(item, Comment):
            comments.append(item.comment)
            end = item.span[1]
            while 1:
                try:
                    item = fifo_item_pop(0)
                except IndexError:
                    item = self.get_source_item()
                if item is None or not item.isempty(ignore_comments):
                    break
            if item is None:
                break # hold raising StopIteration for the next call.
        if item is not None:
            self.fifo_item.insert(0,item)
        return self.comment_item('\n'.join(comments), start, end)

    # Interface to returned items:

    def line_item(self, line, startlineno, endlineno, label, errmessage=None):
        if errmessage is None:
            return  Line(line, (startlineno, endlineno), label, self)
        return SyntaxErrorLine(line, (startlineno, endlineno),
                               label, self, errmessage)

    def multiline_item(self, prefix, lines, suffix,
                       startlineno, endlineno, errmessage=None):
        if errmessage is None:
            return MultiLine(prefix, lines, suffix, (startlineno, endlineno), self)
        return SyntaxErrorMultiLine(prefix, lines, suffix,
                                    (startlineno, endlineno), self, errmessage)

    def comment_item(self, comment, startlineno, endlineno):
        return Comment(comment, (startlineno, endlineno), self)

    # For handling messages:

    def show_message(self, message, stream = sys.stdout):
        stream.write(message+'\n')
        stream.flush()
        return

    def format_message(self, kind, message, startlineno, endlineno,
                       startcolno=0, endcolno=-1):
        back_index = {'warning':2,'error':3,'info':0}.get(kind.lower(),3)
        r = ['%s while processing %r (mode=%r)..' % (kind, self.id, self.mode)]
        for i in range(max(1,startlineno-back_index),startlineno):
            r.append('%5d:%s' % (i,self.source_lines[i-1]))
        for i in range(startlineno,min(endlineno+back_index,len(self.source_lines))+1):
            if i==0 and not self.source_lines:
                break
            linenostr = '%5d:' % (i)
            if i==endlineno:
                sourceline = self.source_lines[i-1]
                l0 = linenostr+sourceline[:startcolno]
                if endcolno==-1:
                    l1 = sourceline[startcolno:]
                    l2 = ''
                else:
                    l1 = sourceline[startcolno:endcolno]
                    l2 = sourceline[endcolno:]
                r.append('%s%s%s <== %s' % (l0,yellow_text(l1),l2,red_text(message)))
            else:
                r.append(linenostr+ self.source_lines[i-1])
        return '\n'.join(r)

    def format_error_message(self, message, startlineno, endlineno,
                             startcolno=0, endcolno=-1):
        return self.format_message('ERROR',message, startlineno,
                                   endlineno, startcolno, endcolno)

    def format_warning_message(self, message, startlineno, endlineno,
                               startcolno=0, endcolno=-1):
        return self.format_message('WARNING',message, startlineno,
                                   endlineno, startcolno, endcolno)

    def error(self, message, item=None):
        if item is None:
            m = self.format_error_message(message, len(self.source_lines)-2, len(self.source_lines))
        else:
            m = self.format_error_message(message, item.span[0], item.span[1])
        self.show_message(m)
        return

    def warning(self, message, item=None):
        if item is None:
            m = self.format_warning_message(message, len(self.source_lines)-2, len(self.source_lines))
        else:
            m = self.format_warning_message(message, item.span[0], item.span[1])
        self.show_message(m)
        return

    # Auxiliary methods for processing raw source lines:

    def handle_cf2py_start(self, line):
        """
        f2py directives can be used only in Fortran codes.
        They are ignored when used inside .pyf files.
        """
        if not line or self.ispyf: return line
        if self.isfix:
            if line[0] in '*cC!#':
                if line[1:5].lower() == 'f2py':
                    line = 5*' ' + line[5:]
                    self.f2py_comment_lines.append(self.linecount)
            if self.isfix77:
                return line
        m = _cf2py_re.match(line)
        if m:
            newline = m.group('indent')+5*' '+m.group('rest')
            self.f2py_comment_lines.append(self.linecount)
            assert len(newline)==len(line),`newlinel,line`
            return newline
        return line

    def handle_inline_comment(self, line, lineno, quotechar=None):
        if quotechar is None and '!' not in line and \
           '"' not in line and "'" not in line:
            return line, quotechar
        i = line.find('!')
        put_item = self.fifo_item.append
        if quotechar is None and i!=-1:
            # first try a quick method
            newline = line[:i]
            if '"' not in newline and '\'' not in newline:
                if self.isfix77 or not line[i:].startswith('!f2py'):
                    put_item(self.comment_item(line[i:], lineno, lineno))
                    return newline, quotechar
        # handle cases where comment char may be a part of a character content
        #splitter = LineSplitter(line, quotechar)
        #items = [item for item in splitter]
        #newquotechar = splitter.quotechar
        items, newquotechar = splitquote(line, quotechar)

        noncomment_items = []
        noncomment_items_append = noncomment_items.append
        n = len(items)
        commentline = None
        for k in range(n):
            item = items[k]
            if isinstance(item, String) or '!' not in item:
                noncomment_items_append(item)
                continue
            j = item.find('!')
            noncomment_items_append(item[:j])
            items[k] = item[j:]
            commentline = ''.join(items[k:])
            break
        if commentline is not None:
            if commentline.startswith('!f2py'):
                # go to next iteration:
                newline = ''.join(noncomment_items) + commentline[5:]
                self.f2py_comment_lines.append(lineno)
                return self.self.handle_inline_comment(newline, lineno, quotechar)
            put_item(self.comment_item(commentline, lineno, lineno))
        return ''.join(noncomment_items), newquotechar

    def handle_multilines(self, line, startlineno, mlstr):
        i = line.find(mlstr)
        if i != -1:
            prefix = line[:i]
            # skip fake multiline starts
            p,k = prefix,0
            while p.endswith('\\'):
                p,k = p[:-1],k+1
            if k % 2: return
        if i != -1 and '!' not in prefix:
            # Note character constans like 'abc"""123',
            # so multiline prefix should better not contain `'' or `"' not `!'.
            for quote in '"\'':
                if prefix.count(quote) % 2:
                    message = self.format_warning_message(\
                            'multiline prefix contains odd number of %r characters' \
                            % (quote), startlineno, startlineno,
                            0, len(prefix))
                    self.show_message(message, sys.stderr)

            suffix = None
            multilines = []
            line = line[i+3:]
            while line is not None:
                j = line.find(mlstr)
                if j != -1 and '!' not in line[:j]:
                    multilines.append(line[:j])
                    suffix = line[j+3:]
                    break
                multilines.append(line)
                line = self.get_single_line()
            if line is None:
                message = self.format_error_message(\
                            'multiline block never ends', startlineno,
                            startlineno, i)
                return self.multiline_item(\
                            prefix,multilines,suffix,\
                            startlineno, self.linecount, message)
            suffix,qc = self.self.handle_inline_comment(suffix, self.linecount)
            # no line continuation allowed in multiline suffix
            if qc is not None:
                message = self.format_message(\
                            'ASSERTION FAILURE(pyf)',
                        'following character continuation: %r, expected None.' % (qc),
                            startlineno, self.linecount)
                self.show_message(message, sys.stderr)
            # XXX: should we do line.replace('\\'+mlstr[0],mlstr[0])
            #      for line in multilines?
            return self.multiline_item(prefix,multilines,suffix,
                                       startlineno, self.linecount)

    # The main method of interpreting raw source lines within
    # the following contexts: f77, fixed f90, free f90, pyf.

    def get_source_item(self):
        """
        a source item is ..
        - a fortran line
        - a list of continued fortran lines
        - a multiline - lines inside triple-qoutes, only when in ispyf mode
        """
        get_single_line = self.get_single_line
        line = get_single_line()
        if line is None: return
        startlineno = self.linecount
        line = self.handle_cf2py_start(line)
        is_f2py_directive = startlineno in self.f2py_comment_lines

        label = None
        if self.ispyf:
            # handle multilines
            for mlstr in ['"""',"'''"]:
                r = self.handle_multilines(line, startlineno, mlstr)
                if r: return r

        if self.isfix:
            label = line[:5].strip().lower()
            if label.endswith(':'): label = label[:-1].strip()
            if not line.strip():
                # empty line
                return self.line_item(line[6:],startlineno,self.linecount,label)
            if _is_fix_comment(line):
                return self.comment_item(line, startlineno, startlineno)
            for i in range(5):
                if line[i] not in _spacedigits:
                    message =  'non-space/digit char %r found in column %i'\
                              ' of fixed Fortran code' % (line[i],i+1)
                    if self.isfix90:
                        message = message + ', switching to free format mode'
                        message = self.format_warning_message(\
                            message,startlineno, self.linecount)
                        self.show_message(message, sys.stderr)
                        self.set_mode(True, False)
                    else:
                        return self.line_item(line[6:], startlineno, self.linecount,
                                           label, self.format_error_message(\
                            message, startlineno, self.linecount))

        if self.isfix77 and not is_f2py_directive:
            lines = [line[6:72]]
            while _is_fix_cont(self.get_next_line()):
                # handle fix format line continuations for F77 code
                line = get_single_line()
                lines.append(line[6:72])
            return self.line_item(''.join(lines),startlineno,self.linecount,label)

        

        if self.isfix90 and not is_f2py_directive:
            # handle inline comment
            newline,qc = self.handle_inline_comment(line[6:], startlineno)
            lines = [newline]
            next_line = self.get_next_line()
            while _is_fix_cont(next_line) or _is_fix_comment(next_line):
                # handle fix format line continuations for F90 code.
                # mixing fix format and f90 line continuations is not allowed
                # nor detected, just eject warnings.
                line2 = get_single_line()
                if _is_fix_comment(line2):
                    # handle fix format comments inside line continuations
                    citem = self.comment_item(line2,self.linecount,self.linecount)
                    self.fifo_item.append(citem)
                else:
                    newline, qc = self.self.handle_inline_comment(line2[6:],
                                                             self.linecount, qc)
                    lines.append(newline)
                next_line = self.get_next_line()
            # no character continuation should follows now
            if qc is not None:
                message = self.format_message(\
                            'ASSERTION FAILURE(fix90)',
                            'following character continuation: %r, expected None.'\
                            % (qc), startlineno, self.linecount)
                self.show_message(message, sys.stderr)
            if len(lines)>1:
                for i in range(len(lines)):
                    l = lines[i]
                    if l.rstrip().endswith('&'):
                        message = self.format_warning_message(\
                        'f90 line continuation character `&\' detected'\
                        ' in fix format code',
                        startlineno + i, startlineno + i, l.rfind('&')+5)
                        self.show_message(message, sys.stderr)
                return self.line_item(''.join(lines),startlineno,
                                      self.linecount,label)
        start_index = 0
        if self.isfix90:
            start_index = 6

        lines = []
        lines_append = lines.append
        put_item = self.fifo_item.append
        qc = None
        while line is not None:
            if start_index: # fix format code
                line,qc = self.handle_inline_comment(line[start_index:],
                                                self.linecount,qc)
                is_f2py_directive = self.linecount in self.f2py_comment_lines
            else:
                line_lstrip = line.lstrip()
                if lines:
                    if line_lstrip.startswith('!'):
                        # check for comment line within line continuation
                        put_item(self.comment_item(line_lstrip,
                                                   self.linecount, self.linecount))
                        line = get_single_line()
                        continue
                else:
                    # first line, check for a f90 label
                    m = _f90label_re.match(line)
                    if m:
                        assert not label,`label,m.group('label')`
                        label = m.group('label').strip()
                        if label.endswith(':'): label = label[:-1].strip()
                        if not self.ispyf: label = label.lower()
                        line = line[m.end():]
                line,qc = self.handle_inline_comment(line, self.linecount, qc)
                is_f2py_directive = self.linecount in self.f2py_comment_lines

            i = line.rfind('&')
            if i!=-1:
                line_i1_rstrip = line[i+1:].rstrip()
            if not lines:
                # first line
                if i == -1 or line_i1_rstrip:
                    lines_append(line)
                    break
                lines_append(line[:i])
                line = get_single_line()
                continue
            if i == -1 or line_i1_rstrip:
                # no line continuation follows
                i = len(line)
            k = -1
            if i != -1:
                # handle the beggining of continued line
                k = line[:i].find('&')
                if k != 1 and line[:k].lstrip():
                    k = -1
            lines_append(line[k+1:i])
            if i==len(line):
                break
            line = get_single_line()

        if qc is not None:
            message = self.format_message('ASSERTION FAILURE(free)',
                'following character continuation: %r, expected None.' % (qc),
                startlineno, self.linecount)
            self.show_message(message, sys.stderr)
        return self.line_item(''.join(lines),startlineno,self.linecount,label)

    ##  FortranReaderBase

# Fortran file and string readers:

class FortranFileReader(FortranReaderBase):

    def __init__(self, filename,
                 include_dirs = None):
        isfree, isstrict = get_source_info(filename)
        self.id = filename
        self.file = open(filename,'r')
        FortranReaderBase.__init__(self, self.file, isfree, isstrict)
        if include_dirs is None:
            self.include_dirs.insert(0, os.path.dirname(filename))
        else:
            self.include_dirs = include_dirs[:]
        return

    def close_source(self):
        self.file.close()

class FortranStringReader(FortranReaderBase):

    def __init__(self, string, isfree, isstrict, include_dirs = None):
        self.id = 'string-'+str(id(string))
        source = StringIO(string)
        FortranReaderBase.__init__(self, source, isfree, isstrict)
        if include_dirs is not None:
            self.include_dirs = include_dirs[:]
        return
  



###############################################################################
############################## BASE CLASSES ###################################
###############################################################################

class NoMatchError(Exception):
    pass

class ParseError(Exception):
    pass

class Base(object):
    """ Base class for Fortran 2003 syntax rules.

    All Base classes have the following attributes:
      .string - original argument to construct a class instance, it's type
                is either str or FortranReaderBase.
      .item   - Line instance (holds label) or None.
    """
    subclasses = {}

    def __new__(cls, string, parent_cls = None):
        """
        """
        if parent_cls is None:
            parent_cls = [cls]
        elif cls not in parent_cls:
            parent_cls.append(cls)
        #print '__new__:',cls.__name__,`string`
        match = cls.__dict__.get('match', None)
        if isinstance(string, FortranReaderBase) and not issubclass(cls, BlockBase) \
               and match is not None:
            reader = string
            item = reader.get_item()
            if item is None: return
            try:
                obj = cls(item.line, parent_cls = parent_cls)
            except NoMatchError:
                obj = None
            if obj is None:
                reader.put_item(item)
                return
            obj.item = item
            return obj
        errmsg = '%s: %r' % (cls.__name__, string)
        if match is not None:
            try:
                result = cls.match(string)
            except NoMatchError, msg:
                if str(msg)==errmsg: # avoid recursion 1.
                    raise
                result = None
        else:
            result = None

        #print '__new__:result:',cls.__name__,`string,result`
        if isinstance(result, tuple):
            obj = object.__new__(cls)
            obj.string = string
            obj.item = None
            if hasattr(cls, 'init'): obj.init(*result)
            return obj
        elif isinstance(result, Base):
            return result
        elif result is None:
            for subcls in Base.subclasses.get(cls.__name__,[]):
                if subcls in parent_cls: # avoid recursion 2.
                    continue
                #print '%s:%s: %r' % (cls.__name__,subcls.__name__,string)
                try:
                    obj = subcls(string, parent_cls = parent_cls)
                except NoMatchError, msg:
                    obj = None
                if obj is not None:
                    return obj
        else:
            raise AssertionError,`result`
        raise NoMatchError,errmsg

##     def restore_reader(self):
##         self._item.reader.put_item(self._item)
##         return

    def init(self, *items):
        self.items = items
        return
    def torepr(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join(map(repr,self.items)))
    def compare(self, other):
        return cmp(self.items,other.items)

    def __str__(self): return self.tostr()

    def __repr__(self): return self.torepr()

    def __cmp__(self, other):
        if self is other: return 0
        if not isinstance(other, self.__class__): return cmp(self.__class__, other.__class__)
        return self.compare(other)

    def tofortran(self, tab='', isfix=None):
        return tab + str(self)


class BlockBase(Base):
    """
    <block-base> = [ <startcls> ]
                     [ <subcls> ]...
                     ...
                     [ <subcls> ]...
                     [ <endcls> ]
    """
    def match(startcls, subclasses, endcls, reader):
        assert isinstance(reader,FortranReaderBase),`reader`
        content = []
        if startcls is not None:
            try:
                obj = startcls(reader)
            except NoMatchError:
                obj = None
            if obj is None: return
            content.append(obj)
        if endcls is not None:
            classes = subclasses + [endcls]
        else:
            classes = subclasses[:]
        i = 0
        while 1:
            cls = classes[i]
            try:
                obj = cls(reader)
            except NoMatchError:
                obj = None
            if obj is None:
                j = i
                for cls in classes[i+1:]:
                    j += 1
                    try:
                        obj = cls(reader)
                    except NoMatchError:
                        obj = None
                    if obj is not None:
                        break
                if obj is not None:
                    i = j
            if obj is not None:
                content.append(obj)
                if endcls is not None and isinstance(obj, endcls): break
                continue
            if endcls is not None:
                item = reader.get_item()
                if item is not None:
                    reader.error('failed to parse with %s, skipping.' % ('|'.join([c.__name__ for c in classes[i:]])), item)
                    continue
                if hasattr(content[0],'name'):
                    reader.error('unexpected eof file while looking line for <%s> of %s.'\
                                 % (classes[-1].__name__.lower().replace('_','-'), content[0].name))
                else:
                    reader.error('unexpected eof file while looking line for <%s>.'\
                                 % (classes[-1].__name__.lower().replace('_','-')))
            break
        if not content: return
        if startcls is not None and endcls is not None:
            # check names of start and end statements:
            start_stmt = content[0]
            end_stmt = content[-1]
            if isinstance(end_stmt, endcls) and hasattr(end_stmt, 'get_name') and hasattr(start_stmt, 'get_name'):
                if end_stmt.get_name() is not None:
                    if start_stmt.get_name() != end_stmt.get_name():
                        end_stmt._item.reader.error('expected <%s-name> is %s but got %s. Ignoring.'\
                                                    % (end_stmt.get_type().lower(), start_stmt.get_name(), end_stmt.get_name()))
                else:
                    end_stmt.set_name(start_stmt.get_name())
        return content,

    def init(self, content):
        self.content = content
        return
    def compare(self, other):
        return cmp(self.content,other.content)

    def tostr(self):
        return self.tofortran()
    def torepr(self):
        return '%s(%s)' % (self.__class__.__name__,', '.join(map(repr, self.content)))

    def tofortran(self, tab='', isfix=None):
        l = []
        start = self.content[0]
        end = self.content[-1]
        extra_tab = ''
        if isinstance(end, EndStmtBase):
            extra_tab = '  '
        l.append(start.tofortran(tab=tab,isfix=isfix))
        for item in self.content[1:-1]:
            l.append(item.tofortran(tab=tab+extra_tab,isfix=isfix))
        if len(self.content)>1:
            l.append(end.tofortran(tab=tab,isfix=isfix))
        return '\n'.join(l)

##     def restore_reader(self):
##         content = self.content[:]
##         content.reverse()
##         for obj in content:
##             obj.restore_reader()
##         return

class SequenceBase(Base):
    """
    <sequence-base> = <obj>, <obj> [ , <obj> ]...
    """
    def match(separator, subcls, string):
        line, repmap = string_replace_map(string)
        if isinstance(separator, str):
            splitted = line.split(separator)
        else:
            splitted = separator[1].split(line)
            separator = separator[0]
        if len(splitted)<=1: return
        lst = []
        for p in splitted:
            lst.append(subcls(repmap(p.strip())))
        return separator, tuple(lst)
    def init(self, separator, items):
        self.separator = separator
        self.items = items
        return
    def tostr(self):
        s = self.separator
        if s==',': s = s + ' '
        elif s==' ': pass
        else: s = ' ' + s + ' '
        return s.join(map(str, self.items))
    def torepr(self): return '%s(%r, %r)' % (self.__class__.__name__, self.separator, self.items)
    def compare(self, other):
        return cmp((self.separator,self.items),(other.separator,self.items))

class UnaryOpBase(Base):
    """
    <unary-op-base> = <unary-op> <rhs>
    """
    def tostr(self):
        return '%s %s' % tuple(self.items)
    def match(op_pattern, rhs_cls, string):
        m = op_pattern.match(string)
        if not m: return
        #if not m: return rhs_cls(string)
        rhs = string[m.end():].lstrip()
        if not rhs: return
        op = string[:m.end()].rstrip().upper()
        return op, rhs_cls(rhs)


class BinaryOpBase(Base):
    """
    <binary-op-base> = <lhs> <op> <rhs>
    <op> is searched from right by default.
    """
    def match(lhs_cls, op_pattern, rhs_cls, string, right=True):
        line, repmap = string_replace_map(string)
        if isinstance(op_pattern, str):
            if right:
                t = line.rsplit(op_pattern,1)
            else:
                t = line.split(op_pattern,1)
            if len(t)!=2: return
            lhs, rhs = t[0].rstrip(), t[1].lstrip()
            op = op_pattern
        else:
            if right:
                t = op_pattern.rsplit(line)
            else:
                t = op_pattern.lsplit(line)
            if t is None or len(t)!=3: return
            lhs, op, rhs = t
            lhs = lhs.rstrip()
            rhs = rhs.lstrip()
            op = op.upper()
        if not lhs: return
        if not rhs: return
        lhs_obj = lhs_cls(repmap(lhs))
        rhs_obj = rhs_cls(repmap(rhs))
        return lhs_obj, op, rhs_obj
    def tostr(self):
        return '%s %s %s' % tuple(self.items)

class SeparatorBase(Base):
    """
    <separator-base> = [ <lhs> ] : [ <rhs> ]
    """
    def match(lhs_cls, rhs_cls, string, require_lhs=False, require_rhs=False):
        line, repmap = string_replace_map(string)
        if ':' not in line: return
        lhs,rhs = line.split(':',1)
        lhs = lhs.rstrip()
        rhs = rhs.lstrip()
        lhs_obj, rhs_obj = None, None
        if lhs:
            if lhs_cls is None: return
            lhs_obj = lhs_cls(repmap(lhs))
        elif require_lhs:
            return
        if rhs:
            if rhs_cls is None: return
            rhs_obj = rhs_cls(repmap(rhs))
        elif require_rhs:
            return
        return lhs_obj, rhs_obj
    def tostr(self):
        s = ''
        if self.items[0] is not None:
            s += '%s :' % (self.items[0])
        else:
            s += ':'
        if self.items[1] is not None:
            s += ' %s' % (self.items[1])
        return s

class KeywordValueBase(Base):
    """
    <keyword-value-base> = [ <lhs> = ] <rhs>
    """
    def match(lhs_cls, rhs_cls, string, require_lhs = True, upper_lhs = False):
        if require_lhs and '=' not in string: return
        if isinstance(lhs_cls, (list, tuple)):
            for s in lhs_cls:
                try:
                    obj = KeywordValueBase.match(s, rhs_cls, string, require_lhs=require_lhs, upper_lhs=upper_lhs)
                except NoMatchError:
                    obj = None
                if obj is not None: return obj
            return obj
        lhs,rhs = string.split('=',1)
        lhs = lhs.rstrip()
        rhs = rhs.lstrip()
        if not rhs: return
        if not lhs:
            if require_lhs: return
            return None, rhs_cls(rhs)
        if isinstance(lhs_cls, str):
            if upper_lhs:
                lhs = lhs.upper()
            if lhs_cls!=lhs: return
            return lhs, rhs_cls(rhs)
        return lhs_cls(lhs),rhs_cls(rhs)
    def tostr(self):
        if self.items[0] is None: return str(self.items[1])
        return '%s = %s' % tuple(self.items)

class BracketBase(Base):
    """
    <bracket-base> = <left-bracket-base> <something> <right-bracket>
    """
    def match(brackets, cls, string, require_cls=True):
        i = len(brackets)/2
        left = brackets[:i]
        right = brackets[-i:]
        if string.startswith(left) and string.endswith(right):
            line = string[i:-i].strip()
            if not line:
                if require_cls:
                    return
                return left,None,right
            return left,cls(line),right
        return
    def tostr(self):
        if self.items[1] is None:
            return '%s%s' % (self.items[0], self.items[2])
        return '%s%s%s' % tuple(self.items)

class NumberBase(Base):
    """
    <number-base> = <number> [ _ <kind-param> ]
    """
    def match(number_pattern, string):
        m = number_pattern.match(string)
        if m is None: return
        return m.group('value').upper(),m.group('kind_param')
    def tostr(self):
        if self.items[1] is None: return str(self.items[0])
        return '%s_%s' % tuple(self.items)
    def compare(self, other):
        return cmp(self.items[0], other.items[0])

class CallBase(Base):
    """
    <call-base> = <lhs> ( [ <rhs> ] )
    """
    def match(lhs_cls, rhs_cls, string, upper_lhs = False, require_rhs=False):
        if not string.endswith(')'): return
        line, repmap = string_replace_map(string)
        i = line.find('(')
        if i==-1: return
        lhs = line[:i].rstrip()
        if not lhs: return
        rhs = line[i+1:-1].strip()
        lhs = repmap(lhs)
        if upper_lhs:
            lhs = lhs.upper()
        rhs = repmap(rhs)
        if isinstance(lhs_cls, str):
            if lhs_cls!=lhs: return
        else:
            lhs = lhs_cls(lhs)
        if rhs:
            if isinstance(rhs_cls, str):
                if rhs_cls!=rhs: return
            else:
                rhs = rhs_cls(rhs)
            return lhs, rhs
        elif require_rhs:
            return
        return lhs, None
    def tostr(self):
        if self.items[1] is None: return '%s()' % (self.items[0])
        return '%s(%s)' % (self.items[0], self.items[1])

class CALLBase(CallBase):
    """
    <CALL-base> = <LHS> ( [ <rhs> ] )
    """
    def match(lhs_cls, rhs_cls, string, require_rhs = False):
        return CallBase.match(lhs_cls, rhs_cls, string, upper_lhs=True, require_rhs = require_rhs)

class StringBase(Base):
    """
    <string-base> = <xyz>
    """
    def match(pattern, string):
        if isinstance(pattern, (list,tuple)):
            for p in pattern:
                obj = StringBase.match(p, string)
                if obj is not None: return obj
            return
        if isinstance(pattern, str):
            if len(pattern)==len(string) and pattern==string: return string,
            return
        if pattern.match(string): return string,
        return
    def init(self, string):
        self.string = string
        return
    def tostr(self): return str(self.string)
    def torepr(self): return '%s(%r)' % (self.__class__.__name__, self.string)
    def compare(self, other):
        return cmp(self.string,other.string)

class STRINGBase(StringBase):
    """
    <STRING-base> = <XYZ>
    """
    def match(pattern, string):
        if isinstance(pattern, (list,tuple)):
            for p in pattern:
                obj = STRINGBase.match(p, string)
                if obj is not None: return obj
            return
        STRING = string.upper()
        if isinstance(pattern, str):
            if len(pattern)==len(string) and pattern==STRING: return STRING,
            return
        if pattern.match(STRING): return STRING,
        return

class StmtBase(Base):
    """
    [ <label> ] <stmt>
    """
    def tofortran(self, tab='', isfix=None):
        label = None
        if self.item is not None: label = self.item.label
        if isfix:
            colon = ''
            c = ' '
        else:
            colon = ':'
            c = ''
        if label:
            t = c + label + colon
            if isfix:
                while len(t)<6: t += ' '
            else:
                tab = tab[len(t):] or ' '
        else:
            t = ''
        return t + tab + str(self)

class EndStmtBase(StmtBase):
    """
    <end-stmt-base> = END [ <stmt> [ <stmt-name>] ]
    """
    def match(stmt_type, stmt_name, string, require_stmt_type=False):
        start = string[:3].upper()
        if start != 'END': return
        line = string[3:].lstrip()
        start = line[:len(stmt_type)].upper()
        if start:
            if start.replace(' ','') != stmt_type.replace(' ',''): return
            line = line[len(stmt_type):].lstrip()
        else:
            if require_stmt_type: return
            line = ''
        if line:
            if stmt_name is None: return
            return stmt_type, stmt_name(line)
        return stmt_type, None
    def init(self, stmt_type, stmt_name):
        self.items = [stmt_type, stmt_name]
        self.type, self.name = stmt_type, stmt_name
        return
    def get_name(self): return self.items[1]
    def get_type(self): return self.items[0]
    def set_name(self, name):
        self.items[1] = name
    def tostr(self):
        if self.items[1] is not None:
            return 'END %s %s' % tuple(self.items)
        return 'END %s' % (self.items[0])
    def torepr(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.type, self.name)

def isalnum(c): return c.isalnum() or c=='_'

class WORDClsBase(Base):
    """
    <WORD-cls> = <WORD> [ [ :: ] <cls> ]
    """
    def match(pattern, cls, string, check_colons=False, require_cls=False):
        if isinstance(pattern, (tuple,list)):
            for p in pattern:
                try:
                    obj = WORDClsBase.match(p, cls, string, check_colons=check_colons, require_cls=require_cls)
                except NoMatchError:
                    obj = None
                if obj is not None: return obj
            return
        if isinstance(pattern, str):
            if string[:len(pattern)].upper()!=pattern: return
            line = string[len(pattern):]
            if not line: return pattern, None
            if isalnum(line[0]): return
            line = line.lstrip()
            if check_colons and line.startswith('::'):
                line = line[2:].lstrip()
            if not line:
                if require_cls: return
                return pattern, None
            if cls is None: return
            return pattern, cls(line)
        m = pattern.match(string)
        if m is None: return
        line = string[len(m.group()):]
        if pattern.value is not None:
            pattern_value = pattern.value
        else:
            pattern_value = m.group().upper()
        if not line: return pattern_value, None
        if isalnum(line[0]): return
        line = line.lstrip()
        if check_colons and line.startswith('::'):
            line = line[2:].lstrip()
        if not line:
            if require_cls: return
            return pattern_value, None
        if cls is None: return
        return pattern_value, cls(line)
    def tostr(self):
        if self.items[1] is None: return str(self.items[0])
        s = str(self.items[1])
        if s and s[0] in '(*':
            return '%s%s' % (self.items[0], s)
        return '%s %s' % (self.items[0], s)
    def tostr_a(self): # colons version of tostr
        if self.items[1] is None: return str(self.items[0])
        return '%s :: %s' % (self.items[0], self.items[1])

###############################################################################
############################### SECTION  1 ####################################
###############################################################################

#R101: <xyz-list> = <xyz> [ , <xyz> ]...
#R102: <xyz-name> = <name>
#R103: <scalar-xyz> = <xyz>

###############################################################################
############################### SECTION  2 ####################################
###############################################################################

class Program(BlockBase): # R201
    """
    <program> = <program-unit>
                  [ <program-unit> ] ...
    """
    subclass_names = []
    use_names = ['Program_Unit']
    def match(reader):
        return BlockBase.match(Program_Unit, [Program_Unit], None, reader)

class Program_Unit(Base): # R202
    """
    <program-unit> = <main-program>
                     | <external-subprogram>
                     | <module>
                     | <block-data>
    """
    subclass_names = ['Main_Program', 'External_Subprogram', 'Module', 'Block_Data']

class External_Subprogram(Base): # R203
    """
    <external-subprogram> = <function-subprogram>
                            | <subroutine-subprogram>
    """
    subclass_names = ['Function_Subprogram', 'Subroutine_Subprogram']


class Specification_Part(BlockBase): # R204
    """
    <specification-part> = [ <use-stmt> ]...
                             [ <import-stmt> ]...
                             [ <implicit-part> ]
                             [ <declaration-construct> ]...
    """
    subclass_names = []
    use_names = ['Use_Stmt', 'Import_Stmt', 'Implicit_Part', 'Declaration_Construct']
    def match(reader):
        return BlockBase.match(None, [Use_Stmt, Import_Stmt, Implicit_Part, Declaration_Construct], None, reader)

class Implicit_Part(Base): # R205
    """
    <implicit-part> = [ <implicit-part-stmt> ]...
                        <implicit-stmt>
    """
    subclass_names = []
    use_names = ['Implicit_Part_Stmt', 'Implicit_Stmt']

class Implicit_Part_Stmt(Base): # R206
    """
    <implicit-part-stmt> = <implicit-stmt>
                           | <parameter-stmt>
                           | <format-stmt>
                           | <entry-stmt>
    """
    subclass_names = ['Implicit_Stmt', 'Parameter_Stmt', 'Format_Stmt', 'Entry_Stmt']

class Declaration_Construct(Base): # R207
    """
    <declaration-construct> = <derived-type-def>
                              | <entry-stmt>
                              | <enum-def>
                              | <format-stmt>
                              | <interface-block>
                              | <parameter-stmt>
                              | <procedure-declaration-stmt>
                              | <specification-stmt>
                              | <type-declaration-stmt>
                              | <stmt-function-stmt>
    """
    subclass_names = ['Derived_Type_Def', 'Entry_Stmt', 'Enum_Def', 'Format_Stmt',
                      'Interface_Block', 'Parameter_Stmt', 'Procedure_Declaration_Stmt',
                      'Specification_Stmt', 'Type_Declaration_Stmt', 'Stmt_Function_Stmt']

class Execution_Part(BlockBase): # R208
    """
    <execution-part> = <executable-construct>
                       | [ <execution-part-construct> ]...

    <execution-part> shall not contain <end-function-stmt>, <end-program-stmt>, <end-subroutine-stmt>
    """
    subclass_names = []
    use_names = ['Executable_Construct_C201', 'Execution_Part_Construct_C201']
    def match(string): return BlockBase.match(Executable_Construct_C201, [Execution_Part_Construct_C201], None, string)

class Execution_Part_Construct(Base): # R209
    """
    <execution-part-construct> = <executable-construct>
                                 | <format-stmt>
                                 | <entry-stmt>
                                 | <data-stmt>
    """
    subclass_names = ['Executable_Construct', 'Format_Stmt', 'Entry_Stmt', 'Data_Stmt']

class Execution_Part_Construct_C201(Base):
    subclass_names = ['Executable_Construct_C201', 'Format_Stmt', 'Entry_Stmt', 'Data_Stmt']

class Internal_Subprogram_Part(Base): # R210
    """
    <internal-subprogram-part> = <contains-stmt>
                                   <internal-subprogram>
                                   [ <internal-subprogram> ]...
    """
    subclass_names = []
    use_names = ['Contains_Stmt', 'Internal_Subprogram']

class Internal_Subprogram(Base): # R211
    """
    <internal-subprogram> = <function-subprogram>
                            | <subroutine-subprogram>
    """
    subclass_names = ['Function_Subprogram', 'Subroutine_Subprogram']

class Specification_Stmt(Base):# R212
    """
    <specification-stmt> = <access-stmt>
                           | <allocatable-stmt>
                           | <asynchronous-stmt>
                           | <bind-stmt>
                           | <common-stmt>
                           | <data-stmt>
                           | <dimension-stmt>
                           | <equivalence-stmt>
                           | <external-stmt>
                           | <intent-stmt>
                           | <intrinsic-stmt>
                           | <namelist-stmt>
                           | <optional-stmt>
                           | <pointer-stmt>
                           | <protected-stmt>
                           | <save-stmt>
                           | <target-stmt>
                           | <volatile-stmt>
                           | <value-stmt>
    """
    subclass_names = ['Access_Stmt', 'Allocatable_Stmt', 'Asynchronous_Stmt','Bind_Stmt',
                      'Common_Stmt', 'Data_Stmt', 'Dimension_Stmt', 'Equivalence_Stmt',
                      'External_Stmt', 'Intent_Stmt', 'Intrinsic_Stmt', 'Namelist_Stmt',
                      'Optional_Stmt','Pointer_Stmt','Protected_Stmt','Save_Stmt',
                      'Target_Stmt','Volatile_Stmt', 'Value_Stmt']

class Executable_Construct(Base):# R213
    """
    <executable-construct> = <action-stmt>
                             | <associate-stmt>
                             | <case-construct>
                             | <do-construct>
                             | <forall-construct>
                             | <if-construct>
                             | <select-type-construct>
                             | <where-construct>
    """
    subclass_names = ['Action_Stmt', 'Associate_Stmt', 'Case_Construct', 'Do_Construct',
                      'Forall_Construct', 'If_Construct', 'Select_Type_Construct', 'Where_Construct']

class Executable_Construct_C201(Base):
    subclass_names = Executable_Construct.subclass_names[:]
    subclass_names[subclass_names.index('Action_Stmt')] = 'Action_Stmt_C201'


class Action_Stmt(Base):# R214
    """
    <action-stmt> = <allocate-stmt>
                    | <assignment-stmt>
                    | <backspace-stmt>
                    | <call-stmt>
                    | <close-stmt>
                    | <continue-stmt>
                    | <cycle-stmt>
                    | <deallocate-stmt>
                    | <endfile-stmt>
                    | <end-function-stmt>
                    | <end-program-stmt>
                    | <end-subroutine-stmt>
                    | <exit-stmt>
                    | <flush-stmt>
                    | <forall-stmt>
                    | <goto-stmt>
                    | <if-stmt>
                    | <inquire-stmt>
                    | <nullify-stmt>
                    | <open-stmt>
                    | <pointer-assignment-stmt>
                    | <print-stmt>
                    | <read-stmt>
                    | <return-stmt>
                    | <rewind-stmt>
                    | <stop-stmt>
                    | <wait-stmt>
                    | <where-stmt>
                    | <write-stmt>
                    | <arithmetic-if-stmt>
                    | <computed-goto-stmt>
    """
    subclass_names = ['Allocate_Stmt', 'Assignment_Stmt', 'Backspace_Stmt', 'Call_Stmt',
                      'Close_Stmt', 'Continue_Stmt', 'Cycle_Stmt', 'Deallocate_Stmt',
                      'Endfile_Stmt', 'End_Function_Stmt', 'End_Subroutine_Stmt', 'Exit_Stmt',
                      'Flush_Stmt', 'Forall_Stmt', 'Goto_Stmt', 'If_Stmt', 'Inquire_Stmt',
                      'Nullify_Stmt', 'Open_Stmt', 'Pointer_Assignment_Stmt', 'Print_Stmt',
                      'Read_Stmt', 'Return_Stmt', 'Rewind_Stmt', 'Stop_Stmt', 'Wait_Stmt',
                      'Where_Stmt', 'Write_Stmt', 'Arithmetic_If_Stmt', 'Computed_Goto_Stmt']

class Action_Stmt_C201(Base):
    """
    <action-stmt-c201> = <action-stmt>
    C201 is applied.
    """
    subclass_names = Action_Stmt.subclass_names[:]
    subclass_names.remove('End_Function_Stmt')
    subclass_names.remove('End_Subroutine_Stmt')
    #subclass_names.remove('End_Program_Stmt')

class Action_Stmt_C802(Base):
    """
    <action-stmt-c802> = <action-stmt>
    C802 is applied.
    """
    subclass_names = Action_Stmt.subclass_names[:]
    subclass_names.remove('End_Function_Stmt')
    subclass_names.remove('End_Subroutine_Stmt')
    subclass_names.remove('If_Stmt')

class Action_Stmt_C824(Base):
    """
    <action-stmt-c824> = <action-stmt>
    C824 is applied.
    """
    subclass_names = Action_Stmt.subclass_names[:]
    subclass_names.remove('End_Function_Stmt')
    subclass_names.remove('End_Subroutine_Stmt')
    subclass_names.remove('Continue_Stmt')
    subclass_names.remove('Goto_Stmt')
    subclass_names.remove('Return_Stmt')
    subclass_names.remove('Stop_Stmt')
    subclass_names.remove('Exit_Stmt')
    subclass_names.remove('Cycle_Stmt')
    subclass_names.remove('Arithmetic_If_Stmt')

class Keyword(Base): # R215
    """
    <keyword> = <name>
    """
    subclass_names = ['Name']

###############################################################################
############################### SECTION  3 ####################################
###############################################################################

#R301: <character> = <alphanumeric-character> | <special-character>
#R302: <alphanumeric-character> = <letter> | <digit> | <underscore>
#R303: <underscore> = _

class Name(StringBase): # R304
    """
    <name> = <letter> [ <alphanumeric_character> ]...
    """
    subclass_names = []
    def match(string): return StringBase.match(pattern.abs_name, string)

class Constant(Base): # R305
    """
    <constant> = <literal-constant>
                 | <named-constant>
    """
    subclass_names = ['Literal_Constant','Named_Constant']

class Literal_Constant(Base): # R306
    """
    <literal-constant> = <int-literal-constant>
                         | <real-literal-constant>
                         | <complex-literal-constant>
                         | <logical-literal-constant>
                         | <char-literal-constant>
                         | <boz-literal-constant>
    """
    subclass_names = ['Int_Literal_Constant', 'Real_Literal_Constant','Complex_Literal_Constant',
                      'Logical_Literal_Constant','Char_Literal_Constant','Boz_Literal_Constant']

class Named_Constant(Base): # R307
    """
    <named-constant> = <name>
    """
    subclass_names = ['Name']

class Int_Constant(Base): # R308
    """
    <int-constant> = <constant>
    """
    subclass_names = ['Constant']

class Char_Constant(Base): # R309
    """
    <char-constant> = <constant>
    """
    subclass_names = ['Constant']

#R310: <intrinsic-operator> = <power-op> | <mult-op> | <add-op> | <concat-op> | <rel-op> | <not-op> | <and-op> | <or-op> | <equiv-op>
#R311: <defined-operator> = <defined-unary-op> | <defined-binary-op> | <extended-intrinsic-op>
#R312: <extended-intrinsic-op> = <intrinsic-op>

class Label(StringBase): # R313
    """
    <label> = <digit> [ <digit> [ <digit> [ <digit> [ <digit> ] ] ] ]
    """
    subclass_names = []
    def match(string): return StringBase.match(pattern.abs_label, string)

###############################################################################
############################### SECTION  4 ####################################
###############################################################################

class Type_Spec(Base): # R401
    """
    <type-spec> = <intrinsic-type-spec>
                  | <derived-type-spec>
    """
    subclass_names = ['Intrinsic_Type_Spec', 'Derived_Type_Spec']

class Type_Param_Value(StringBase): # R402
    """
    <type-param-value> = <scalar-int-expr>
                       | *
                       | :
    """
    subclass_names = ['Scalar_Int_Expr']
    use_names = []
    def match(string): return StringBase.match(['*',':'], string)

class Intrinsic_Type_Spec(WORDClsBase): # R403
    """
    <intrinsic-type-spec> = INTEGER [ <kind-selector> ]
                            | REAL [ <kind-selector> ]
                            | DOUBLE COMPLEX
                            | COMPLEX [ <kind-selector> ]
                            | CHARACTER [ <char-selector> ]
                            | LOGICAL [ <kind-selector> ]
    Extensions:
                            | DOUBLE PRECISION
                            | BYTE
    """
    subclass_names = []
    use_names = ['Kind_Selector','Char_Selector']

    def match(string):
        for w,cls in [('INTEGER',Kind_Selector),
                      ('REAL',Kind_Selector),
                      ('COMPLEX',Kind_Selector),
                      ('LOGICAL',Kind_Selector),
                      ('CHARACTER',Char_Selector),
                      (pattern.abs_double_complex_name, None),
                      (pattern.abs_double_precision_name, None),
                      ('BYTE', None),
                      ]:
            try:
                obj = WORDClsBase.match(w,cls,string)
            except NoMatchError:
                obj = None
            if obj is not None: return obj
        return


class Kind_Selector(Base): # R404
    """
    <kind-selector> = ( [ KIND = ] <scalar-int-initialization-expr> )
    Extensions:
                      | * <char-length>
    """
    subclass_names = []
    use_names = ['Char_Length','Scalar_Int_Initialization_Expr']

    def match(string):
        if string[0]+string[-1] != '()':
            if not string.startswith('*'): return
            return '*',Char_Length(string[1:].lstrip())
        line = string[1:-1].strip()
        if line[:4].upper()=='KIND':
            line = line[4:].lstrip()
            if not line.startswith('='): return
            line = line[1:].lstrip()
        return '(',Scalar_Int_Initialization_Expr(line),')'
    def tostr(self):
        if len(self.items)==2: return '%s%s' % tuple(self.items)
        return '%sKIND = %s%s' % tuple(self.items)

class Signed_Int_Literal_Constant(NumberBase): # R405
    """
    <signed-int-literal-constant> = [ <sign> ] <int-literal-constant>
    """
    subclass_names = ['Int_Literal_Constant'] # never used because sign is included in pattern
    def match(string):
        return NumberBase.match(pattern.abs_signed_int_literal_constant_named, string)

class Int_Literal_Constant(NumberBase): # R406
    """
    <int-literal-constant> = <digit-string> [ _ <kind-param> ]
    """
    subclass_names = []
    def match(string):
        return NumberBase.match(pattern.abs_int_literal_constant_named, string)

#R407: <kind-param> = <digit-string> | <scalar-int-constant-name>
#R408: <signed-digit-string> = [ <sign> ] <digit-string>
#R409: <digit-string> = <digit> [ <digit> ]...
#R410: <sign> = + | -

class Boz_Literal_Constant(Base): # R411
    """
    <boz-literal-constant> = <binary-constant>
                             | <octal-constant>
                             | <hex-constant>
    """
    subclass_names = ['Binary_Constant','Octal_Constant','Hex_Constant']

class Binary_Constant(STRINGBase): # R412
    """
    <binary-constant> = B ' <digit> [ <digit> ]... '
                        | B \" <digit> [ <digit> ]... \"
    """
    subclass_names = []
    def match(string): return STRINGBase.match(pattern.abs_binary_constant, string)

class Octal_Constant(STRINGBase): # R413
    """
    <octal-constant> = O ' <digit> [ <digit> ]... '
                       | O \" <digit> [ <digit> ]... \"
    """
    subclass_names = []
    def match(string): return STRINGBase.match(pattern.abs_octal_constant, string)

class Hex_Constant(STRINGBase): # R414
    """
    <hex-constant> = Z ' <digit> [ <digit> ]... '
                     | Z \" <digit> [ <digit> ]... \"
    """
    subclass_names = []
    def match(string): return STRINGBase.match(pattern.abs_hex_constant, string)

#R415: <hex-digit> = <digit> | A | B | C | D | E | F

class Signed_Real_Literal_Constant(NumberBase): # R416
    """
    <signed-real-literal-constant> = [ <sign> ] <real-literal-constant>
    """
    subclass_names = ['Real_Literal_Constant'] # never used
    def match(string):
        return NumberBase.match(pattern.abs_signed_real_literal_constant_named, string)

class Real_Literal_Constant(NumberBase): # R417
    """
    """
    subclass_names = []
    def match(string):
        return NumberBase.match(pattern.abs_real_literal_constant_named, string)

#R418: <significand> = <digit-string> . [ <digit-string> ]  | . <digit-string>
#R419: <exponent-letter> = E | D
#R420: <exponent> = <signed-digit-string>

class Complex_Literal_Constant(Base): # R421
    """
    <complex-literal-constant> = ( <real-part>, <imag-part> )
    """
    subclass_names = []
    use_names = ['Real_Part','Imag_Part']
    def match(string):
        if not string or string[0]+string[-1]!='()': return
        if not pattern.abs_complex_literal_constant.match(string):
            return
        r,i = string[1:-1].split(',')
        return Real_Part(r.strip()), Imag_Part(i.strip())
    def tostr(self): return '(%s, %s)' % tuple(self.items)

class Real_Part(Base): # R422
    """
    <real-part> = <signed-int-literal-constant>
                  | <signed-real-literal-constant>
                  | <named-constant>
    """
    subclass_names = ['Signed_Int_Literal_Constant','Signed_Real_Literal_Constant','Named_Constant']

class Imag_Part(Base): # R423
    """
    <imag-part> = <real-part>
    """
    subclass_names = ['Signed_Int_Literal_Constant','Signed_Real_Literal_Constant','Named_Constant']

class Char_Selector(Base): # R424
    """
    <char-selector> = <length-selector>
                      | ( LEN = <type-param-value> , KIND = <scalar-int-initialization-expr> )
                      | ( <type-param-value> , [ KIND = ] <scalar-int-initialization-expr> )
                      | ( KIND = <scalar-int-initialization-expr> [ , LEN = <type-param-value> ] )
    """
    subclass_names = ['Length_Selector']
    use_names = ['Type_Param_Value','Scalar_Int_Initialization_Expr']
    def match(string):
        if string[0]+string[-1] != '()': return
        line, repmap = string_replace_map(string[1:-1].strip())
        if line[:3].upper()=='LEN':
            line = line[3:].lstrip()
            if not line.startswith('='): return
            line = line[1:].lstrip()
            i = line.find(',')
            if i==-1: return
            v = line[:i].rstrip()
            line = line[i+1:].lstrip()
            if line[:4].upper()!='KIND': return
            line = line[4:].lstrip()
            if not line.startswith('='): return
            line = line[1:].lstrip()
            v = repmap(v)
            line = repmap(line)
            return Type_Param_Value(v), Scalar_Int_Initialization_Expr(line)
        elif line[:4].upper()=='KIND':
            line = line[4:].lstrip()
            if not line.startswith('='): return
            line = line[1:].lstrip()
            i = line.find(',')
            if i==-1: return None,Scalar_Int_Initialization_Expr(line)
            v = line[i+1:].lstrip()
            line = line[:i].rstrip()
            if v[:3].upper()!='LEN': return
            v = v[3:].lstrip()
            if not v.startswith('='): return
            v = v[1:].lstrip()
            return Type_Param_Value(v), Scalar_Int_Initialization_Expr(line)
        else:
            i = line.find(',')
            if i==-1: return
            v = line[:i].rstrip()
            line = line[i+1:].lstrip()
            if line[:4].upper()=='KIND':
                line = line[4:].lstrip()
                if not line.startswith('='): return
                line = line[1:].lstrip()
            return Type_Param_Value(v), Scalar_Int_Initialization_Expr(line)
        return
    def tostr(self):
        if self.items[0] is None:
            return '(KIND = %s)' % (self.items[1])
        return '(LEN = %s, KIND = %s)' % (self.items[0],self.items[1])

class Length_Selector(Base): # R425
    """
    <length -selector> = ( [ LEN = ] <type-param-value> )
                        | * <char-length> [ , ]
    """
    subclass_names = []
    use_names = ['Type_Param_Value','Char_Length']
    def match(string):
        if string[0]+string[-1] == '()':
            line = string[1:-1].strip()
            if line[:3].upper()=='LEN':
                line = line[3:].lstrip()
                if not line.startswith('='): return
                line = line[1:].lstrip()
            return '(',Type_Param_Value(line),')'
        if not string.startswith('*'): return
        line = string[1:].lstrip()
        if string[-1]==',': line = line[:-1].rstrip()
        return '*',Char_Length(line)
    def tostr(self):
        if len(self.items)==2: return '%s%s' % tuple(self.items)
        return '%sLEN = %s%s' % tuple(self.items)

class Char_Length(BracketBase): # R426
    """
    <char-length> = ( <type-param-value> )
                    | <scalar-int-literal-constant>
    """
    subclass_names = ['Scalar_Int_Literal_Constant']
    use_names = ['Type_Param_Value']
    def match(string): return BracketBase.match('()',Type_Param_Value, string)

class Char_Literal_Constant(Base): # R427
    """
    <char-literal-constant> = [ <kind-param> _ ] ' <rep-char> '
                              | [ <kind-param> _ ] \" <rep-char> \"
    """
    subclass_names = []
    rep = pattern.char_literal_constant
    def match(string):
        if string[-1] not in '"\'': return
        if string[-1]=='"':
            abs_a_n_char_literal_constant_named = pattern.abs_a_n_char_literal_constant_named2
        else:
            abs_a_n_char_literal_constant_named = pattern.abs_a_n_char_literal_constant_named1
        line, repmap = string_replace_map(string)
        m = abs_a_n_char_literal_constant_named.match(line)
        if not m: return
        kind_param = m.group('kind_param')
        line = m.group('value')
        line = repmap(line)
        return line, kind_param
    def tostr(self):
        if self.items[1] is None: return str(self.items[0])
        return '%s_%s' % (self.items[1], self.items[0])

class Logical_Literal_Constant(NumberBase): # R428
    """
    <logical-literal-constant> = .TRUE. [ _ <kind-param> ]
                                 | .FALSE. [ _ <kind-param> ]
    """
    subclass_names = []
    def match(string):
        return NumberBase.match(pattern.abs_logical_literal_constant_named, string)

class Derived_Type_Def(Base): # R429
    """
    <derived-type-def> = <derived-type-stmt>
                           [ <type-param-def-stmt> ]...
                           [ <private-or-sequence> ]...
                           [ <component-part> ]
                           [ <type-bound-procedure-part> ]
                           <end-type-stmt>
    """
    subclass_names = []
    use_names = ['Derived_Type_Stmt', 'Type_Param_Def_Stmt', 'Private_Or_Sequence',
                 'Component_Part', 'Type_Bound_Procedure_Part', 'End_Type_Stmt']

class Derived_Type_Stmt(StmtBase): # R430
    """
    <derived-type-stmt> = TYPE [ [ , <type-attr-spec-list> ] :: ] <type-name> [ ( <type-param-name-list> ) ]
    """
    subclass_names = []
    use_names = ['Type_Attr_Spec_List', 'Type_Name', 'Type_Param_Name_List']
    def match(string):
        if string[:4].upper()!='TYPE': return
        line = string[4:].lstrip()
        i = line.find('::')
        attr_specs = None
        if i!=-1:
            if line.startswith(','):
                l = line[1:i].strip()
                if not l: return
                attr_specs = Type_Attr_Spec_List(l)
            line = line[i+2:].lstrip()
        m = pattern.name.match(line)
        if m is None: return
        name = Type_Name(m.group())
        line = line[m.end():].lstrip()
        if not line: return attr_specs, name, None
        if line[0]+line[-1]!='()': return
        return attr_specs, name, Type_Param_Name_List(line[1:-1].strip())
    def tostr(self):
        s = 'TYPE'
        if self.items[0] is not None:
            s += ', %s :: %s' % (self.items[0], self.items[1])
        else:
            s += ' :: %s' % (self.items[1])
        if self.items[2] is not None:
            s += '(%s)' % (self.items[2])
        return s

class Type_Name(Name): # C424
    """
    <type-name> = <name>
    <type-name> shall not be DOUBLEPRECISION or the name of intrinsic type
    """
    subclass_names = []
    use_names = []
    def match(string):
        if pattern.abs_intrinsic_type_name.match(string): return
        return Name.match(string)

class Type_EXTENDS_Parent_Type_Name(CALLBase):
    """
    <..> = EXTENDS ( <parent-type-name> )
    """
    subclass_names = []
    use_names = ['Parent_Type_Name']
    def match(string): return CALLBase.match('EXTENDS', Parent_Type_Name, string)

class Type_Attr_Spec(STRINGBase): # R431
    """
    <type-attr-spec> = <access-spec>
                       | EXTENDS ( <parent-type-name> )
                       | ABSTRACT
                       | BIND (C)
    """
    subclass_names = ['Access_Spec', 'Type_EXTENDS_Parent_Type_Name', 'Language_Binding_Spec']
    def match(string): return STRINGBase.match('ABSTRACT', string)

class Private_Or_Sequence(Base): # R432
    """
    <private-or-sequence> = <private-components-stmt>
                            | <sequence-stmt>
    """
    subclass_names = ['Private_Components_Stmt', 'Sequence_Stmt']

class End_Type_Stmt(EndStmtBase): # R433
    """
    <end-type-stmt> = END TYPE [ <type-name> ]
    """
    subclass_names = []
    use_names = ['Type_Name']
    def match(string): return EndStmtBase.match('TYPE',Type_Name, string, require_stmt_type=True)

class Sequence_Stmt(STRINGBase): # R434
    """
    <sequence-stmt> = SEQUENCE
    """
    subclass_names = []
    def match(string): return STRINGBase.match('SEQUENCE', string)
    pass

class Type_Param_Def_Stmt(StmtBase): # R435
    """
    <type-param-def-stmt> = INTEGER [ <kind-selector> ] , <type-param-attr-spec> :: <type-param-decl-list>
    """
    subclass_names = []
    use_names = ['Kind_Selector', 'Type_Param_Attr_Spec', 'Type_Param_Decl_List']
    def match(string):
        if string[:7].upper()!='INTEGER': return
        line, repmap = string_replace_map(string[7:].lstrip())
        if not line: return
        i = line.find(',')
        if i==-1: return
        kind_selector = repmap(line[:i].rstrip()) or None
        line = repmap(line[i+1:].lstrip())
        i = line.find('::')
        if i==-1: return
        l1 = line[:i].rstrip()
        l2 = line[i+2:].lstrip()
        if not l1 or not l2: return
        if kind_selector: kind_selector = Kind_Selector(kind_selector)
        return kind_selector, Type_Param_Attr_Spec(l1), Type_Param_Decl_List(l2)
    pass
    def tostr(self):
        s = 'INTEGER'
        if self.items[0] is not None:
            s += '%s, %s :: %s' % tuple(self.items)
        else:
            s += ', %s :: %s' % tuple(self.items[1:])
        return s

class Type_Param_Decl(BinaryOpBase): # R436
    """
    <type-param-decl> = <type-param-name> [ = <scalar-int-initialization-expr> ]
    """
    subclass_names = ['Type_Param_Name']
    use_names = ['Scalar_Int_Initialization_Expr']
    def match(string):
        if '=' not in string: return
        lhs,rhs = string.split('=',1)
        lhs = lhs.rstrip()
        rhs = rhs.lstrip()
        if not lhs or not rhs: return
        return Type_Param_Name(lhs),'=',Scalar_Int_Initialization_Expr(rhs)
    pass

class Type_Param_Attr_Spec(STRINGBase): # R437
    """
    <type-param-attr-spec> = KIND
                             | LEN
    """
    subclass_names = []
    def match(string): return STRINGBase.match(['KIND', 'LEN'], string)
    pass


class Component_Part(BlockBase): # R438
    """
    <component-part> = [ <component-def-stmt> ]...
    """
    subclass_names = []
    use_names = ['Component_Def_Stmt']
    def match(reader):
        content = []
        while 1:
            try:
                obj = Component_Def_Stmt(reader)
            except NoMatchError:
                obj = None
            if obj is None:
                break
            content.append(obj)
        if content:
            return content,
        return
    pass

    def tofortran(self, tab='', isfix=None):
        l = []
        for item in self.content:
            l.append(item.tofortran(tab=tab,isfix=isfix))
        return '\n'.join(l)

class Component_Def_Stmt(Base): # R439
    """
    <component-def-stmt> = <data-component-def-stmt>
                           | <proc-component-def-stmt>
    """
    subclass_names = ['Data_Component_Def_Stmt', 'Proc_Component_Def_Stmt']

class Data_Component_Def_Stmt(StmtBase): # R440
    """
    <data-component-def-stmt> = <declaration-type-spec> [ [ , <component-attr-spec-list> ] :: ] <component-decl-list>
    """
    subclass_names = []
    use_names = ['Declaration_Type_Spec', 'Component_Attr_Spec_List', 'Component_Decl_List']

class Dimension_Component_Attr_Spec(CALLBase):
    """
    <dimension-component-attr-spec> = DIMENSION ( <component-array-spec> )
    """
    subclass_names = []
    use_names = ['Component_Array_Spec']
    def match(string): return CALLBase.match('DIMENSION', Component_Array_Spec, string)
    pass

class Component_Attr_Spec(STRINGBase): # R441
    """
    <component-attr-spec> = POINTER
                            | DIMENSION ( <component-array-spec> )
                            | ALLOCATABLE
                            | <access-spec>
    """
    subclass_names = ['Access_Spec', 'Dimension_Component_Attr_Spec']
    use_names = []
    def match(string): return STRINGBase.match(['POINTER', 'ALLOCATABLE'], string)
    pass

class Component_Decl(Base): # R442
    """
    <component-decl> = <component-name> [ ( <component-array-spec> ) ] [ * <char-length> ] [ <component-initialization> ]
    """
    subclass_names = []
    use_names = ['Component_Name', 'Component_Array_Spec', 'Char_Length', 'Component_Initialization']
    def match(string):
        m = pattern.name.match(string)
        if m is None: return
        name = Component_Name(m.group())
        newline = string[m.end():].lstrip()
        if not newline: return name, None, None, None
        array_spec = None
        char_length = None
        init = None
        if newline.startswith('('):
            line, repmap = string_replace_map(newline)
            i = line.find(')')
            if i==-1: return
            array_spec = Component_Array_Spec(repmap(line[1:i].strip()))
            newline = repmap(line[i+1:].lstrip())
        if newline.startswith('*'):
            line, repmap = string_replace_map(newline)
            i = line.find('=')
            if i!=-1:
                char_length = repmap(line[1:i].strip())
                newline = repmap(newline[i:].lstrip())
            else:
                char_length = repmap(newline[1:].strip())
                newline = ''
            char_length = Char_Length(char_length)
        if newline.startswith('='):
            init = Component_Initialization(newline)
        else:
            assert newline=='',`newline`
        return name, array_spec, char_length, init
    pass
    def tostr(self):
        s = str(self.items[0])
        if self.items[1] is not None:
            s += '(' + str(self.items[1]) + ')'
        if self.items[2] is not None:
            s += '*' + str(self.items[2])
        if self.items[3] is not None:
            s += ' ' + str(self.items[3])
        return s

class Component_Array_Spec(Base): # R443
    """
    <component-array-spec> = <explicit-shape-spec-list>
                             | <deferred-shape-spec-list>
    """
    subclass_names = ['Explicit_Shape_Spec_List', 'Deferred_Shape_Spec_List']

class Component_Initialization(Base): # R444
    """
    <component-initialization> =  = <initialization-expr>
                                 | => <null-init>
    """
    subclass_names = []
    use_names = ['Initialization_Expr', 'Null_Init']
    def match(string):
        if string.startswith('=>'):
            return '=>', Null_Init(string[2:].lstrip())
        if string.startswith('='):
            return '=', Initialization_Expr(string[2:].lstrip())
        return
    pass
    def tostr(self): return '%s %s' % tuple(self.items)


class Proc_Component_Def_Stmt(StmtBase): # R445
    """
    <proc-component-def-stmt> = PROCEDURE ( [ <proc-interface> ] ) , <proc-component-attr-spec-list> :: <proc-decl-list>
    """
    subclass_names = []
    use_names = ['Proc_Interface', 'Proc_Component_Attr_Spec_List', 'Proc_Decl_List']

class Proc_Component_PASS_Arg_Name(CALLBase):
    """
    <proc-component-PASS-arg-name> = PASS ( <arg-name> )
    """
    subclass_names = []
    use_names = ['Arg_Name']
    def match(string): return CALLBase.match('PASS', Arg_Name, string)
    pass

class Proc_Component_Attr_Spec(STRINGBase): # R446
    """
    <proc-component-attr-spec> = POINTER
                                 | PASS [ ( <arg-name> ) ]
                                 | NOPASS
                                 | <access-spec>
    """
    subclass_names = ['Access_Spec', 'Proc_Component_PASS_Arg_Name']
    def match(string): return STRINGBase.match(['POINTER','PASS','NOPASS'], string)
    pass

class Private_Components_Stmt(StmtBase): # R447
    """
    <private-components-stmt> = PRIVATE
    """
    subclass_names = []
    def match(string): return StringBase.match('PRIVATE', string)
    pass

class Type_Bound_Procedure_Part(Base): # R448
    """
    <type-bound-procedure-part> = <contains-stmt>
                                      [ <binding-private-stmt> ]
                                      <proc-binding-stmt>
                                      [ <proc-binding-stmt> ]...
    """
    subclass_names = []
    use_names = ['Contains_Stmt', 'Binding_Private_Stmt', 'Proc_Binding_Stmt']

class Binding_Private_Stmt(StmtBase, STRINGBase): # R449
    """
    <binding-private-stmt> = PRIVATE
    """
    subclass_names = []
    def match(string): return StringBase.match('PRIVATE', string)
    pass

class Proc_Binding_Stmt(Base): # R450
    """
    <proc-binding-stmt> = <specific-binding>
                          | <generic-binding>
                          | <final-binding>
    """
    subclass_names = ['Specific_Binding', 'Generic_Binding', 'Final_Binding']

class Specific_Binding(StmtBase): # R451
    """
    <specific-binding> = PROCEDURE [ ( <interface-name> ) ] [ [ , <binding-attr-list> ] :: ] <binding-name> [ => <procedure-name> ]
    """
    subclass_names = []
    use_names = ['Interface_Name', 'Binding_Attr_List', 'Binding_Name', 'Procedure_Name']

class Generic_Binding(StmtBase): # R452
    """
    <generic-binding> = GENERIC [ , <access-spec> ] :: <generic-spec> => <binding-name-list>
    """
    subclass_names = []
    use_names = ['Access_Spec', 'Generic_Spec', 'Binding_Name_List']

class Binding_PASS_Arg_Name(CALLBase):
    """
    <binding-PASS-arg-name> = PASS ( <arg-name> )
    """
    subclass_names = []
    use_names = ['Arg_Name']
    def match(string): return CALLBase.match('PASS', Arg_Name, string)
    pass

class Binding_Attr(STRINGBase): # R453
    """
    <binding-attr> = PASS [ ( <arg-name> ) ]
                     | NOPASS
                     | NON_OVERRIDABLE
                     | <access-spec>
    """
    subclass_names = ['Access_Spec', 'Binding_PASS_Arg_Name']
    def match(string): return STRINGBase.match(['PASS', 'NOPASS', 'NON_OVERRIDABLE'], string)
    pass

class Final_Binding(StmtBase, WORDClsBase): # R454
    """
    <final-binding> = FINAL [ :: ] <final-subroutine-name-list>
    """
    subclass_names = []
    use_names = ['Final_Subroutine_Name_List']
    def match(string): return WORDClsBase.match('FINAL',Final_Subroutine_Name_List,string,check_colons=True, require_cls=True)
    pass
    tostr = WORDClsBase.tostr_a

class Derived_Type_Spec(CallBase): # R455
    """
    <derived-type-spec> = <type-name> [ ( <type-param-spec-list> ) ]
    """
    subclass_names = ['Type_Name']
    use_names = ['Type_Param_Spec_List']
    def match(string): return CallBase.match(Type_Name, Type_Param_Spec_List, string)
    pass

class Type_Param_Spec(KeywordValueBase): # R456
    """
    <type-param-spec> = [ <keyword> = ] <type-param-value>
    """
    subclass_names = ['Type_Param_Value']
    use_names = ['Keyword']
    def match(string): return KeywordValueBase.match(Keyword, Type_Param_Value, string)
    pass

class Structure_Constructor_2(KeywordValueBase): # R457.b
    """
    <structure-constructor-2> = [ <keyword> = ] <component-data-source>
    """
    subclass_names = ['Component_Data_Source']
    use_names = ['Keyword']
    def match(string): return KeywordValueBase.match(Keyword, Component_Data_Source, string)
    pass

class Structure_Constructor(CallBase): # R457
    """
    <structure-constructor> = <derived-type-spec> ( [ <component-spec-list> ] )
                            | <structure-constructor-2>
    """
    subclass_names = ['Structure_Constructor_2']
    use_names = ['Derived_Type_Spec', 'Component_Spec_List']
    def match(string): return CallBase.match(Derived_Type_Spec, Component_Spec_List, string)
    pass

class Component_Spec(KeywordValueBase): # R458
    """
    <component-spec> = [ <keyword> = ] <component-data-source>
    """
    subclass_names = ['Component_Data_Source']
    use_names = ['Keyword']
    def match(string): return KeywordValueBase.match(Keyword, Component_Data_Source, string)
    pass

class Component_Data_Source(Base): # R459
    """
    <component-data-source> = <expr>
                              | <data-target>
                              | <proc-target>
    """
    subclass_names = ['Proc_Target', 'Data_Target', 'Expr']

class Enum_Def(Base): # R460
    """
    <enum-def> = <enum-def-stmt>
                     <enumerator-def-stmt>
                     [ <enumerator-def-stmt> ]...
                     <end-enum-stmt>
    """
    subclass_names = []
    use_names = ['Enum_Def_Stmt', 'Enumerator_Def_Stmt', 'End_Enum_Stmt']

class Enum_Def_Stmt(STRINGBase): # R461
    """
    <enum-def-stmt> = ENUM, BIND(C)
    """
    subclass_names = []
    def match(string):
        if string[:4].upper()!='ENUM': return
        line = string[4:].lstrip()
        if not line.startswith(','): return
        line = line[1:].lstrip()
        if line[:4].upper()!='BIND': return
        line = line[4:].lstrip()
        if not line or line[0]+line[-1]!='()': return
        line = line[1:-1].strip()
        if line!='C' or line!='c': return
        return 'ENUM, BIND(C)',
    pass

class Enumerator_Def_Stmt(StmtBase, WORDClsBase): # R462
    """
    <enumerator-def-stmt> = ENUMERATOR [ :: ] <enumerator-list>
    """
    subclass_names = []
    use_names = ['Enumerator_List']
    def match(string): return WORDClsBase.match('ENUMERATOR',Enumerator_List,string,check_colons=True, require_cls=True)
    pass
    tostr = WORDClsBase.tostr_a

class Enumerator(BinaryOpBase): # R463
    """
    <enumerator> = <named-constant> [ = <scalar-int-initialization-expr> ]
    """
    subclass_names = ['Named_Constant']
    use_names = ['Scalar_Int_Initialization_Expr']
    def match(string):
        if '=' not in string: return
        lhs,rhs = string.split('=',1)
        return Named_Constant(lhs.rstrip()),'=',Scalar_Int_Initialization_Expr(rhs.lstrip())
    pass

class End_Enum_Stmt(EndStmtBase): # R464
    """
    <end-enum-stmt> = END ENUM
    """
    subclass_names = []
    def match(string): return EndStmtBase.match('ENUM',None, string, requite_stmt_type=True)
    pass

class Array_Constructor(BracketBase): # R465
    """
    <array-constructor> = (/ <ac-spec> /)
                          | <left-square-bracket> <ac-spec> <right-square-bracket>

    """
    subclass_names = []
    use_names = ['Ac_Spec']
    def match(string):
        try:
            obj = BracketBase.match('(//)', Ac_Spec, string)
        except NoMatchError:
            obj = None
        if obj is None:
            obj = BracketBase.match('[]', Ac_Spec, string)
        return obj
    pass

class Ac_Spec(Base): # R466
    """
    <ac-spec> = <type-spec> ::
                | [ <type-spec> :: ] <ac-value-list>
    """
    subclass_names = ['Ac_Value_List']
    use_names = ['Type_Spec']
    def match(string):
        if string.endswith('::'):
            return Type_Spec(string[:-2].rstrip()),None
        line, repmap = string_replace_map(string)
        i = line.find('::')
        if i==-1: return
        ts = line[:i].rstrip()
        line = line[i+2:].lstrip()
        ts = repmap(ts)
        line = repmap(line)
        return Type_Spec(ts),Ac_Value_List(line)
    pass
    def tostr(self):
        if self.items[0] is None:
            return str(self.items[1])
        if self.items[1] is None:
            return str(self.items[0]) + ' ::'
        return '%s :: %s' % self.items

# R467: <left-square-bracket> = [
# R468: <right-square-bracket> = ]

class Ac_Value(Base): # R469
    """
    <ac-value> = <expr>
                 | <ac-implied-do>
    """
    subclass_names = ['Ac_Implied_Do','Expr']

class Ac_Implied_Do(Base): # R470
    """
    <ac-implied-do> = ( <ac-value-list> , <ac-implied-do-control> )
    """
    subclass_names = []
    use_names = ['Ac_Value_List','Ac_Implied_Do_Control']
    def match(string):
        if string[0]+string[-1] != '()': return
        line, repmap = string_replace_map(string[1:-1].strip())
        i = line.rfind('=')
        if i==-1: return
        j = line[:i].rfind(',')
        assert j!=-1
        s1 = repmap(line[:j].rstrip())
        s2 = repmap(line[j+1:].lstrip())
        return Ac_Value_List(s1),Ac_Implied_Do_Control(s2)
    pass
    def tostr(self): return '(%s, %s)' % tuple(self.items)

class Ac_Implied_Do_Control(Base): # R471
    """
    <ac-implied-do-control> = <ac-do-variable> = <scalar-int-expr> , <scalar-int-expr> [ , <scalar-int-expr> ]
    """
    subclass_names = []
    use_names = ['Ac_Do_Variable','Scalar_Int_Expr']
    def match(string):
        i = string.find('=')
        if i==-1: return
        s1 = string[:i].rstrip()
        line, repmap = string_replace_map(string[i+1:].lstrip())
        t = line.split(',')
        if not (2<=len(t)<=3): return
        t = [Scalar_Int_Expr(s.strip()) for s in t]
        return Ac_Do_Variable(s1), t
    pass
    def tostr(self): return '%s = %s' % (self.items[0], ', '.join(map(str,self.items[1])))

class Ac_Do_Variable(Base): # R472
    """
    <ac-do-variable> = <scalar-int-variable>
    <ac-do-variable> shall be a named variable
    """
    subclass_names = ['Scalar_Int_Variable']

###############################################################################
############################### SECTION  5 ####################################
###############################################################################

class Type_Declaration_Stmt(Base): # R501
    """
    <type-declaration-stmt> = <declaration-type-spec> [ [ , <attr-spec> ]... :: ] <entity-decl-list>
    """
    subclass_names = []
    use_names = ['Declaration_Type_Spec', 'Attr_Spec_List', 'Entity_Decl_List']

    def match(string):
        line, repmap = string_replace_map(string)
        i = line.find('::')
        if i!=-1:
            j = line[:i].find(',')
            if j!=-1:
                i = j
        else:
            if line[:6].upper()=='DOUBLE':
                m = re.search(r'\s[a-z_]',line[6:].lstrip())
                if m is None: return
                i = m.start() + len(line)-len(line[6:].lstrip())
            else:
                m = re.search(r'\s[a-z_]',line)
                if m is None: return
                i = m.start()
        type_spec = Declaration_Type_Spec(repmap(line[:i].rstrip()))
        if type_spec is None: return
        line = line[i:].lstrip()
        if line.startswith(','):
            i = line.find('::')
            if i==-1: return
            attr_specs = Attr_Spec_List(repmap(line[1:i].strip()))
            if attr_specs is None: return
            line = line[i:]
        else:
            attr_specs = None
        if line.startswith('::'):
            line = line[2:].lstrip()
        entity_decls = Entity_Decl_List(repmap(line))
        if entity_decls is None: return
        return type_spec, attr_specs, entity_decls
    pass
    def tostr(self):
        if self.items[1] is None:
            return '%s :: %s' % (self.items[0], self.items[2])
        else:
            return '%s, %s :: %s' % self.items

class Declaration_Type_Spec(Base): # R502
    """
    <declaration-type-spec> = <intrinsic-type-spec>
                              | TYPE ( <derived-type-spec> )
                              | CLASS ( <derived-type-spec> )
                              | CLASS ( * )
    """
    subclass_names = ['Intrinsic_Type_Spec']
    use_names = ['Derived_Type_Spec']

    def match(string):
        if string[-1] != ')': return
        start = string[:4].upper()
        if start == 'TYPE':
            line = string[4:].lstrip()
            if not line.startswith('('): return
            return 'TYPE',Derived_Type_Spec(line[1:-1].strip())
        start = string[:5].upper()
        if start == 'CLASS':
            line = string[5:].lstrip()
            if not line.startswith('('): return
            line = line[1:-1].strip()
            if line=='*': return 'CLASS','*'
            return 'CLASS', Derived_Type_Spec(line)
        return
    pass
    def tostr(self): return '%s(%s)' % self.items

class Dimension_Attr_Spec(CALLBase): # R503.d
    """
    <dimension-attr-spec> = DIMENSION ( <array-spec> )
    """
    subclass_names = []
    use_names = ['Array_Spec']
    def match(string): return CALLBase.match('DIMENSION', Array_Spec, string)
    pass

class Intent_Attr_Spec(CALLBase): # R503.f
    """
    <intent-attr-spec> = INTENT ( <intent-spec> )
    """
    subclass_names = []
    use_names = ['Intent_Spec']
    def match(string): return CALLBase.match('INTENT', Intent_Spec, string)
    pass

class Attr_Spec(STRINGBase): # R503
    """
    <attr-spec> = <access-spec>
                  | ALLOCATABLE
                  | ASYNCHRONOUS
                  | DIMENSION ( <array-spec> )
                  | EXTERNAL
                  | INTENT ( <intent-spec> )
                  | INTRINSIC
                  | <language-binding-spec>
                  | OPTIONAL
                  | PARAMETER
                  | POINTER
                  | PROTECTED
                  | SAVE
                  | TARGET
                  | VALUE
                  | VOLATILE
    """
    subclass_names = ['Access_Spec', 'Language_Binding_Spec',
                      'Dimension_Attr_Spec', 'Intent_Attr_Spec']
    use_names = []
    def match(string): return STRINGBase.match(pattern.abs_attr_spec, string)
    pass

class Entity_Decl(Base): # R504
    """
    <entity-decl> = <object-name> [ ( <array-spec> ) ] [ * <char-length> ] [ <initialization> ]
                    | <function-name> [ * <char-length> ]
    """
    subclass_names = []
    use_names = ['Object_Name', 'Array_Spec', 'Char_Length', 'Initialization', 'Function_Name']
    def match(string):
        m = pattern.name.match(string)
        if m is None: return
        name = Name(m.group())
        newline = string[m.end():].lstrip()
        if not newline: return name, None, None, None
        array_spec = None
        char_length = None
        init = None
        if newline.startswith('('):
            line, repmap = string_replace_map(newline)
            i = line.find(')')
            if i==-1: return
            array_spec = Array_Spec(repmap(line[1:i].strip()))
            newline = repmap(line[i+1:].lstrip())
        if newline.startswith('*'):
            line, repmap = string_replace_map(newline)
            i = line.find('=')
            if i!=-1:
                char_length = repmap(line[1:i].strip())
                newline = repmap(newline[i:].lstrip())
            else:
                char_length = repmap(newline[1:].strip())
                newline = ''
            char_length = Char_Length(char_length)
        if newline.startswith('='):
            init = Initialization(newline)
        else:
            assert newline=='',`newline`
        return name, array_spec, char_length, init
    pass
    def tostr(self):
        s = str(self.items[0])
        if self.items[1] is not None:
            s += '(' + str(self.items[1]) + ')'
        if self.items[2] is not None:
            s += '*' + str(self.items[2])
        if self.items[3] is not None:
            s += ' ' + str(self.items[3])
        return s

class Object_Name(Base): # R505
    """
    <object-name> = <name>
    """
    subclass_names = ['Name']

class Initialization(Base): # R506
    """
    <initialization> =  = <initialization-expr>
                       | => <null-init>
    """
    subclass_names = []
    use_names = ['Initialization_Expr', 'Null_Init']
    def match(string):
        if string.startswith('=>'):
            return '=>', Null_Init(string[2:].lstrip())
        if string.startswith('='):
            return '=', Initialization_Expr(string[2:].lstrip())
        return
    pass
    def tostr(self): return '%s %s' % self.items

class Null_Init(STRINGBase): # R507
    """
    <null-init> = <function-reference>

    <function-reference> shall be a reference to the NULL intrinsic function with no arguments.
    """
    subclass_names = ['Function_Reference']
    def match(string): return STRINGBase.match('NULL', string)
    pass

class Access_Spec(STRINGBase): # R508
    """
    <access-spec> = PUBLIC
                    | PRIVATE
    """
    subclass_names = []
    def match(string): return STRINGBase.match(['PUBLIC','PRIVATE'], string)
    pass

class Language_Binding_Spec(Base): # R509
    """
    <language-binding-spec> = BIND ( C [ , NAME = <scalar-char-initialization-expr> ] )
    """
    subclass_names = []
    use_names = ['Scalar_Char_Initialization_Expr']
    def match(string):
        start = string[:4].upper()
        if start != 'BIND': return
        line = string[4:].lstrip()
        if not line or line[0]+line[-1]!='()': return
        line = line[1:-1].strip()
        if not line: return
        start = line[0].upper()
        if start!='C': return
        line = line[1:].lstrip()
        if not line: return None,
        if not line.startswith(','): return
        line = line[1:].lstrip()
        start = line[:4].upper()
        if start!='NAME': return
        line=line[4:].lstrip()
        if not line.startswith('='): return
        return Scalar_Char_Initialization_Expr(line[1:].lstrip()),
    pass
    def tostr(self):
        if self.items[0] is None: return 'BIND(C)'
        return 'BIND(C, NAME = %s)' % (self.items[0])

class Array_Spec(Base): # R510
    """
    <array-spec> = <explicit-shape-spec-list>
                   | <assumed-shape-spec-list>
                   | <deferred-shape-spec-list>
                   | <assumed-size-spec>
    """
    subclass_names = ['Assumed_Size_Spec', 'Explicit_Shape_Spec_List', 'Assumed_Shape_Spec_List',
                      'Deferred_Shape_Spec_List']

class Explicit_Shape_Spec(SeparatorBase): # R511
    """
    <explicit-shape-spec> = [ <lower-bound> : ] <upper-bound>
    """
    subclass_names = []
    use_names = ['Lower_Bound', 'Upper_Bound']
    def match(string):
        line, repmap = string_replace_map(string)
        if ':' not in line:
            return None, Upper_Bound(string)
        lower,upper = line.split(':',1)
        lower = lower.rstrip()
        upper = upper.lstrip()
        if not upper: return
        if not lower: return
        return Lower_Bound(repmap(lower)), Upper_Bound(repmap(upper))
    pass
    def tostr(self):
        if self.items[0] is None: return str(self.items[1])
        return SeparatorBase.tostr(self)

class Lower_Bound(Base): # R512
    """
    <lower-bound> = <specification-expr>
    """
    subclass_names = ['Specification_Expr']

class Upper_Bound(Base): # R513
    """
    <upper-bound> = <specification-expr>
    """
    subclass_names = ['Specification_Expr']

class Assumed_Shape_Spec(SeparatorBase): # R514
    """
    <assumed-shape-spec> = [ <lower-bound> ] :
    """
    subclass_names = []
    use_names = ['Lower_Bound']
    def match(string): return SeparatorBase.match(Lower_Bound, None, string)
    pass

class Deferred_Shape_Spec(SeparatorBase): # R515
    """
    <deferred_shape_spec> = :
    """
    subclass_names = []
    def match(string):
        if string==':': return None,None
        return
    pass

class Assumed_Size_Spec(Base): # R516
    """
    <assumed-size-spec> = [ <explicit-shape-spec-list> , ] [ <lower-bound> : ] *
    """
    subclass_names = []
    use_names = ['Explicit_Shape_Spec_List', 'Lower_Bound']
    def match(string):
        if not string.endswith('*'): return
        line = string[:-1].rstrip()
        if not line: return None,None
        if line.endswith(':'):
            line, repmap = string_replace_map(line[:-1].rstrip())
            i = line.rfind(',')
            if i==-1:
                return None, Lower_Bound(repmap(line))
            return Explicit_Shape_Spec_List(repmap(line[:i].rstrip())), Lower_Bound(repmap(line[i+1:].lstrip()))
        if not line.endswith(','): return
        line = line[:-1].rstrip()
        return Explicit_Shape_Spec_List(line), None
    pass
    def tostr(self):
        s = ''
        if self.items[0] is not None:
            s += str(self.items[0]) + ', '
        if self.items[1] is not None:
            s += str(self.items[1]) + ' : '
        s += '*'
        return s

class Intent_Spec(STRINGBase): # R517
    """
    <intent-spec> = IN
                    | OUT
                    | INOUT
    """
    subclass_names = []
    def match(string): return STRINGBase.match(pattern.abs_intent_spec, string)
    pass

class Access_Stmt(StmtBase, WORDClsBase): # R518
    """
    <access-stmt> = <access-spec> [ [ :: ] <access-id-list> ]
    """
    subclass_names = []
    use_names = ['Access_Spec', 'Access_Id_List']
    def match(string): return WORDClsBase.match(['PUBLIC', 'PRIVATE'],Access_Id_List,string,check_colons=True, require_cls=False)
    pass
    tostr = WORDClsBase.tostr_a

class Access_Id(Base): # R519
    """
    <access-id> = <use-name>
                  | <generic-spec>
    """
    subclass_names = ['Use_Name', 'Generic_Spec']

class Object_Name_Deferred_Shape_Spec_List_Item(CallBase):
    """
    <..> =  <object-name> [ ( <deferred-shape-spec-list> ) ]
    """
    subclass_names = ['Object_Name']
    use_names = ['Deferred_Shape_Spec_List']
    def match(string): return CallBase.match(Object_Name, Deferred_Shape_Spec_List, string, require_rhs=True)
    pass

class Allocatable_Stmt(StmtBase, WORDClsBase): # R520
    """
    <allocateble-stmt> = ALLOCATABLE [ :: ] <object-name> [ ( <deferred-shape-spec-list> ) ] [ , <object-name> [ ( <deferred-shape-spec-list> ) ] ]...
    """
    subclass_names = []
    use_names = ['Object_Name_Deferred_Shape_Spec_List_Item_List']
    def match(string):
        return WORDClsBase.match('ALLOCATABLE', Object_Name_Deferred_Shape_Spec_List_Item_List, string,
                                 check_colons=True, require_cls=True)
    pass

class Asynchronous_Stmt(StmtBase, WORDClsBase): # R521
    """
    <asynchronous-stmt> = ASYNCHRONOUS [ :: ] <object-name-list>
    """
    subclass_names = []
    use_names = ['Object_Name_List']
    def match(string): return WORDClsBase.match('ASYNCHRONOUS',Object_Name_List,string,check_colons=True, require_cls=True)
    pass


class Bind_Stmt(StmtBase): # R522
    """
    <bind-stmt> = <language-binding-spec> [ :: ] <bind-entity-list>
    """
    subclass_names = []
    use_names = ['Language_Binding_Spec', 'Bind_Entity_List']
    def match(string):
        i = string.find('::')
        if i==-1:
            i = string.find(')')
            if i==-1: return
            lhs. rhs = string[:i], string[i+1:]
        else:
            lhs, rhs = string.split('::',1)
        lhs = lhs.rstrip()
        rhs = rhs.lstrip()
        if not lhs or not rhs: return
        return Language_Binding_Spec(lhs), Bind_Entity_List(rhs)
    pass
    def tostr(self):
        return '%s :: %s' % self.items


class Bind_Entity(BracketBase): # R523
    """
    <bind-entity> = <entity-name>
                    | / <common-block-name> /
    """
    subclass_names = ['Entity_Name']
    use_names = ['Common_Block_Name']
    def match(string): return BracketBase.match('//',Common_Block_Name, string)
    pass

class Data_Stmt(StmtBase): # R524
    """
    <data-stmt> = DATA <data-stmt-set> [ [ , ] <data-stmt-set> ]...
    """
    subclass_names = []
    use_names = ['Data_Stmt_Set']

class Data_Stmt_Set(Base): # R525
    """
    <data-stmt-set> = <data-stmt-object-list> / <data-stmt-value-list> /
    """
    subclass_names = []
    use_names = ['Data_Stmt_Object_List', 'Data_Stmt_Value_List']

class Data_Stmt_Object(Base): # R526
    """
    <data-stmt-object> = <variable>
                         | <data-implied-do>
    """
    subclass_names = ['Variable', 'Data_Implied_Do']

class Data_Implied_Do(Base): # R527
    """
    <data-implied-do> = ( <data-i-do-object-list> , <data-i-do-variable> = <scalar-int-expr > , <scalar-int-expr> [ , <scalar-int-expr> ] )
    """
    subclass_names = []
    use_names = ['Data_I_Do_Object_List', 'Data_I_Do_Variable', 'Scalar_Int_Expr']

class Data_I_Do_Object(Base): # R528
    """
    <data-i-do-object> = <array-element>
                         | <scalar-structure-component>
                         | <data-implied-do>
    """
    subclass_names = ['Array_Element', 'Scalar_Structure_Component', 'Data_Implied_Do']

class Data_I_Do_Variable(Base): # R529
    """
    <data-i-do-variable> = <scalar-int-variable>
    """
    subclass_names = ['Scalar_Int_Variable']

class Data_Stmt_Value(Base): # R530
    """
    <data-stmt-value> = [ <data-stmt-repeat> * ] <data-stmt-constant>
    """
    subclass_names = ['Data_Stmt_Constant']
    use_names = ['Data_Stmt_Repeat']
    def match(string):
        line, repmap = string_replace_map(string)
        s = line.split('*')
        if len(s)!=2: return
        lhs = repmap(s[0].rstrip())
        rhs = repmap(s[1].lstrip())
        if not lhs or not rhs: return
        return Data_Stmt_Repeat(lhs), Data_Stmt_Constant(rhs)
    pass
    def tostr(self):
        return '%s * %s' % self.items

class Data_Stmt_Repeat(Base): # R531
    """
    <data-stmt-repeat> = <scalar-int-constant>
                         | <scalar-int-constant-subobject>
    """
    subclass_names = ['Scalar_Int_Constant', 'Scalar_Int_Constant_Subobject']

class Data_Stmt_Constant(Base): # R532
    """
    <data-stmt-constant> = <scalar-constant>
                           | <scalar-constant-subobject>
                           | <signed-int-literal-constant>
                           | <signed-real-literal-constant>
                           | <null-init>
                           | <structure-constructor>
    """
    subclass_names = ['Scalar_Constant', 'Scalar_Constant_Subobject',
                      'Signed_Int_Literal_Constant', 'Signed_Real_Literal_Constant',
                      'Null_Init', 'Structure_Constructor']

class Int_Constant_Subobject(Base): # R533
    """
    <int-constant-subobject> = <constant-subobject>
    """
    subclass_names = ['Constant_Subobject']

class Constant_Subobject(Base): # R534
    """
    <constant-subobject> = <designator>
    """
    subclass_names = ['Designator']

class Dimension_Stmt(StmtBase): # R535
    """
    <dimension-stmt> = DIMENSION [ :: ] <array-name> ( <array-spec> ) [ , <array-name> ( <array-spec> ) ]...
    """
    subclass_names = []
    use_names = ['Array_Name', 'Array_Spec']
    def match(string):
        if string[:9].upper()!='DIMENSION': return
        line, repmap = string_replace_map(string[9:].lstrip())
        if line.startswith('::'): line = line[2:].lstrip()
        decls = []
        for s in line.split(','):
            s = s.strip()
            if not s.endswith(')'): return
            i = s.find('(')
            if i==-1: return
            decls.append((Array_Name(repmap(s[:i].rstrip())), Array_Spec(repmap(s[i+1:-1].strip()))))
        if not decls: return
        return decls,
    pass
    def tostr(self):
        return 'DIMENSION :: ' + ', '.join(['%s(%s)' % ns for ns in self.items[0]])

class Intent_Stmt(StmtBase): # R536
    """
    <intent-stmt> = INTENT ( <intent-spec> ) [ :: ] <dummy-arg-name-list>
    """
    subclass_names = []
    use_names = ['Intent_Spec', 'Dummy_Arg_Name_List']
    def match(string):
        if string[:6].upper()!='INTENT': return
        line = string[6:].lstrip()
        if not line or not line.startswith('('): return
        i = line.rfind(')')
        if i==-1: return
        spec = line[1:i].strip()
        if not spec: return
        line = line[i+1:].lstrip()
        if line.startswith('::'):
            line = line[2:].lstrip()
        if not line: return
        return Intent_Spec(spec), Dummy_Arg_Name_List(line)
    pass
    def tostr(self):
        return 'INTENT(%s) :: %s' % self.items

class Optional_Stmt(StmtBase, WORDClsBase): # R537
    """
    <optional-stmt> = OPTIONAL [ :: ] <dummy-arg-name-list>
    """
    subclass_names = []
    use_names = ['Dummy_Arg_Name_List']
    def match(string): return WORDClsBase.match('OPTIONAL',Dummy_Arg_Name_List,string,check_colons=True, require_cls=True)
    pass
    tostr = WORDClsBase.tostr_a

class Parameter_Stmt(StmtBase, CALLBase): # R538
    """
    <parameter-stmt> = PARAMETER ( <named-constant-def-list> )
    """
    subclass_names = []
    use_names = ['Named_Constant_Def_List']
    def match(string): return CALLBase.match('PARAMETER', Named_Constant_Def_List, string, require_rhs=True)
    pass

class Named_Constant_Def(KeywordValueBase): # R539
    """
    <named-constant-def> = <named-constant> = <initialization-expr>
    """
    subclass_names = []
    use_names = ['Named_Constant', 'Initialization_Expr']
    def match(string): return KeywordValueBase.match(Named_Constant, Initialization_Expr, string)
    pass

class Pointer_Stmt(StmtBase, WORDClsBase): # R540
    """
    <pointer-stmt> = POINTER [ :: ] <pointer-decl-list>
    """
    subclass_names = []
    use_names = ['Pointer_Decl_List']
    def match(string): return WORDClsBase.match('POINTER',Pointer_Decl_List,string,check_colons=True, require_cls=True)
    pass
    tostr = WORDClsBase.tostr_a

class Pointer_Decl(CallBase): # R541
    """
    <pointer-decl> = <object-name> [ ( <deferred-shape-spec-list> ) ]
                     | <proc-entity-name>
    """
    subclass_names = ['Proc_Entity_Name', 'Object_Name']
    use_names = ['Deferred_Shape_Spec_List']
    def match(string): return CallBase.match(Object_Name, Deferred_Shape_Spec_List, string, require_rhs=True)
    pass

class Protected_Stmt(StmtBase, WORDClsBase): # R542
    """
    <protected-stmt> = PROTECTED [ :: ] <entity-name-list>
    """
    subclass_names = []
    use_names = ['Entity_Name_List']
    def match(string): return WORDClsBase.match('PROTECTED',Entity_Name_List,string,check_colons=True, require_cls=True)
    pass
    tostr = WORDClsBase.tostr_a

class Save_Stmt(StmtBase, WORDClsBase): # R543
    """
    <save-stmt> = SAVE [ [ :: ] <saved-entity-list> ]
    """
    subclass_names = []
    use_names = ['Saved_Entity_List']
    def match(string): return WORDClsBase.match('SAVE',Saved_Entity_List,string,check_colons=True, require_cls=False)
    pass
    tostr = WORDClsBase.tostr_a

class Saved_Entity(BracketBase): # R544
    """
    <saved-entity> = <object-name>
                     | <proc-pointer-name>
                     | / <common-block-name> /
    """
    subclass_names = ['Object_Name', 'Proc_Pointer_Name']
    use_names = ['Common_Block_Name']
    def match(string): return BracketBase.match('//',CommonBlockName, string)
    pass

class Proc_Pointer_Name(Base): # R545
    """
    <proc-pointer-name> = <name>
    """
    subclass_names = ['Name']

class Target_Stmt(StmtBase): # R546
    """
    <target-stmt> = TARGET [ :: ] <object-name> [ ( <array-spec> ) ] [ , <object-name> [ ( <array-spec> ) ] ]...
    """
    subclass_names = []
    use_names = ['Object_Name', 'Array_Spec']

class Value_Stmt(StmtBase, WORDClsBase): # R547
    """
    <value-stmt> = VALUE [ :: ] <dummy-arg-name-list>
    """
    subclass_names = []
    use_names = ['Dummy_Arg_Name_List']
    def match(string): return WORDClsBase.match('VALUE',Dummy_Arg_Name_List,string,check_colons=True, require_cls=True)
    pass
    tostr = WORDClsBase.tostr_a

class Volatile_Stmt(StmtBase, WORDClsBase): # R548
    """
    <volatile-stmt> = VOLATILE [ :: ] <object-name-list>
    """
    subclass_names = []
    use_names = ['Object_Name_List']
    def match(string): return WORDClsBase.match('VOLATILE',Object_Name_List,string,check_colons=True, require_cls=True)
    pass
    tostr = WORDClsBase.tostr_a

class Implicit_Stmt(StmtBase, WORDClsBase): # R549
    """
    <implicit-stmt> = IMPLICIT <implicit-spec-list>
                      | IMPLICIT NONE
    """
    subclass_names = []
    use_names = ['Implicit_Spec_List']
    def match(string):
        for w,cls in [(pattern.abs_implicit_none, None),
                      ('IMPLICIT', Implicit_Spec_List)]:
            try:
                obj = WORDClsBase.match(w, cls, string)
            except NoMatchError:
                obj = None
            if obj is not None: return obj
        return
    pass

class Implicit_Spec(CallBase): # R550
    """
    <implicit-spec> = <declaration-type-spec> ( <letter-spec-list> )
    """
    subclass_names = []
    use_names = ['Declaration_Type_Spec', 'Letter_Spec_List']
    def match(string):
        if not string.endswith(')'): return
        i = string.rfind('(')
        if i==-1: return
        s1 = string[:i].rstrip()
        s2 = string[i+1:-1].strip()
        if not s1 or not s2: return
        return Declaration_Type_Spec(s1), Letter_Spec_List(s2)
    pass

class Letter_Spec(Base): # R551
    """
    <letter-spec> = <letter> [ - <letter> ]
    """
    subclass_names = []
    def match(string):
        if len(string)==1:
            lhs = string.upper()
            if 'A'<=lhs<='Z': return lhs, None
            return
        if '-' not in string: return
        lhs,rhs = string.split('-',1)
        lhs = lhs.strip().upper()
        rhs = rhs.strip().upper()
        if not len(lhs)==len(rhs)==1: return
        if not ('A'<=lhs<=rhs<='Z'): return
        return lhs,rhs
    pass
    def tostr(self):
        if self.items[1] is None: return str(self.items[0])
        return '%s - %s' % tuple(self.items)

class Namelist_Stmt(StmtBase): # R552
    """
    <namelist-stmt> = NAMELIST / <namelist-group-name> / <namelist-group-object-list> [ [ , ] / <namelist-group-name> / <namelist-group-object-list> ]
    """
    subclass_names = []
    use_names = ['Namelist_Group_Name', 'Namelist_Group_Object_List']

class Namelist_Group_Object(Base): # R553
    """
    <namelist-group-object> = <variable-name>
    """
    subclass_names = ['Variable_Name']

class Equivalence_Stmt(StmtBase, WORDClsBase): # R554
    """
    <equivalence-stmt> = EQUIVALENCE <equivalence-set-list>
    """
    subclass_names = []
    use_names = ['Equivalence_Set_List']
    def match(string): return WORDClsBase.match('EQUIVALENCE', Equivalence_Set_List, string)
    pass

class Equivalence_Set(Base): # R555
    """
    <equivalence-set> = ( <equivalence-object> , <equivalence-object-list> )
    """
    subclass_names = []
    use_names = ['Equivalence_Object', 'Equivalence_Object_List']
    def match(string):
        if not string or string[0]+string[-1]!='()': return
        line = string[1:-1].strip()
        if not line: return
        l = Equivalence_Object_List(line)
        obj = l.items[0]
        l.items = l.items[1:]
        if not l.items: return
        return obj, l
    pass
    def tostr(self): return '(%s, %s)' % tuple(self.items)

class Equivalence_Object(Base): # R556
    """
    <equivalence-object> = <variable-name>
                           | <array-element>
                           | <substring>
    """
    subclass_names = ['Variable_Name', 'Array_Element', 'Substring']

class Common_Stmt(StmtBase): # R557
    """
    <common-stmt> = COMMON [ / [ <common-block-name> ] / ] <common-block-object-list> [ [ , ] / [ <common-block-name> ] / <common-block-object-list> ]...
    """
    subclass_names = []
    use_names = ['Common_Block_Name', 'Common_Block_Object_List']
    def match(string):
        if string[:6].upper()!='COMMON': return
        line = string[6:]
        if not line or 'A'<=line[0].upper()<='Z' or line[0]=='_': return
        line, repmap = string_replace_map(line.lstrip())
        items = []
        if line.startswith('/'):
            i = line.find('/',1)
            if i==-1: return
            name = line[1:i].strip() or None
            if name is not None: name = Common_Block_Name(name)
            line = line[i+1:].lstrip()
            i = line.find('/')
            if i==-1:
                lst = Common_Block_Object_List(repmap(line))
                line = ''
            else:
                l = line[:i].rstrip()
                if l.endswith(','): l = l[:-1].rstrip()
                if not l: return
                lst = Common_Block_Object_List(repmap(l))
                line = line[i:].lstrip()
        else:
            name = None
            i = line.find('/')
            if i==-1:
                lst = Common_Block_Object_List(repmap(line))
                line = ''
            else:
                l = line[:i].rstrip()
                if l.endswith(','): l = l[:-1].rstrip()
                if not l: return
                lst = Common_Block_Object_List(repmap(l))
                line = line[i:].lstrip()
        items.append((name, lst))
        while line:
            if line.startswith(','): line = line[1:].lstrip()
            if not line.startswith('/'): return
            i = line.find('/',1)
            name = line[1:i].strip() or None
            if name is not None: name = Common_Block_Name(name)
            line = line[i+1:].lstrip()
            i = line.find('/')
            if i==-1:
                lst = Common_Block_Object_List(repmap(line))
                line = ''
            else:
                l = line[:i].rstrip()
                if l.endswith(','): l = l[:-1].rstrip()
                if not l: return
                lst = Common_Block_Object_List(repmap(l))
                line = line[i:].lstrip()
            items.append((name, lst))
        return items,
    pass
    def tostr(self):
        s = 'COMMON'
        for (name, lst) in self.items[0]:
            if name is not None:
                s += ' /%s/ %s' % (name, lst)
            else:
                s += ' // %s' % (lst)
        return s

class Common_Block_Object(CallBase): # R558
    """
    <common-block-object> = <variable-name> [ ( <explicit-shape-spec-list> ) ]
                            | <proc-pointer-name>
    """
    subclass_names = ['Proc_Pointer_Name','Variable_Name']
    use_names = ['Variable_Name', 'Explicit_Shape_Spec_List']
    def match(string): return CallBase.match(Variable_Name, Explicit_Shape_Spec_List, string, require_rhs=True)
    pass

###############################################################################
############################### SECTION  6 ####################################
###############################################################################

class Variable(Base): # R601
    """
    <variable> = <designator>
    """
    subclass_names = ['Designator']

class Variable_Name(Base): # R602
    """
    <variable-name> = <name>
    """
    subclass_names = ['Name']

class Designator(Base): # R603
    """
    <designator> = <object-name>
                   | <array-element>
                   | <array-section>
                   | <structure-component>
                   | <substring>
    <substring-range> = [ <scalar-int-expr> ] : [ <scalar-int-expr> ]
    <structure-component> = <data-ref>
    """
    subclass_names = ['Object_Name','Array_Section','Array_Element','Structure_Component',
                      'Substring'
                      ]

class Logical_Variable(Base): # R604
    """
    <logical-variable> = <variable>
    """
    subclass_names = ['Variable']

class Default_Logical_Variable(Base): # R605
    """
    <default-logical-variable> = <variable>
    """
    subclass_names = ['Variable']

class Char_Variable(Base): # R606
    """
    <char-variable> = <variable>
    """
    subclass_names = ['Variable']

class Default_Char_Variable(Base): # R607
    """
    <default-char-variable> = <variable>
    """
    subclass_names = ['Variable']


class Int_Variable(Base): # R608
    """
    <int-variable> = <variable>
    """
    subclass_names = ['Variable']


class Substring(CallBase): # R609
    """
    <substring> = <parent-string> ( <substring-range> )
    """
    subclass_names = []
    use_names = ['Parent_String','Substring_Range']
    def match(string): return CallBase.match(Parent_String, Substring_Range, string, require_rhs=True)
    pass

class Parent_String(Base): # R610
    """
    <parent-string> = <scalar-variable-name>
                      | <array-element>
                      | <scalar-structure-component>
                      | <scalar-constant>
    """
    subclass_names = ['Scalar_Variable_Name', 'Array_Element', 'Scalar_Structure_Component', 'Scalar_Constant']

class Substring_Range(SeparatorBase): # R611
    """
    <substring-range> = [ <scalar-int-expr> ] : [ <scalar-int-expr> ]
    """
    subclass_names = []
    use_names = ['Scalar_Int_Expr']
    def match(string):
        return SeparatorBase.match(Scalar_Int_Expr, Scalar_Int_Expr, string)
    pass

class Data_Ref(SequenceBase): # R612
    """
    <data-ref> = <part-ref> [ % <part-ref> ]...
    """
    subclass_names = ['Part_Ref']
    use_names = []
    def match(string): return SequenceBase.match(r'%', Part_Ref, string)
    pass

class Part_Ref(CallBase): # R613
    """
    <part-ref> = <part-name> [ ( <section-subscript-list> ) ]
    """
    subclass_names = ['Part_Name']
    use_names = ['Section_Subscript_List']
    def match(string):
        return CallBase.match(Part_Name, Section_Subscript_List, string, require_rhs=True)
    pass

class Structure_Component(Base): # R614
    """
    <structure-component> = <data-ref>
    """
    subclass_names = ['Data_Ref']

class Type_Param_Inquiry(BinaryOpBase): # R615
    """
    <type-param-inquiry> = <designator> % <type-param-name>
    """
    subclass_names = []
    use_names = ['Designator','Type_Param_Name']
    def match(string):
        return BinaryOpBase.match(\
            Designator, pattern.percent_op.named(), Type_Param_Name, string)
    pass

class Array_Element(Base): # R616
    """
    <array-element> = <data-ref>
    """
    subclass_names = ['Data_Ref']

class Array_Section(CallBase): # R617
    """
    <array-section> = <data-ref> [ ( <substring-range> ) ]
    """
    subclass_names = ['Data_Ref']
    use_names = ['Substring_Range']
    def match(string): return CallBase.match(Data_Ref, Substring_Range, string, require_rhs=True)
    pass

class Subscript(Base): # R618
    """
    <subscript> = <scalar-int-expr>
    """
    subclass_names = ['Scalar_Int_Expr']

class Section_Subscript(Base): # R619
    """
    <section-subscript> = <subscript>
                          | <subscript-triplet>
                          | <vector-subscript>
    """
    subclass_names = ['Subscript_Triplet', 'Vector_Subscript', 'Subscript']

class Subscript_Triplet(Base): # R620
    """
    <subscript-triplet> = [ <subscript> ] : [ <subscript> ] [ : <stride> ]
    """
    subclass_names = []
    use_names = ['Subscript','Stride']
    def match(string):
        line, repmap = string_replace_map(string)
        t = line.split(':')
        if len(t)<=1 or len(t)>3: return
        lhs_obj,rhs_obj, stride_obj = None, None, None
        if len(t)==2:
            lhs,rhs = t[0].rstrip(),t[1].lstrip()
        else:
            lhs,rhs,stride = t[0].rstrip(),t[1].strip(),t[2].lstrip()
            if stride:
                stride_obj = Stride(repmap(stride))
        if lhs:
            lhs_obj = Subscript(repmap(lhs))
        if rhs:
            rhs_obj = Subscript(repmap(rhs))
        return lhs_obj, rhs_obj, stride_obj
    pass
    def tostr(self):
        s = ''
        if self.items[0] is not None:
            s += str(self.items[0]) + ' :'
        else:
            s += ':'
        if self.items[1] is not None:
            s += ' ' + str(self.items[1])
        if self.items[2] is not None:
            s += ' : ' + str(self.items[2])
        return s

class Stride(Base): # R621
    """
    <stride> = <scalar-int-expr>
    """
    subclass_names = ['Scalar_Int_Expr']

class Vector_Subscript(Base): # R622
    """
    <vector-subscript> = <int-expr>
    """
    subclass_names = ['Int_Expr']

class Allocate_Stmt(StmtBase): # R623
    """
    <allocate-stmt> = ALLOCATE ( [ <type-spec> :: ] <allocation-list> [ , <alloc-opt-list> ] )
    """
    subclass_names = []
    use_names = ['Type_Spec', 'Allocation_List', 'Alloc_Opt_List']

class Alloc_Opt(KeywordValueBase):# R624
    """
    <alloc-opt> = STAT = <stat-variable>
                  | ERRMSG = <errmsg-variable>
                  | SOURCE = <source-expr>
    """
    subclass_names = []
    use_names = ['Stat_Variable', 'Errmsg_Variable', 'Source_Expr']
    def match(string):
        for (k,v) in [('STAT', Stat_Variable),
                      ('ERRMSG', Errmsg_Variable),
                      ('SOURCE', Source_Expr)
                      ]:
            try:
                obj = KeywordValueBase.match(k, v, string, upper_lhs = True)
            except NoMatchError:
                obj = None
            if obj is not None: return obj
        return
    pass


class Stat_Variable(Base):# R625
    """
    <stat-variable> = <scalar-int-variable>
    """
    subclass_names = ['Scalar_Int_Variable']

class Errmsg_Variable(Base):# R626
    """
    <errmsg-variable> = <scalar-default-char-variable>
    """
    subclass_names = ['Scalar_Default_Char_Variable']

class Source_Expr(Base):# R627
    """
    <source-expr> = <expr>
    """
    subclass_names = ['Expr']

class Allocation(CallBase):# R628
    """
    <allocation> = <allocate-object> [ ( <allocate-shape-spec-list> ) ]
                 | <variable-name>
    """
    subclass_names = ['Variable_Name', 'Allocate_Object']
    use_names = ['Allocate_Shape_Spec_List']
    def match(string):
        return CallBase.match(Allocate_Object, Allocate_Shape_Spec_List, string, require_rhs = True)
    pass

class Allocate_Object(Base): # R629
    """
    <allocate-object> = <variable-name>
                        | <structure-component>
    """
    subclass_names = ['Variable_Name', 'Structure_Component']

class Allocate_Shape_Spec(SeparatorBase): # R630
    """
    <allocate-shape-spec> = [ <lower-bound-expr> : ] <upper-bound-expr>
    """
    subclass_names = []
    use_names = ['Lower_Bound_Expr', 'Upper_Bound_Expr']
    def match(string):
        line, repmap = string_replace_map(string)
        if ':' not in line: return None, Upper_Bound_Expr(string)
        lower,upper = line.split(':',1)
        lower = lower.rstrip()
        upper = upper.lstrip()
        if not upper: return
        if not lower: return
        return Lower_Bound_Expr(repmap(lower)), Upper_Bound_Expr(repmap(upper))
    pass
    def tostr(self):
        if self.items[0] is None: return str(self.items[1])
        return SeparatorBase.tostr(self)


class Lower_Bound_Expr(Base): # R631
    """
    <lower-bound-expr> = <scalar-int-expr>
    """
    subclass_names = ['Scalar_Int_Expr']

class Upper_Bound_Expr(Base): # R632
    """
    <upper-bound-expr> = <scalar-int-expr>
    """
    subclass_names = ['Scalar_Int_Expr']

class Nullify_Stmt(StmtBase, CALLBase): # R633
    """
    <nullify-stmt> = NULLIFY ( <pointer-object-list> )
    """
    subclass_names = []
    use_names = ['Pointer_Object_List']
    def match(string): return CALLBase.match('NULLIFY', Pointer_Object_List, string, require_rhs=True)
    pass

class Pointer_Object(Base): # R634
    """
    <pointer-object> = <variable-name>
                       | <structure-component>
                       | <proc-pointer-name>
    """
    subclass_names = ['Variable_Name', 'Structure_Component', 'Proc_Pointer_Name']

class Deallocate_Stmt(StmtBase): # R635
    """
    <deallocate-stmt> = DEALLOCATE ( <allocate-object-list> [ , <dealloc-opt-list> ] )
    """
    subclass_names = []
    use_names = ['Allocate_Object_List', 'Dealloc_Opt_List']

class Dealloc_Opt(KeywordValueBase): # R636
    """
    <dealloc-opt> = STAT = <stat-variable>
                    | ERRMSG = <errmsg-variable>
    """
    subclass_names = []
    use_names = ['Stat_Variable', 'Errmsg_Variable']
    def match(string):
        for (k,v) in [('STAT', Stat_Variable),
                      ('ERRMSG', Errmsg_Variable),
                      ]:
            try:
                obj = KeywordValueBase.match(k, v, string, upper_lhs = True)
            except NoMatchError:
                obj = None
            if obj is not None: return obj
        return
    pass

class Scalar_Char_Initialization_Expr(Base):
    subclass_names = ['Char_Initialization_Expr']

###############################################################################
############################### SECTION  7 ####################################
###############################################################################

class Primary(Base): # R701
    """
    <primary> = <constant>
                | <designator>
                | <array-constructor>
                | <structure-constructor>
                | <function-reference>
                | <type-param-inquiry>
                | <type-param-name>
                | ( <expr> )
    """
    subclass_names = ['Constant', 'Parenthesis', 'Designator','Array_Constructor',
                      'Structure_Constructor',
                      'Function_Reference', 'Type_Param_Inquiry', 'Type_Param_Name',
                       ]

class Parenthesis(BracketBase): # R701.h
    """
    <parenthesis> = ( <expr> )
    """
    subclass_names = []
    use_names = ['Expr']
    def match(string): return BracketBase.match('()', Expr, string)
    pass

class Level_1_Expr(UnaryOpBase): # R702
    """
    <level-1-expr> = [ <defined-unary-op> ] <primary>
    <defined-unary-op> = . <letter> [ <letter> ]... .
    """
    subclass_names = ['Primary']
    use_names = []
    def match(string):
        if pattern.non_defined_binary_op.match(string):
            raise NoMatchError,'%s: %r' % (Level_1_Expr.__name__, string)
        return UnaryOpBase.match(\
            pattern.defined_unary_op.named(),Primary,string)
    pass

class Defined_Unary_Op(STRINGBase): # R703
    """
    <defined-unary-op> = . <letter> [ <letter> ]... .
    """
    subclass_names = ['Defined_Op']


class Defined_Op(STRINGBase): # R703, 723
    """
    <defined-op> = . <letter> [ <letter> ]... .
    """
    subclass_names = []
    def match(string):
        if pattern.non_defined_binary_op.match(string):
            raise NoMatchError,'%s: %r' % (Defined_Unary_Op.__name__, string)
        return STRINGBase.match(pattern.abs_defined_op, string)
    pass

class Mult_Operand(BinaryOpBase): # R704
    """
    <mult-operand> = <level-1-expr> [ <power-op> <mult-operand> ]
    <power-op> = **
    """
    subclass_names = ['Level_1_Expr']
    use_names = ['Mult_Operand']
    def match(string):
        return BinaryOpBase.match(\
            Level_1_Expr,pattern.power_op.named(),Mult_Operand,string,right=False)
    pass

class Add_Operand(BinaryOpBase): # R705
    """
    <add-operand> = [ <add-operand> <mult-op> ] <mult-operand>
    <mult-op>  = *
                 | /
    """
    subclass_names = ['Mult_Operand']
    use_names = ['Add_Operand','Mult_Operand']
    def match(string):
        return BinaryOpBase.match(Add_Operand,pattern.mult_op.named(),Mult_Operand,string)
    pass

class Level_2_Expr(BinaryOpBase): # R706
    """
    <level-2-expr> = [ [ <level-2-expr> ] <add-op> ] <add-operand>
    <level-2-expr> = [ <level-2-expr> <add-op> ] <add-operand>
                     | <level-2-unary-expr>
    <add-op>   = +
                 | -
    """
    subclass_names = ['Level_2_Unary_Expr']
    use_names = ['Level_2_Expr']
    def match(string):
        return BinaryOpBase.match(\
            Level_2_Expr,pattern.add_op.named(),Add_Operand,string)
    pass

class Level_2_Unary_Expr(UnaryOpBase): # R706.c
    """
    <level-2-unary-expr> = [ <add-op> ] <add-operand>
    """
    subclass_names = ['Add_Operand']
    use_names = []
    def match(string): return UnaryOpBase.match(pattern.add_op.named(),Add_Operand,string)
    pass

#R707: <power-op> = **
#R708: <mult-op> = * | /
#R709: <add-op> = + | -

class Level_3_Expr(BinaryOpBase): # R710
    """
    <level-3-expr> = [ <level-3-expr> <concat-op> ] <level-2-expr>
    <concat-op>    = //
    """
    subclass_names = ['Level_2_Expr']
    use_names =['Level_3_Expr']
    def match(string):
        return BinaryOpBase.match(\
            Level_3_Expr,pattern.concat_op.named(),Level_2_Expr,string)
    pass

#R711: <concat-op> = //

class Level_4_Expr(BinaryOpBase): # R712
    """
    <level-4-expr> = [ <level-3-expr> <rel-op> ] <level-3-expr>
    <rel-op> = .EQ. | .NE. | .LT. | .LE. | .GT. | .GE. | == | /= | < | <= | > | >=
    """
    subclass_names = ['Level_3_Expr']
    use_names = []
    def match(string):
        return BinaryOpBase.match(\
            Level_3_Expr,pattern.rel_op.named(),Level_3_Expr,string)
    pass

#R713: <rel-op> = .EQ. | .NE. | .LT. | .LE. | .GT. | .GE. | == | /= | < | <= | > | >=

class And_Operand(UnaryOpBase): # R714
    """
    <and-operand> = [ <not-op> ] <level-4-expr>
    <not-op> = .NOT.
    """
    subclass_names = ['Level_4_Expr']
    use_names = []
    def match(string):
        return UnaryOpBase.match(\
            pattern.not_op.named(),Level_4_Expr,string)
    pass

class Or_Operand(BinaryOpBase): # R715
    """
    <or-operand> = [ <or-operand> <and-op> ] <and-operand>
    <and-op> = .AND.
    """
    subclass_names = ['And_Operand']
    use_names = ['Or_Operand','And_Operand']
    def match(string):
        return BinaryOpBase.match(\
            Or_Operand,pattern.and_op.named(),And_Operand,string)
    pass

class Equiv_Operand(BinaryOpBase): # R716
    """
    <equiv-operand> = [ <equiv-operand> <or-op> ] <or-operand>
    <or-op>  = .OR.
    """
    subclass_names = ['Or_Operand']
    use_names = ['Equiv_Operand']
    def match(string):
        return BinaryOpBase.match(\
            Equiv_Operand,pattern.or_op.named(),Or_Operand,string)
    pass


class Level_5_Expr(BinaryOpBase): # R717
    """
    <level-5-expr> = [ <level-5-expr> <equiv-op> ] <equiv-operand>
    <equiv-op> = .EQV.
               | .NEQV.
    """
    subclass_names = ['Equiv_Operand']
    use_names = ['Level_5_Expr']
    def match(string):
        return BinaryOpBase.match(\
            Level_5_Expr,pattern.equiv_op.named(),Equiv_Operand,string)
    pass

#R718: <not-op> = .NOT.
#R719: <and-op> = .AND.
#R720: <or-op> = .OR.
#R721: <equiv-op> = .EQV. | .NEQV.

class Expr(BinaryOpBase): # R722
    """
    <expr> = [ <expr> <defined-binary-op> ] <level-5-expr>
    <defined-binary-op> = . <letter> [ <letter> ]... .
    TODO: defined_binary_op must not be intrinsic_binary_op!!
    """
    subclass_names = ['Level_5_Expr']
    use_names = ['Expr']
    def match(string):
        return BinaryOpBase.match(Expr, pattern.defined_binary_op.named(), Level_5_Expr,
                                   string)
    pass

class Defined_Unary_Op(STRINGBase): # R723
    """
    <defined-unary-op> = . <letter> [ <letter> ]... .
    """
    subclass_names = ['Defined_Op']

class Logical_Expr(Base): # R724
    """
    <logical-expr> = <expr>
    """
    subclass_names = ['Expr']

class Char_Expr(Base): # R725
    """
    <char-expr> = <expr>
    """
    subclass_names = ['Expr']

class Default_Char_Expr(Base): # R726
    """
    <default-char-expr> = <expr>
    """
    subclass_names = ['Expr']

class Int_Expr(Base): # R727
    """
    <int-expr> = <expr>
    """
    subclass_names = ['Expr']

class Numeric_Expr(Base): # R728
    """
    <numeric-expr> = <expr>
    """
    subclass_names = ['Expr']

class Specification_Expr(Base): # R729
    """
    <specification-expr> = <scalar-int-expr>
    """
    subclass_names = ['Scalar_Int_Expr']

class Initialization_Expr(Base): # R730
    """
    <initialization-expr> = <expr>
    """
    subclass_names = ['Expr']

class Char_Initialization_Expr(Base): # R731
    """
    <char-initialization-expr> = <char-expr>
    """
    subclass_names = ['Char_Expr']

class Int_Initialization_Expr(Base): # R732
    """
    <int-initialization-expr> = <int-expr>
    """
    subclass_names = ['Int_Expr']

class Logical_Initialization_Expr(Base): # R733
    """
    <logical-initialization-expr> = <logical-expr>
    """
    subclass_names = ['Logical_Expr']

class Assignment_Stmt(StmtBase, BinaryOpBase): # R734
    """
    <assignment-stmt> = <variable> = <expr>
    """
    subclass_names = []
    use_names = ['Variable', 'Expr']
    def match(string):
        return BinaryOpBase.match(Variable, '=', Expr, string, right=False)
    pass

class Pointer_Assignment_Stmt(StmtBase): # R735
    """
    <pointer-assignment-stmt> = <data-pointer-object> [ ( <bounds-spec-list> ) ] => <data-target>
                                | <data-pointer-object> ( <bounds-remapping-list> ) => <data-target>
                                | <proc-pointer-object> => <proc-target>
    """
    subclass_names = []
    use_names = ['Data_Pointer_Object', 'Bounds_Spec_List', 'Data_Target', 'Bounds_Remapping_List',
                 'Proc_Pointer_Object', 'Proc_Target']

class Data_Pointer_Object(BinaryOpBase): # R736
    """
    <data-pointer-object> = <variable-name>
                            | <variable> % <data-pointer-component-name>
    """
    subclass_names = ['Variable_Name']
    use_names = ['Variable', 'Data_Pointer_Component_Name']
    def match(string):
        return BinaryOpBase.match(Variable, r'%', Data_Pointer_Component_Name, string)
    pass

class Bounds_Spec(SeparatorBase): # R737
    """
    <bounds-spec> = <lower-bound-expr> :
    """
    subclass_names = []
    use_names = ['Lower_Bound_Expr']
    def match(string): return SeparatorBase.match(Lower_Bound_Expr, None, string, require_lhs=True)
    pass

class Bounds_Remapping(SeparatorBase): # R738
    """
    <bounds-remapping> = <lower-bound-expr> : <upper-bound-expr>
    """
    subclass_names = []
    use_classes = ['Lower_Bound_Expr', 'Upper_Bound_Expr']
    def match(string): return SeparatorBase.match(Lower_Bound_Expr, Upper_Bound_Expr, string, require_lhs=True, require_rhs=True)
    pass

class Data_Target(Base): # R739
    """
    <data-target> = <variable>
                    | <expr>
    """
    subclass_names = ['Variable','Expr']

class Proc_Pointer_Object(Base): # R740
    """
    <proc-pointer-object> = <proc-pointer-name>
                            | <proc-component-ref>
    """
    subclass_names = ['Proc_Pointer_Name', 'Proc_Component_Ref']

class Proc_Component_Ref(BinaryOpBase): # R741
    """
    <proc-component-ref> = <variable> % <procedure-component-name>
    """
    subclass_names = []
    use_names = ['Variable','Procedure_Component_Name']
    def match(string):
        return BinaryOpBase.match(Variable, r'%', Procedure_Component_Name, string)
    pass

class Proc_Target(Base): # R742
    """
    <proc-target> = <expr>
                    | <procedure-name>
                    | <proc-component-ref>
    """
    subclass_names = ['Proc_Component_Ref', 'Procedure_Name', 'Expr']


class Where_Stmt(StmtBase): # R743
    """
    <where-stmt> = WHERE ( <mask-expr> ) <where-assignment-stmt>
    """
    subclass_names = []
    use_names = ['Mask_Expr', 'Where_Assignment_Stmt']
    def match(string):
        if string[:5].upper()!='WHERE': return
        line, repmap = string_replace_map(string[5:].lstrip())
        if not line.startswith('('): return
        i = line.find(')')
        if i==-1: return
        stmt = repmap(line[i+1:].lstrip())
        if not stmt: return
        expr = repmap(line[1:i].strip())
        if not expr: return
        return Mask_Expr(expr), Where_Assignment_Stmt(stmt)
    pass
    def tostr(self): return 'WHERE (%s) %s' % tuple(self.items)


class Where_Construct(Base): # R744
    """
    <where-construct> = <where-construct-stmt>
                              [ <where-body-construct> ]...
                            [ <masked-elsewhere-stmt>
                              [ <where-body-construct> ]...
                            ]...
                            [ <elsewhere-stmt>
                              [ <where-body-construct> ]... ]
                            <end-where-stmt>
    """
    subclass_names = []
    use_names = ['Where_Construct_Stmt', 'Where_Body_Construct',
                 'Elsewhere_Stmt', 'End_Where_Stmt'
                 ]

class Where_Construct_Stmt(StmtBase): # R745
    """
    <where-construct-stmt> = [ <where-construct-name> : ] WHERE ( <mask-expr> )
    """
    subclass_names = []
    use_names = ['Where_Construct_Name', 'Mask_Expr']

    def match(string):
        if string[:5].upper()!='WHERE': return
        line = string[5:].lstrip()
        if not line: return
        if line[0]+line[-1] != '()': return
        line = line[1:-1].strip()
        if not line: return
        return Mask_Expr(line),
    pass
    def tostr(self): return 'WHERE (%s)' % tuple(self.items)

class Where_Body_Construct(Base): # R746
    """
    <where-body-construct> = <where-assignment-stmt>
                             | <where-stmt>
                             | <where-construct>
    """
    subclass_names = ['Where_Assignment_Stmt', 'Where_Stmt', 'Where_Construct']

class Where_Assignment_Stmt(Base): # R747
    """
    <where-assignment-stmt> = <assignment-stmt>
    """
    subclass_names = ['Assignment_Stmt']

class Mask_Expr(Base): # R748
    """
    <mask-expr> = <logical-expr>
    """
    subclass_names = ['Logical_Expr']

class Masked_Elsewhere_Stmt(StmtBase): # R749
    """
    <masked-elsewhere-stmt> = ELSEWHERE ( <mask-expr> ) [ <where-construct-name> ]
    """
    subclass_names = []
    use_names = ['Mask_Expr', 'Where_Construct_Name']
    def match(string):
        if string[:9].upper()!='ELSEWHERE': return
        line = string[9:].lstrip()
        if not line.startswith('('): return
        i = line.rfind(')')
        if i==-1: return
        expr = line[1:i].strip()
        if not expr: return
        line = line[i+1:].rstrip()
        if line:
            return Mask_Expr(expr), Where_Construct_Name(line)
        return Mask_Expr(expr), None
    pass
    def tostr(self):
        if self.items[1] is None: return 'ELSEWHERE(%s)' % (self.items[0])
        return 'ELSEWHERE(%s) %s' % self.items

class Elsewhere_Stmt(StmtBase, WORDClsBase): # R750
    """
    <elsewhere-stmt> = ELSEWHERE [ <where-construct-name> ]
    """
    subclass_names = []
    use_names = ['Where_Construct_Name']
    def match(string): return WORDClsBase.match('ELSEWHERE', Where_Construct_Name, string)
    pass

class End_Where_Stmt(EndStmtBase): # R751
    """
    <end-where-stmt> = END WHERE [ <where-construct-name> ]
    """
    subclass_names = []
    use_names = ['Where_Construct_Name']
    def match(string): return EndStmtBase.match('WHERE',Where_Construct_Name, string, require_stmt_type=True)
    pass


class Forall_Construct(Base): # R752
    """
    <forall-construct> = <forall-construct-stmt>
                             [ <forall-body-construct> ]...
                             <end-forall-stmt>
    """
    subclass_names = []
    use_names = ['Forall_Construct_Stmt', 'Forall_Body_Construct', 'End_Forall_Stmt']

class Forall_Construct_Stmt(StmtBase, WORDClsBase): # R753
    """
    <forall-construct-stmt> = [ <forall-construct-name> : ] FORALL <forall-header>
    """
    subclass_names = []
    use_names = ['Forall_Construct_Name', 'Forall_Header']
    def match(string): return WORDClsBase.match('FORALL', Forall_Header, string, require_cls = True)
    pass

class Forall_Header(Base): # R754
    """
    <forall-header> = ( <forall-triplet-spec-list> [ , <scalar-mask-expr> ] )
    """
    subclass_names = []
    use_names = ['Forall_Triplet_Spec_List', 'Scalar_Mask_Expr']

class Forall_Triplet_Spec(Base): # R755
    """
    <forall-triplet-spec> = <index-name> = <subscript> : <subscript> [ : <stride> ]
    """
    subclass_names = []
    use_names = ['Index_Name', 'Subscript', 'Stride']

class Forall_Body_Construct(Base): # R756
    """
    <forall-body-construct> = <forall-assignment-stmt>
                              | <where-stmt>
                              | <where-construct>
                              | <forall-construct>
                              | <forall-stmt>
    """
    subclass_names = ['Forall_Assignment_Stmt', 'Where_Stmt', 'Where_Construct',
                      'Forall_Construct', 'Forall_Stmt']

class Forall_Assignment_Stmt(Base): # R757
    """
    <forall-assignment-stmt> = <assignment-stmt>
                               | <pointer-assignment-stmt>
    """
    subclass_names = ['Assignment_Stmt', 'Pointer_Assignment_Stmt']

class End_Forall_Stmt(EndStmtBase): # R758
    """
    <end-forall-stmt> = END FORALL [ <forall-construct-name> ]
    """
    subclass_names = []
    use_names = ['Forall_Construct_Name']
    def match(string): return EndStmtBase.match('FORALL',Forall_Construct_Name, string, require_stmt_type=True)
    pass

class Forall_Stmt(StmtBase): # R759
    """
    <forall-stmt> = FORALL <forall-header> <forall-assignment-stmt>
    """
    subclass_names = []
    use_names = ['Forall_Header', 'Forall_Assignment_Stmt']
    def match(string):
        if string[:6].upper()!='FORALL': return
        line, repmap = string_replace_map(string[6:].lstrip())
        if not line.startswith(')'): return
        i = line.find(')')
        if i==-1: return
        header = repmap(line[1:i].strip())
        if not header: return
        line = repmap(line[i+1:].lstrip())
        if not line: return
        return Forall_Header(header), Forall_Assignment_Stmt(line)
    pass
    def tostr(self): return 'FORALL %s %s' % self.items

###############################################################################
############################### SECTION  8 ####################################
###############################################################################

class Block(BlockBase): # R801
    """
    block = [ <execution-part-construct> ]...
    """
    subclass_names = []
    use_names = ['Execution_Part_Construct']
    def match(string): return BlockBase.match(None, [Execution_Part_Construct], None, string)
    pass

class If_Construct(BlockBase): # R802
    """
    <if-construct> = <if-then-stmt>
                           <block>
                         [ <else-if-stmt>
                           <block>
                         ]...
                         [ <else-stmt>
                           <block>
                         ]
                         <end-if-stmt>
    """
    subclass_names = []
    use_names = ['If_Then_Stmt', 'Block', 'Else_If_Stmt', 'Else_Stmt', 'End_If_Stmt']

    def match(reader):
        content = []
        try:
            obj = If_Then_Stmt(reader)
        except NoMatchError:
            obj = None
        if obj is None: return
        content.append(obj)
        obj = Block(reader)
        if obj is None: return # todo: restore reader
        content.append(obj)
        while 1:
            try:
                obj = Else_If_Stmt(reader)
            except NoMatchError:
                obj = None
            if obj is not None:
                content.append(obj)
                obj = Block(reader)
                if obj is None: return # todo: restore reader
                content.append(obj)
                continue
            try:
                obj = Else_Stmt(reader)
            except NoMatchError:
                obj = None
            if obj is not None:
                content.append(obj)
                obj = Block(reader)
                if obj is None: return # todo: restore reader
                content.append(obj)
            break
        try:
            obj = End_If_Stmt(reader)
        except NoMatchError:
            obj = None
        if obj is None: return # todo: restore reader
        content.append(obj)
        return content,
    pass

    def tofortran(self, tab='', isfix=None):
        l = []
        start = self.content[0]
        end = self.content[-1]
        l.append(start.tofortran(tab=tab,isfix=isfix))
        for item in self.content[1:-1]:
            if isinstance(item, (Else_If_Stmt, Else_Stmt)):
                l.append(item.tofortran(tab=tab,isfix=isfix))
            else:
                l.append(item.tofortran(tab=tab+'  ',isfix=isfix))
        l.append(end.tofortran(tab=tab,isfix=isfix))
        return '\n'.join(l)


class If_Then_Stmt(StmtBase): # R803
    """
    <if-then-stmt> = [ <if-construct-name> : ] IF ( <scalar-logical-expr> ) THEN
    """
    subclass_names = []
    use_names = ['If_Construct_Name', 'Scalar_Logical_Expr']
    def match(string):
        if string[:2].upper()!='IF': return
        if string[-4:].upper()!='THEN': return
        line = string[2:-4].strip()
        if not line: return
        if line[0]+line[-1]!='()': return
        return Scalar_Logical_Expr(line[1:-1].strip()),
    pass
    def tostr(self): return 'IF (%s) THEN' % self.items

class Else_If_Stmt(StmtBase): # R804
    """
    <else-if-stmt> = ELSE IF ( <scalar-logical-expr> ) THEN [ <if-construct-name> ]
    """
    subclass_names = []
    use_names = ['Scalar_Logical_Expr', 'If_Construct_Name']

    def match(string):
        if string[:4].upper()!='ELSE': return
        line = string[4:].lstrip()
        if line[:2].upper()!='IF': return
        line = line[2:].lstrip()
        if not line.startswith('('): return
        i = line.rfind(')')
        if i==-1: return
        expr = line[1:i].strip()
        line = line[i+1:].lstrip()
        if line[:4].upper()!='THEN': return
        line = line[4:].lstrip()
        if line: return Scalar_Logical_Expr(expr), If_Construct_Name(line)
        return Scalar_Logical_Expr(expr), None
    pass
    def tostr(self):
        if self.items[1] is None:
            return 'ELSE IF (%s) THEN' % (self.items[0])
        return 'ELSE IF (%s) THEN %s' % self.items

class Else_Stmt(StmtBase): # R805
    """
    <else-stmt> = ELSE [ <if-construct-name> ]
    """
    subclass_names = []
    use_names = ['If_Construct_Name']
    def match(string):
        if string[:4].upper()!='ELSE': return
        line = string[4:].lstrip()
        if line: return If_Construct_Name(line),
        return None,
    pass
    def tostr(self):
        if self.items[0] is None:
            return 'ELSE'
        return 'ELSE %s' % self.items

class End_If_Stmt(EndStmtBase): # R806
    """
    <end-if-stmt> = END IF [ <if-construct-name> ]
    """
    subclass_names = []
    use_names = ['If_Construct_Name']
    def match(string): return EndStmtBase.match('IF',If_Construct_Name, string, require_stmt_type=True)
    pass

class If_Stmt(StmtBase): # R807
    """
    <if-stmt> = IF ( <scalar-logical-expr> ) <action-stmt>
    """
    subclass_names = []
    use_names = ['Scalar_Logical_Expr', 'Action_Stmt_C802']
    def match(string):
        if string[:2].upper() != 'IF': return
        line, repmap = string_replace_map(string)
        line = line[2:].lstrip()
        if not line.startswith('('): return
        i = line.find(')')
        if i==-1: return
        expr = repmap(line[1:i].strip())
        stmt = repmap(line[i+1:].lstrip())
        return Scalar_Logical_Expr(expr), Action_Stmt_C802(stmt)
    pass
    def tostr(self): return 'IF (%s) %s' % self.items

class Case_Construct(Base): # R808
    """
    <case-construct> = <select-case-stmt>
                           [ <case-stmt>
                             <block>
                           ]..
                           <end-select-stmt>
    """
    subclass_names = []
    use_names = ['Select_Case_Stmt', 'Case_Stmt', 'End_Select_Stmt']

class Select_Case_Stmt(StmtBase, CALLBase): # R809
    """
    <select-case-stmt> = [ <case-construct-name> : ] SELECT CASE ( <case-expr> )
    """
    subclass_names = []
    use_names = ['Case_Construct_Name', 'Case_Expr']
    def match(string): return CALLBase.match(pattter.abs_select_case, Case_Expr, string)
    pass

class Case_Stmt(StmtBase): # R810
    """
    <case-stmt> = CASE <case-selector> [ <case-construct-name> ]
    """
    subclass_names = []
    use_names = ['Case_Selector', 'Case_Construct_Name']

class End_Select_Stmt(EndStmtBase): # R811
    """
    <end-select-stmt> = END SELECT [ <case-construct-name> ]
    """
    subclass_names = []
    use_names = ['Case_Construct_Name']
    def match(string): return EndStmtBase.match('SELECT',Case_Construct_Name, string, require_stmt_type=True)
    pass

class Case_Expr(Base): # R812
    """
    <case-expr> = <scalar-int-expr>
                  | <scalar-char-expr>
                  | <scalar-logical-expr>
    """
    subclass_names = []
    subclass_names = ['Scalar_Int_Expr', 'Scalar_Char_Expr', 'Scalar_Logical_Expr']

class Case_Selector(Base): # R813
    """
    <case-selector> = ( <case-value-range-list> )
                      | DEFAULT
    """
    subclass_names = []
    use_names = ['Case_Value_Range_List']

class Case_Value_Range(SeparatorBase): # R814
    """
    <case-value-range> = <case-value>
                         | <case-value> :
                         | : <case-value>
                         | <case-value> : <case-value>
    """
    subclass_names = ['Case_Value']
    def match(string): return SeparatorBase.match(Case_Value, Case_Value, string)
    pass

class Case_Value(Base): # R815
    """
    <case-value> = <scalar-int-initialization-expr>
                   | <scalar-char-initialization-expr>
                   | <scalar-logical-initialization-expr>
    """
    subclass_names = ['Scalar_Int_Initialization_Expr', 'Scalar_Char_Initialization_Expr', 'Scalar_Logical_Initialization_Expr']


class Associate_Construct(Base): # R816
    """
    <associate-construct> = <associate-stmt>
                                <block>
                                <end-associate-stmt>
    """
    subclass_names = []
    use_names = ['Associate_Stmt', 'Block', 'End_Associate_Stmt']

class Associate_Stmt(StmtBase, CALLBase): # R817
    """
    <associate-stmt> = [ <associate-construct-name> : ] ASSOCIATE ( <association-list> )
    """
    subclass_names = []
    use_names = ['Associate_Construct_Name', 'Association_List']
    def match(string): return CALLBase.match('ASSOCIATE', Association_List, string)
    pass

class Association(BinaryOpBase): # R818
    """
    <association> = <associate-name> => <selector>
    """
    subclass_names = []
    use_names = ['Associate_Name', 'Selector']
    def match(string): return BinaryOpBase.match(Assiciate_Name, '=>', Selector, string)
    pass

class Selector(Base): # R819
    """
    <selector> = <expr>
                 | <variable>
    """
    subclass_names = ['Expr', 'Variable']

class End_Associate_Stmt(EndStmtBase): # R820
    """
    <end-associate-stmt> = END ASSOCIATE [ <associate-construct-name> ]
    """
    subclass_names = []
    use_names = ['Associate_Construct_Name']
    def match(string): return EndStmtBase.match('ASSOCIATE',Associate_Construct_Name, string, require_stmt_type=True)
    pass

class Select_Type_Construct(Base): # R821
    """
    <select-type-construct> = <select-type-stmt>
                                  [ <type-guard-stmt>
                                    <block>
                                  ]...
                                  <end-select-type-stmt>
    """
    subclass_names = []
    use_names = ['Select_Type_Stmt', 'Type_Guard_Stmt', 'Block', 'End_Select_Type_Stmt']

class Select_Type_Stmt(StmtBase): # R822
    """
    <select-type-stmt> = [ <select-construct-name> : ] SELECT TYPE ( [ <associate-name> => ] <selector> )
    """
    subclass_names = []
    use_names = ['Select_Construct_Name', 'Associate_Name', 'Selector']

class Type_Guard_Stmt(StmtBase): # R823
    """
    <type-guard-stmt> = TYPE IS ( <type-spec> ) [ <select-construct-name> ]
                        | CLASS IS ( <type-spec> ) [ <select-construct-name> ]
                        | CLASS DEFAULT [ <select-construct-name> ]
    """
    subclass_names = []
    use_names = ['Type_Spec', 'Select_Construct_Name']
    def match(string):
        if string[:4].upper()=='TYPE':
            line = string[4:].lstrip()
            if not line[:2].upper()=='IS': return
            line = line[2:].lstrip()
            kind = 'TYPE IS'
        elif string[:5].upper()=='CLASS':
            line = string[5:].lstrip()
            if line[:2].upper()=='IS':
                line = line[2:].lstrip()
                kind = 'CLASS IS'
            elif line[:7].upper()=='DEFAULT':
                line = line[7:].lstrip()
                if line:
                    if isalnum(line[0]): return
                    return 'CLASS DEFAULT', None, Select_Construct_Name(line)
                return 'CLASS DEFAULT', None, None
            else:
                return
        else:
            return
        if not line.startswith('('): return
        i = line.rfind(')')
        if i==-1: return
        l = line[1:i].strip()
        if not l: return
        line = line[i+1:].lstrip()
        if line:
            return kind, Type_Spec(l), Select_Construct_Name(line)
        return kind, Type_Spec(l), None
    pass
    def tostr(self):
        s = str(self.items[0])
        if self.items[1] is not None:
            s += ' (%s)' % (self.items[0])
        if self.items[2] is not None:
            s += ' %s' % (self.items[2])
        return s

class End_Select_Type_Stmt(EndStmtBase): # R824
    """
    <end-select-type-stmt> = END SELECT [ <select-construct-name> ]
    """
    subclass_names = []
    use_names = ['Select_Construct_Name']
    def match(string): return EndStmtBase.match('SELECT',Select_Construct_Name, string, require_stmt_type=True)
    pass

class Do_Construct(Base): # R825
    """
    <do-construct> = <block-do-construct>
                     | <nonblock-do-construct>
    """
    subclass_names = ['Block_Do_Construct', 'Nonblock_Do_Construct']

class Block_Do_Construct(BlockBase): # R826
    """
    <block-do-construct> = <do-stmt>
                               <do-block>
                               <end-do>
    """
    subclass_names = []
    use_names = ['Do_Stmt', 'Do_Block', 'End_Do']
    def match(reader):
        assert isinstance(reader,FortranReaderBase),`reader`
        content = []
        try:
            obj = Do_Stmt(reader)
        except NoMatchError:
            obj = None
        if obj is None: return
        content.append(obj)
        if isinstance(obj, Label_Do_Stmt):
            label = str(obj.dolabel)
            while 1:
                try:
                    obj = Execution_Part_Construct(reader)
                except NoMatchError:
                    obj = None
                if obj is None: break
                content.append(obj)
                if isinstance(obj, Continue_Stmt) and obj.item.label==label:
                    return content,
            return
            raise RuntimeError,'Expected continue stmt with specified label'
        else:
            obj = End_Do(reader)
            content.append(obj)
            raise NotImplementedError
        return content,
    pass

    def tofortran(self, tab='', isfix=None):
        if not isinstance(self.content[0], Label_Do_Stmt):
            return BlockBase.tofortran(tab, isfix)
        l = []
        start = self.content[0]
        end = self.content[-1]
        extra_tab = '  '
        l.append(start.tofortran(tab=tab,isfix=isfix))
        for item in self.content[1:-1]:
            l.append(item.tofortran(tab=tab+extra_tab,isfix=isfix))
        if len(self.content)>1:
            l.append(end.tofortran(tab=tab,isfix=isfix))
        return '\n'.join(l)

class Do_Stmt(Base): # R827
    """
    <do-stmt> = <label-do-stmt>
                | <nonlabel-do-stmt>
    """
    subclass_names = ['Label_Do_Stmt', 'Nonlabel_Do_Stmt']

class Label_Do_Stmt(StmtBase): # R828
    """
    <label-do-stmt> = [ <do-construct-name> : ] DO <label> [ <loop-control> ]
    """
    subclass_names = []
    use_names = ['Do_Construct_Name', 'Label', 'Loop_Control']
    def match(string):
        if string[:2].upper()!='DO': return
        line = string[2:].lstrip()
        m = pattern.label.match(line)
        if m is None: return
        label = m.group()
        line = line[m.end():].lstrip()
        if line: return Label(label), Loop_Control(line)
        return Label(label), None
    pass
    def tostr(self):
        if self.itens[1] is None: return 'DO %s' % (self.items[0])
        return 'DO %s %s' % self.items

class Nonlabel_Do_Stmt(StmtBase, WORDClsBase): # R829
    """
    <nonlabel-do-stmt> = [ <do-construct-name> : ] DO [ <loop-control> ]
    """
    subclass_names = []
    use_names = ['Do_Construct_Name', 'Loop_Control']
    def match(string): return WORDClsBase.match('DO', Loop_Control, string)
    pass

class Loop_Control(Base): # R830
    """
    <loop-control> = [ , ] <do-variable> = <scalar-int-expr> , <scalar-int-expr> [ , <scalar-int-expr> ]
                     | [ , ] WHILE ( <scalar-logical-expr> )
    """
    subclass_names = []
    use_names = ['Do_Variable', 'Scalar_Int_Expr', 'Scalar_Logical_Expr']
    def match(string):
        if string.startswith(','):
            line, repmap = string_replace_map(string[1:].lstrip())
        else:
            line, repmap = string_replace_map(string)
        if line[:5].upper()=='WHILE' and line[5:].lstrip().startswith('('):
            l = line[5:].lstrip()
            i = l.find(')')
            if i!=-1 and i==len(l)-1:
                return Scalar_Logical_Expr(repmap(l[1:i].strip())),
        if line.count('=')!=1: return
        var,rhs = line.split('=')
        rhs = [s.strip() for s in rhs.lstrip().split(',')]
        if not 2<=len(rhs)<=3: return
        return Variable(repmap(var.rstrip())),map(Scalar_Int_Expr, map(repmap,rhs))
    pass
    def tostr(self):
        if len(self.items)==1: return ', WHILE (%s)' % (self.items[0])
        return ', %s = %s' % (self.items[0], ', '.join(map(str,self.items[1])))

class Do_Variable(Base): # R831
    """
    <do-variable> = <scalar-int-variable>
    """
    subclass_names = ['Scalar_Int_Variable']

class Do_Block(Base): # R832
    """
    <do-block> = <block>
    """
    subclass_names = ['Block']

class End_Do(Base): # R833
    """
    <end-do> = <end-do-stmt>
               | <continue-stmt>
    """
    subclass_names = ['End_Do_Stmt', 'Continue_Stmt']

class End_Do_Stmt(EndStmtBase): # R834
    """
    <end-do-stmt> = END DO [ <do-construct-name> ]
    """
    subclass_names = []
    use_names = ['Do_Construct_Name']
    def match(string): return EndStmtBase.match('DO',Do_Construct_Name, string, require_stmt_type=True)
    pass

class Nonblock_Do_Construct(Base): # R835
    """
    <nonblock-do-stmt> = <action-term-do-construct>
                         | <outer-shared-do-construct>
    """
    subclass_names = ['Action_Term_Do_Construct', 'Outer_Shared_Do_Construct']

class Action_Term_Do_Construct(BlockBase): # R836
    """
    <action-term-do-construct> = <label-do-stmt>
                                     <do-body>
                                     <do-term-action-stmt>
    """
    subclass_names = []
    use_names = ['Label_Do_Stmt', 'Do_Body', 'Do_Term_Action_Stmt']
    def match(reader):
        content = []
        for cls in [Label_Do_Stmt, Do_Body, Do_Term_Action_Stmt]:
            obj = cls(reader)
            if obj is None: # todo: restore reader
                return
            content.append(obj)
        return content,
    pass

class Do_Body(BlockBase): # R837
    """
    <do-body> = [ <execution-part-construct> ]...
    """
    subclass_names = []
    use_names = ['Execution_Part_Construct']
    def match(string): return BlockBase.match(None, [Execution_Part_Construct], None, string)
    pass

class Do_Term_Action_Stmt(StmtBase): # R838
    """
    <do-term-action-stmt> = <action-stmt>
    C824: <do-term-action-stmt> shall not be <continue-stmt>, <goto-stmt>, <return-stmt>, <stop-stmt>,
                          <exit-stmt>, <cycle-stmt>, <end-function-stmt>, <end-subroutine-stmt>,
                          <end-program-stmt>, <arithmetic-if-stmt>
    """
    subclass_names = ['Action_Stmt_C824']

class Outer_Shared_Do_Construct(BlockBase): # R839
    """
    <outer-shared-do-construct> = <label-do-stmt>
                                      <do-body>
                                      <shared-term-do-construct>
    """
    subclass_names = []
    use_names = ['Label_Do_Stmt', 'Do_Body', 'Shared_Term_Do_Construct']
    def match(reader):
        content = []
        for cls in [Label_Do_Stmt, Do_Body, Shared_Term_Do_Construct]:
            obj = cls(reader)
            if obj is None: # todo: restore reader
                return
            content.append(obj)
        return content,
    pass

class Shared_Term_Do_Construct(Base): # R840
    """
    <shared-term-do-construct> = <outer-shared-do-construct>
                                 | <inner-shared-do-construct>
    """
    subclass_names = ['Outer_Shared_Do_Construct', 'Inner_Shared_Do_Construct']

class Inner_Shared_Do_Construct(BlockBase): # R841
    """
    <inner-shared-do-construct> = <label-do-stmt>
                                      <do-body>
                                      <do-term-shared-stmt>
    """
    subclass_names = []
    use_names = ['Label_Do_Stmt', 'Do_Body', 'Do_Term_Shared_Stmt']

    def match(reader):
        content = []
        for cls in [Label_Do_Stmt, Do_Body, Do_Term_Shared_Stmt]:
            obj = cls(reader)
            if obj is None: # todo: restore reader
                return
            content.append(obj)
        return content,
    pass

class Do_Term_Shared_Stmt(StmtBase): # R842
    """
    <do-term-shared-stmt> = <action-stmt>
    C826: see C824 above.
    """
    subclass_names = ['Action_Stmt']

class Cycle_Stmt(StmtBase, WORDClsBase): # R843
    """
    <cycle-stmt> = CYCLE [ <do-construct-name> ]
    """
    subclass_names = []
    use_names = ['Do_Construct_Name']
    def match(string): return WORDClsBase.match('CYCLE', Do_Construct_Name, string)
    pass

class Exit_Stmt(StmtBase, WORDClsBase): # R844
    """
    <exit-stmt> = EXIT [ <do-construct-name> ]
    """
    subclass_names = []
    use_names = ['Do_Construct_Name']
    def match(string): return WORDClsBase.match('EXIT', Do_Construct_Name, string)
    pass

class Goto_Stmt(StmtBase): # R845
    """
    <goto-stmt> = GO TO <label>
    """
    subclass_names = []
    use_names = ['Label']
    def match(string):
        if string[:2].upper() != 'GO': return
        line = string[2:].lstrip()
        if line[:2].upper() != 'TO': return
        return Label(line[2:].lstrip()),
    pass
    def tostr(self): return 'GO TO %s' % (self.items[0])

class Computed_Goto_Stmt(StmtBase): # R846
    """
    <computed-goto-stmt> = GO TO ( <label-list> ) [ , ] <scalar-int-expr>
    """
    subclass_names = []
    use_names = ['Label_List', 'Scalar_Int_Expr']
    def match(string):
        if string[:2].upper()!='GO': return
        line = string[2:].lstrip()
        if line[:2].upper()!='TO': return
        line = line[2:].lstrip()
        if not line.startswith('('): return
        i = line.find(')')
        if i==-1: return
        lst = line[1:i].strip()
        if not lst: return
        line = line[i+1:].lstrip()
        if line.startswith(','):
            line = line[1:].lstrip()
        if not line: return
        return Label_List(lst), Scalar_Int_Expr(line)
    pass
    def tostr(self): return 'GO TO (%s), %s' % self.items

class Arithmetic_If_Stmt(StmtBase): # R847
    """
    <arithmetic-if-stmt> = IF ( <scalar-numeric-expr> ) <label> , <label> , <label>
    """
    subclass_names = []
    use_names = ['Scalar_Numeric_Expr', 'Label']
    def match(string):
        if string[:2].upper() != 'IF': return
        line = string[2:].lstrip()
        if not line.startswith('('): return
        i = line.rfind(')')
        if i==-1: return
        labels = line[i+1:].lstrip().split(',')
        if len(labels) != 3: return
        labels = [Label(l.strip()) for l in labels]
        return (Scalar_Numeric_Expr(line[1:i].strip()),) + tuple(labels)
    pass
    def tostr(self): return 'IF (%s) %s, %s, %s' % self.items

class Continue_Stmt(StmtBase, STRINGBase): # R848
    """
    <continue-stmt> = CONTINUE
    """
    subclass_names = []
    def match(string): return STRINGBase.match('CONTINUE', string)
    pass


class Stop_Stmt(StmtBase, WORDClsBase): # R849
    """
    <stop-stmt> = STOP [ <stop-code> ]
    """
    subclass_names = []
    use_names = ['Stop_Code']
    def match(string): return WORDClsBase.match('STOP', Stop_Code, string)
    pass

class Stop_Code(StringBase): # R850
    """
    <stop-code> = <scalar-char-constant>
                  | <digit> [ <digit> [ <digit> [ <digit> [ <digit> ] ] ] ]
    """
    subclass_names = ['Scalar_Char_Constant']
    def match(string): return StringBase.match(pattern.abs_label, string)
    pass


###############################################################################
############################### SECTION  9 ####################################
###############################################################################

class Io_Unit(StringBase): # R901
    """
    <io-unit> = <file-unit-number>
                | *
                | <internal-file-variable>
    """
    subclass_names = ['File_Unit_Number', 'Internal_File_Variable']
    def match(string): return StringBase.match('*', string)
    pass

class File_Unit_Number(Base): # R902
    """
    <file-unit-number> = <scalar-int-expr>
    """
    subclass_names = ['Scalar_Int_Expr']

class Internal_File_Variable(Base): # R903
    """
    <internal-file-variable> = <char-variable>
    C901: <char-variable> shall not be an array section with a vector subscript.
    """
    subclass_names = ['Char_Variable']

class Open_Stmt(StmtBase, CALLBase): # R904
    """
    <open-stmt> = OPEN ( <connect-spec-list> )
    """
    subclass_names = []
    use_names = ['Connect_Spec_List']
    def match(string): CALLBase.match('OPEN', Connect_Spec_List, string, require_rhs=True)
    pass

class Connect_Spec(KeywordValueBase): # R905
    """
    <connect-spec> = [ UNIT = ] <file-unit-number>
                     | ACCESS = <scalar-default-char-expr>
                     | ACTION = <scalar-default-char-expr>
                     | ASYNCHRONOUS = <scalar-default-char-expr>
                     | BLANK = <scalar-default-char-expr>
                     | DECIMAL = <scalar-default-char-expr>
                     | DELIM = <scalar-default-char-expr>
                     | ENCODING = <scalar-default-char-expr>
                     | ERR = <label>
                     | FILE = <file-name-expr>
                     | FORM = <scalar-default-char-expr>
                     | IOMSG = <iomsg-variable>
                     | IOSTAT = <scalar-int-variable>
                     | PAD = <scalar-default-char-expr>
                     | POSITION = <scalar-default-char-expr>
                     | RECL = <scalar-int-expr>
                     | ROUND = <scalar-default-char-expr>
                     | SIGN = <scalar-default-char-expr>
                     | STATUS = <scalar-default-char-expr>
    """
    subclass_names = []
    use_names = ['File_Unit_Number', 'Scalar_Default_Char_Expr', 'Label', 'File_Name_Expr', 'Iomsg_Variable',
                 'Scalar_Int_Expr', 'Scalar_Int_Variable']
    def match(string):
        for (k,v) in [\
            (['ACCESS','ACTION','ASYNCHRONOUS','BLANK','DECIMAL','DELIM','ENCODING',
              'FORM','PAD','POSITION','ROUND','SIGN','STATUS'], Scalar_Default_Char_Expr),
            ('ERR', Label),
            ('FILE',File_Name_Expr),
            ('IOSTAT', Scalar_Int_Variable),
            ('IOMSG', Iomsg_Variable),
            ('RECL', Scalar_Int_Expr),
            ('UNIT', File_Unit_Number),
            ]:
            try:
                obj = KeywordValueBase.match(k, v, string, upper_lhs = True)
            except NoMatchError:
                obj = None
            if obj is not None: return obj
        return 'UNIT', File_Unit_Number
    pass


class File_Name_Expr(Base): # R906
    """
    <file-name-expr> = <scalar-default-char-expr>
    """
    subclass_names = ['Scalar_Default_Char_Expr']

class Iomsg_Variable(Base): # R907
    """
    <iomsg-variable> = <scalar-default-char-variable>
    """
    subclass_names = ['Scalar_Default_Char_Variable']

class Close_Stmt(StmtBase, CALLBase): # R908
    """
    <close-stmt> = CLOSE ( <close-spec-list> )
    """
    subclass_names = []
    use_names = ['Close_Spec_List']
    def match(string): CALLBase.match('CLOSE', Close_Spec_List, string, require_rhs=True)
    pass

class Close_Spec(KeywordValueBase): # R909
    """
    <close-spec> = [ UNIT = ] <file-unit-number>
                   | IOSTAT = <scalar-int-variable>
                   | IOMSG = <iomsg-variable>
                   | ERR = <label>
                   | STATUS = <scalar-default-char-expr>
    """
    subclass_names = []
    use_names = ['File_Unit_Number', 'Scalar_Default_Char_Expr', 'Label', 'Iomsg_Variable',
                 'Scalar_Int_Variable']
    def match(string):
        for (k,v) in [\
            ('ERR', Label),
            ('IOSTAT', Scalar_Int_Variable),
            ('IOMSG', Iomsg_Variable),
            ('STATUS', Scalar_Default_Char_Expr),
            ('UNIT', File_Unit_Number),
            ]:
            try:
                obj = KeywordValueBase.match(k, v, string, upper_lhs = True)
            except NoMatchError:
                obj = None
            if obj is not None: return obj
        return 'UNIT', File_Unit_Number(string)
    pass

class Read_Stmt(StmtBase): # R910
    """
    <read-stmt> = READ ( <io-control-spec-list> ) [ <input-item-list> ]
                  | READ <format> [ , <input-item-list> ]
    """
    subclass_names = []
    use_names = ['Io_Control_Spec_List', 'Input_Item_List', 'Format']

class Write_Stmt(StmtBase): # R911
    """
    <write-stmt> = WRITE ( <io-control-spec-list> ) [ <output-item-list> ]
    """
    subclass_names = []
    use_names = ['Io_Control_Spec_List', 'Output_Item_List']
    def match(string):
        if string[:5].upper()!='WRITE': return
        line = string[5:].lstrip()
        if not line.startswith('('): return
        line, repmap = string_replace_map(line)
        i = line.find(')')
        if i==-1: return
        l = line[1:i].strip()
        if not l: return
        l = repmap(l)
        if i==len(line)-1:
            return Io_Control_Spec_List(l),None
        return Io_Control_Spec_List(l), Output_Item_List(repmap(line[i+1:].lstrip()))
    pass
    def tostr(self):
        if self.items[1] is None: return 'WRITE(%s)' % (self.items[0])
        return 'WRITE(%s) %s' % tuple(self.items)

class Print_Stmt(StmtBase): # R912
    """
    <print-stmt> = PRINT <format> [ , <output-item-list> ]
    """
    subclass_names = []
    use_names = ['Format', 'Output_Item_List']
    def match(string):
        if string[:5].upper()!='PRINT': return
        line = string[5:]
        if not line: return
        c = line[0].upper()
        if 'A'<=c<='Z' or c=='_' or '0'<=c<='9': return
        line, repmap = string_replace_map(line.lstrip())
        i = line.find(',')
        if i==-1: return Format(repmap(line)), None
        l = repmap(line[i+1:].lstrip())
        if not l: return
        return Format(repmap(line[:i].rstrip())), Output_Item_List(l)
    pass
    def tostr(self):
        if self.items[1] is None: return 'PRINT %s' % (self.items[0])
        return 'PRINT %s, %s' % tuple(self.items)

class Io_Control_Spec_List(SequenceBase): # R913-list
    """
    <io-control-spec-list> is a list taking into account C910, C917, C918
    """
    subclass_names = []
    use_names = ['Io_Control_Spec']
    def match(string):
        line, repmap = string_replace_map(string)
        splitted = line.split(',')
        if not splitted: return
        lst = []
        for i in range(len(splitted)):
            p = splitted[i].strip()
            if i==0:
                if '=' not in p: p = 'UNIT=%s' % (repmap(p))
                else: p = repmap(p)
            elif i==1:
                if '=' not in p:
                    p = repmap(p)
                    try:
                        f = Format(p)
                        # todo: make sure that f is char-expr, if not, raise NoMatchError
                        p = 'FMT=%s' % (Format(p))
                    except NoMatchError:
                        p = 'NML=%s' % (Namelist_Group_Name(p))
                else:
                    p = repmap(p)
            else:
                p = repmap(p)
            lst.append(Io_Control_Spec(p))
        return ',', tuple(lst)
    pass

class Io_Control_Spec(KeywordValueBase): # R913
    """
    <io-control-spec> = [ UNIT = ] <io-unit>
                        | [ FMT = ] <format>
                        | [ NML = ] <namelist-group-name>
                        | ADVANCE = <scalar-default-char-expr>
                        | ASYNCHRONOUS = <scalar-char-initialization-expr>
                        | BLANK = <scalar-default-char-expr>
                        | DECIMAL = <scalar-default-char-expr>
                        | DELIM = <scalar-default-char-expr>
                        | END = <label>
                        | EOR = <label>
                        | ERR = <label>
                        | ID = <scalar-int-variable>
                        | IOMSG = <iomsg-variable>
                        | IOSTAT = <scalar-int-variable>
                        | PAD = <scalar-default-char-expr>
                        | POS = <scalar-int-expr>
                        | REC = <scalar-int-expr>
                        | ROUND = <scalar-default-char-expr>
                        | SIGN = <scalar-default-char-expr>
                        | SIZE = <scalar-int-variable>
    """
    subclass_names = []
    use_names = ['Io_Unit', 'Format', 'Namelist_Group_Name', 'Scalar_Default_Char_Expr',
                 'Scalar_Char_Initialization_Expr', 'Label', 'Scalar_Int_Variable',
                 'Iomsg_Variable', 'Scalar_Int_Expr']
    def match(string):
        for (k,v) in [\
            (['ADVANCE', 'BLANK', 'DECIMAL', 'DELIM', 'PAD', 'ROUND', 'SIGN'], Scalar_Default_Char_Expr),
            ('ASYNCHRONOUS', Scalar_Char_Initialization_Expr),
            (['END','EOR','ERR'], Label),
            (['ID','IOSTAT','SIZE'], Scalar_Int_Variable),
            ('IOMSG', Iomsg_Variable),
            (['POS', 'REC'], Scalar_Int_Expr),
            ('UNIT', Io_Unit),
            ('FMT', Format),
            ('NML', Namelist_Group_Name)
            ]:
            try:
                obj = KeywordValueBase.match(k, v, string, upper_lhs = True)
            except NoMatchError:
                obj = None
            if obj is not None: return obj
        return
    pass

class Format(StringBase): # R914
    """
    <format> = <default-char-expr>
               | <label>
               | *
    """
    subclass_names = ['Label', 'Default_Char_Expr']
    def match(string): return StringBase.match('*', string)
    pass

class Input_Item(Base): # R915
    """
    <input-item> = <variable>
                   | <io-implied-do>
    """
    subclass_names = ['Variable', 'Io_Implied_Do']

class Output_Item(Base): # R916
    """
    <output-item> = <expr>
                    | <io-implied-do>
    """
    subclass_names = ['Expr', 'Io_Implied_Do']

class Io_Implied_Do(Base): # R917
    """
    <io-implied-do> = ( <io-implied-do-object-list> , <io-implied-do-control> )
    """
    subclass_names = []
    use_names = ['Io_Implied_Do_Object_List', 'Io_Implied_Do_Control']

class Io_Implied_Do_Object(Base): # R918
    """
    <io-implied-do-object> = <input-item>
                             | <output-item>
    """
    subclass_names = ['Input_Item', 'Output_Item']

class Io_Implied_Do_Control(Base): # R919
    """
    <io-implied-do-control> = <do-variable> = <scalar-int-expr> , <scalar-int-expr> [ , <scalar-int-expr> ]
    """
    subclass_names = []
    use_names = ['Do_Variable', 'Scalar_Int_Expr']

class Dtv_Type_Spec(CALLBase): # R920
    """
    <dtv-type-spec> = TYPE ( <derived-type-spec> )
                      | CLASS ( <derived-type-spec> )
    """
    subclass_names = []
    use_names = ['Derived_Type_Spec']
    def match(string): CALLStmt.match(['TYPE', 'CLASS'], Derived_Type_Spec, string, require_rhs=True)
    pass

class Wait_Stmt(StmtBase, CALLBase): # R921
    """
    <wait-stmt> = WAIT ( <wait-spec-list> )
    """
    subclass_names = []
    use_names = ['Wait_Spec_List']
    def match(string): return CALLBase.match('WAIT', Wait_Spec_List, string, require_rhs=True)
    pass

class Wait_Spec(KeywordValueBase): # R922
    """
    <wait-spec> = [ UNIT = ] <file-unit-number>
                  | END = <label>
                  | EOR = <label>
                  | ERR = <label>
                  | ID = <scalar-int-expr>
                  | IOMSG = <iomsg-variable>
                  | IOSTAT = <scalar-int-variable>
    """
    subclass_names = []
    use_names = ['File_Unit_Number', 'Label', 'Scalar_Int_Expr', 'Iomsg_Variable', 'Scalar_Int_Variable']
    def match(string):
        for (k,v) in [\
            (['END','EOR','ERR'], Label),
            ('IOSTAT', Scalar_Int_Variable),
            ('IOMSG', Iomsg_Variable),
            ('ID', Scalar_Int_Expr),
            ('UNIT', File_Unit_Number),
            ]:
            try:
                obj = KeywordValueBase.match(k, v, string, upper_lhs = True)
            except NoMatchError:
                obj = None
            if obj is not None: return obj
        return 'UNIT', File_Unit_Number(string)

    pass

class Backspace_Stmt(StmtBase): # R923
    """
    <backspace-stmt> = BACKSPACE <file-unit-number>
                       | BACKSPACE ( <position-spec-list> )
    """
    subclass_names = []
    use_names = ['File_Unit_Number', 'Position_Spec_List']

class Endfile_Stmt(StmtBase): # R924
    """
    <endfile-stmt> = ENDFILE <file-unit-number>
                     | ENDFILE ( <position-spec-list> )
    """
    subclass_names = []
    use_names = ['File_Unit_Number', 'Position_Spec_List']

class Rewind_Stmt(StmtBase): # R925
    """
    <rewind-stmt> = REWIND <file-unit-number>
                    | REWIND ( <position-spec-list> )
    """
    subclass_names = []
    use_names = ['File_Unit_Number', 'Position_Spec_List']

class Position_Spec(KeywordValueBase): # R926
    """
    <position-spec> = [ UNIT = ] <file-unit-number>
                      | IOMSG = <iomsg-variable>
                      | IOSTAT = <scalar-int-variable>
                      | ERR = <label>
    """
    subclass_names = []
    use_names = ['File_Unit_Number', 'Iomsg_Variable', 'Scalar_Int_Variable', 'Label']
    def match(string):
        for (k,v) in [\
            ('ERR', Label),
            ('IOSTAT', Scalar_Int_Variable),
            ('IOMSG', Iomsg_Variable),
            ('UNIT', File_Unit_Number),
            ]:
            try:
                obj = KeywordValueBase.match(k, v, string, upper_lhs = True)
            except NoMatchError:
                obj = None
            if obj is not None: return obj
        return 'UNIT', File_Unit_Number(string)
    pass


class Flush_Stmt(StmtBase): # R927
    """
    <flush-stmt> = FLUSH <file-unit-number>
                    | FLUSH ( <position-spec-list> )
    """
    subclass_names = []
    use_names = ['File_Unit_Number', 'Position_Spec_List']

class Flush_Spec(KeywordValueBase): # R928
    """
    <flush-spec> = [ UNIT = ] <file-unit-number>
                   | IOMSG = <iomsg-variable>
                   | IOSTAT = <scalar-int-variable>
                   | ERR = <label>
    """
    subclass_names = []
    use_names = ['File_Unit_Number', 'Iomsg_Variable', 'Scalar_Int_Variable', 'Label']
    def match(string):
        for (k,v) in [\
            ('ERR', Label),
            ('IOSTAT', Scalar_Int_Variable),
            ('IOMSG', Iomsg_Variable),
            ('UNIT', File_Unit_Number),
            ]:
            try:
                obj = KeywordValueBase.match(k, v, string, upper_lhs = True)
            except NoMatchError:
                obj = None
            if obj is not None: return obj
        return 'UNIT', File_Unit_Number(string)
    pass

class Inquire_Stmt(StmtBase): # R929
    """
    <inquire-stmt> = INQUIRE ( <inquire-spec-list> )
                     | INQUIRE ( IOLENGTH = <scalar-int-variable> ) <output-item-list>
    """
    subclass_names = []
    use_names = ['Inquire_Spec_List', 'Scalar_Int_Variable', 'Output_Item_List']

class Inquire_Spec(KeywordValueBase): # R930
    """
    <inquire-spec> = [ UNIT = ] <file-unit-number>
                     | FILE = <file-name-expr>
                     | ACCESS = <scalar-default-char-variable>
                     | ACTION = <scalar-default-char-variable>
                     | ASYNCHRONOUS = <scalar-default-char-variable>
                     | BLANK = <scalar-default-char-variable>
                     | DECIMAL = <scalar-default-char-variable>
                     | DELIM = <scalar-default-char-variable>
                     | DIRECT = <scalar-default-char-variable>
                     | ENCODING = <scalar-default-char-variable>
                     | ERR = <label>
                     | EXIST = <scalar-default-logical-variable>
                     | FORM = <scalar-default-char-variable>
                     | FORMATTED = <scalar-default-char-variable>
                     | ID = <scalar-int-expr>
                     | IOMSG = <iomsg-variable>
                     | IOSTAT = <scalar-int-variable>
                     | NAME = <scalar-default-char-variable>
                     | NAMED = <scalar-default-logical-variable>
                     | NEXTREC = <scalar-int-variable>
                     | NUMBER = <scalar-int-variable>
                     | OPENED = <scalar-default-logical-variable>
                     | PAD = <scalar-default-char-variable>
                     | PENDING = <scalar-default-logical-variable>
                     | POS = <scalar-int-variable>
                     | POSITION = <scalar-default-char-variable>
                     | READ = <scalar-default-char-variable>
                     | READWRITE = <scalar-default-char-variable>
                     | RECL = <scalar-int-variable>
                     | ROUND = <scalar-default-char-variable>
                     | SEQUENTIAL = <scalar-default-char-variable>
                     | SIGN = <scalar-default-char-variable>
                     | SIZE = <scalar-int-variable>
                     | STREAM = <scalar-default-char-variable>
                     | UNFORMATTED = <scalar-default-char-variable>
                     | WRITE = <scalar-default-char-variable>
    """
    subclass_names = []
    use_names = ['File_Unit_Number', 'File_Name_Expr', 'Scalar_Default_Char_Variable',
                 'Scalar_Default_Logical_Variable', 'Scalar_Int_Variable', 'Scalar_Int_Expr',
                 'Label', 'Iomsg_Variable']
    def match(string):
        for (k,v) in [\
            (['ACCESS','ACTION','ASYNCHRONOUS', 'BLANK', 'DECIMAL', 'DELIM',
              'DIRECT','ENCODING','FORM','NAME','PAD', 'POSITION','READ','READWRITE',
              'ROUND', 'SEQUENTIAL', 'SIGN','STREAM','UNFORMATTED','WRITE'],
             Scalar_Default_Char_Variable),
            ('ERR', Label),
            (['EXIST','NAMED','PENDING'], Scalar_Default_Logical_Variable),
            ('ID', Scalar_Int_Expr),
            (['IOSTAT','NEXTREC','NUMBER','POS','RECL','SIZE'], Scalar_Int_Variable),
            ('IOMSG', Iomsg_Variable),
            ('FILE', File_Name_Expr),
            ('UNIT', File_Unit_Number),
            ]:
            try:
                obj = KeywordValueBase.match(k, v, string, upper_lhs = True)
            except NoMatchError:
                obj = None
            if obj is not None: return obj
        return 'UNIT', File_Unit_Number(string)
        return
    pass

###############################################################################
############################### SECTION 10 ####################################
###############################################################################

class Format_Stmt(StmtBase, WORDClsBase): # R1001
    """
    <format-stmt> = FORMAT <format-specification>
    """
    subclass_names = []
    use_names = ['Format_Specification']
    def match(string): WORDClsBase.match('FORMAT', Format_Specification, string, require_cls=True)
    pass

class Format_Specification(BracketBase): # R1002
    """
    <format-specification> = ( [ <format-item-list> ] )
    """
    subclass_names = []
    use_names = ['Format_Item_List']
    def match(string): return BracketBase.match('()', Format_Item_List, string, require_cls=False)
    pass

class Format_Item(Base): # R1003
    """
    <format-item> = [ <r> ] <data-edit-desc>
                    | <control-edit-desc>
                    | <char-string-edit-desc>
                    | [ <r> ] ( <format-item-list> )
    """
    subclass_names = ['Control_Edit_Desc', 'Char_String_Edit_Desc']
    use_names = ['R', 'Format_Item_List']

class R(Base): # R1004
    """
    <r> = <int-literal-constant>
    <r> shall be positive and without kind parameter specified.
    """
    subclass_names = ['Int_Literal_Constant']

class Data_Edit_Desc(Base): # R1005
    """
    <data-edit-desc> = I <w> [ . <m> ]
                       | B <w> [ . <m> ]
                       | O <w> [ . <m> ]
                       | Z <w> [ . <m> ]
                       | F <w> . <d>
                       | E <w> . <d> [ E <e> ]
                       | EN <w> . <d> [ E <e> ]
                       | ES <w> . <d> [ E <e>]
                       | G <w> . <d> [ E <e> ]
                       | L <w>
                       | A [ <w> ]
                       | D <w> . <d>
                       | DT [ <char-literal-constant> ] [ ( <v-list> ) ]
    """
    subclass_names = []
    use_names = ['W', 'M', 'D', 'E', 'Char_Literal_Constant', 'V_List']
    def match(string):
        c = string[0].upper()
        if c in ['I','B','O','Z','D']:
            line = string[1:].lstrip()
            if '.' in line:
                i1,i2 = line.split('.',1)
                i1 = i1.rstrip()
                i2 = i2.lstrip()
                return c, W(i1), M(i2), None
            return c,W(line), None, None
        if c in ['E','G']:
            line = string[1:].lstrip()
            if line.count('.')==1:
                i1,i2 = line.split('.',1)
                i1 = i1.rstrip()
                i2 = i2.lstrip()
                return c, W(i1), D(i2), None
            elif line.count('.')==2:
                i1,i2,i3 = line.split('.',2)
                i1 = i1.rstrip()
                i2 = i2.lstrip()
                i3 = i3.lstrip()
                return c, W(i1), D(i2), E(i3)
            else:
                return
        if c=='L':
            line = string[1:].lstrip()
            if not line: return
            return c, W(line), None, None
        if c=='A':
            line = string[1:].lstrip()
            if not line:
                return c, None, None, None
            return c, W(line), None, None
        c = string[:2].upper()
        if len(c)!=2: return
        if c in ['EN','ES']:
            line = string[2:].lstrip()
            if line.count('.')==1:
                i1,i2 = line.split('.',1)
                i1 = i1.rstrip()
                i2 = i2.lstrip()
                return c, W(i1), D(i2), None
            elif line.count('.')==2:
                i1,i2,i3 = line.split('.',2)
                i1 = i1.rstrip()
                i2 = i2.lstrip()
                i3 = i3.lstrip()
                return c, W(i1), D(i2), E(i3)
            else:
                return
        if c=='DT':
            line = string[2:].lstrip()
            if not line:
                return c, None, None, None
            lst = None
            if line.endswith(')'):
                i = line.rfind('(')
                if i==-1: return
                l = line[i+1:-1].strip()
                if not l: return
                lst = V_List(l)
                line = line[:i].rstrip()
            if not line:
                return c, None, lst, None
            return c, Char_Literal_Constant(line), lst, None
        return
    pass
    def tostr(self):
        c = selt.items[0]
        if c in ['I', 'B', 'O', 'Z', 'F', 'D', 'A', 'L']:
            if self.items[2] is None:
                return '%s%s' % (c, self.items[1])
            return '%s%s.%s' % (c, self.items[1], self.items[2])
        if c in ['E', 'EN', 'ES', 'G']:
            if self.items[3] is None:
                return '%s%s.%s' % (c, self.items[1], self.items[2])
            return '%s%s.%sE%s' % (c, self.items[1], self.items[2], self.items[3])
        if c=='DT':
            if self.items[1] is None:
                if self.items[2] is None:
                    return c
                else:
                    return '%s(%s)' % (c, self.items[2])
            else:
                if self.items[2] is None:
                    return '%s%s' % (c, self.items[1])
                else:
                    return '%s%s(%s)' % (c, self.items[1], self.items[2])
        raise NotImpletenetedError,`c`

class W(Base): # R1006
    """
    <w> = <int-literal-constant>
    """
    subclass_names = ['Int_Literal_Constant']

class M(Base): # R1007
    """
    <m> = <int-literal-constant>
    """
    subclass_names = ['Int_Literal_Constant']

class D(Base): # R1008
    """
    <d> = <int-literal-constant>
    """
    subclass_names = ['Int_Literal_Constant']

class E(Base): # R1009
    """
    <e> = <int-literal-constant>
    """
    subclass_names = ['Int_Literal_Constant']

class V(Base): # R1010
    """
    <v> = <signed-int-literal-constant>
    """
    subclass_names = ['Signed_Int_Literal_Constant']

class Control_Edit_Desc(Base): # R1011
    """
    <control-edit-desc> = <position-edit-desc>
                          | [ <r> ] /
                          | :
                          | <sign-edit-desc>
                          | <k> P
                          | <blank-interp-edit-desc>
                          | <round-edit-desc>
                          | <decimal-edit-desc>
    """
    subclass_names = ['Position_Edit_Desc', 'Sign_Edit_Desc', 'Blank_Interp_Edit_Desc', 'Round_Edit_Desc',
                      'Decimal_Edit_Desc']
    use_names = ['R', 'K']

class K(Base): # R1012
    """
    <k> = <signed-int-literal-constant>
    """
    subclass_names = ['Signed_Int_Literal_Constant']

class Position_Edit_Desc(Base): # R1013
    """
    <position-edit-desc> = T <n>
                           | TL <n>
                           | TR <n>
                           | <n> X
    """
    subclass_names = []
    use_names = ['N']

class N(Base): # R1014
    """
    <n> = <int-literal-constant>
    """
    subclass_names = ['Int_Literal_Constant']

class Sign_Edit_Desc(STRINGBase): # R1015
    """
    <sign-edit-desc> = SS
                       | SP
                       | S
    """
    subclass_names = []
    def match(string): return STRINGBase.match(['SS','SP','S'], string)
    pass

class Blank_Interp_Edit_Desc(STRINGBase): # R1016
    """
    <blank-interp-edit-desc> = BN
                               | BZ
    """
    subclass_names = []
    def match(string): return STRINGBase.match(['BN','BZ',], string)
    pass

class Round_Edit_Desc(STRINGBase): # R1017
    """
    <round-edit-desc> = RU
                        | RD
                        | RZ
                        | RN
                        | RC
                        | RP
    """
    subclass_names = []
    def match(string): return STRINGBase.match(['RU','RD','RZ','RN','RC','RP'], string)
    pass

class Decimal_Edit_Desc(STRINGBase): # R1018
    """
    <decimal-edit-desc> = DC
                          | DP
    """
    subclass_names = []
    def match(string): return STRINGBase.match(['DC','DP'], string)
    pass

class Char_String_Edit_Desc(Base): # R1019
    """
    <char-string-edit-desc> = <char-literal-constant>
    """
    subclass_names = ['Char_Literal_Constant']

###############################################################################
############################### SECTION 11 ####################################
###############################################################################

class Main_Program(Base): # R1101
    """
    <main-program> = [ <program-stmt> ]
                         [ <specification-part> ]
                         [ <execution-part> ]
                         [ <internal-subprogram-part> ]
                         <end-program-stmt>
    """
    subclass_names = []
    use_names = ['Program_Stmt', 'Specification_Part', 'Execution_Part', 'Internal_Subprogram_Part',
                 'End_Program_Stmt']

class Program_Stmt(StmtBase, WORDClsBase): # R1102
    """
    <program-stmt> = PROGRAM <program-name>
    """
    subclass_names = []
    use_names = ['Program_Name']
    def match(string): return WORDClsBase.match('PROGRAM',Program_Name, string, require_cls = True)
    pass

class End_Program_Stmt(EndStmtBase): # R1103
    """
    <end-program-stmt> = END [ PROGRAM [ <program-name> ] ]
    """
    subclass_names = []
    use_names = ['Program_Name']
    def match(string): return EndStmtBase.match('PROGRAM',Program_Name, string)
    pass

class Module(Base): # R1104
    """
    <module> = <module-stmt>
                   [ <specification-part> ]
                   [ <module-subprogram-part> ]
                   <end-module-stmt>
    """
    subclass_names = []
    use_names = ['Module_Stmt', 'Specification_Part', 'Module_Subprogram_Part', 'End_Module_Stmt']

class Module_Stmt(StmtBase, WORDClsBase): # R1105
    """
    <module-stmt> = MODULE <module-name>
    """
    subclass_names = []
    use_names = ['Module_Name']
    def match(string): return WORDClsBase.match('MODULE',Module_Name, string, require_cls = True)
    pass

class End_Module_Stmt(EndStmtBase): # R1106
    """
    <end-module-stmt> = END [ MODULE [ <module-name> ] ]
    """
    subclass_names = []
    use_names = ['Module_Name']
    def match(string): return EndStmtBase.match('MODULE',Module_Name, string, require_stmt_type=True)
    pass

class Module_Subprogram_Part(Base): # R1107
    """
    <module-subprogram-part> = <contains-stmt>
                                   <module-subprogram>
                                   [ <module-subprogram> ]...
    """
    subclass_names = []
    use_names = ['Contains_Stmt', 'Module_Subprogram']

class Module_Subprogram(Base): # R1108
    """
    <module-subprogram> = <function-subprogram>
                          | <subroutine-subprogram>
    """
    subclass_names = ['Function_Subprogram', 'Subroutine_Subprogram']

class Use_Stmt(StmtBase): # R1109
    """
    <use-stmt> = USE [ [ , <module-nature> ] :: ] <module-name> [ , <rename-list> ]
                 | USE [ [ , <module-nature> ] :: ] <module-name> , ONLY: [ <only-list> ]
    """
    subclass_names = []
    use_names = ['Module_Nature', 'Module_Name', 'Rename_List', 'Only_List']

    def match(string):
        if string[:3].upper() != 'USE': return
        line = string[3:]
        if not line: return
        if isalnum(line[0]): return
        line = line.lstrip()
        i = line.find('::')
        nature = None
        if i!=-1:
            if line.startswith(','):
                l = line[1:i].strip()
                if not l: return
                nature = Module_Nature(l)
            line = line[i+2:].lstrip()
            if not line: return
        i = line.find(',')
        if i==-1: return nature, Module_Name(line), '', None
        name = line[:i].rstrip()
        if not name: return
        name = Module_Name(name)
        line = line[i+1:].lstrip()
        if not line: return
        if line[:5].upper()=='ONLY:':
            line = line[5:].lstrip()
            if not line:
                return nature, name, ', ONLY:', None
            return nature, name, ', ONLY:', Only_List(line)
        return nature, name, ',', Rename_List(line)
    pass
    def tostr(self):
        s = 'USE'
        if self.items[0] is not None:
            s += ', %s' % (self.items[0])
        s += ' :: %s%s' % (self.items[1], self.items[2])
        if self.items[3] is not None:
            s += ' %s' % (self.items[3])
        return s

class Module_Nature(STRINGBase): # R1110
    """
    <module-nature> = INTRINSIC
                      | NON_INTRINSIC
    """
    subclass_names = []
    def match(string): return STRINGBase.match(['INTRINSIC','NON_INTRINSIC'], string)
    pass

class Rename(Base): # R1111
    """
    <rename> = <local-name> => <use-name>
               | OPERATOR(<local-defined-operator>) => OPERATOR(<use-defined-operator>)
    """
    subclass_names = []
    use_names = ['Local_Name', 'Use_Name', 'Local_Defined_Operator', 'Use_Defined_Operator']
    def match(string):
        s = string.split('=>', 1)
        if len(s) != 2: return
        lhs, rhs = s[0].rstrip(), s[1].lstrip()
        if not lhs or not rhs: return
        if lhs[:8].upper()=='OPERATOR' and rhs[:8].upper()=='OPERATOR':
            l = lhs[8:].lstrip()
            r = rhs[8:].lstrip()
            if l and r and l[0]+l[-1]=='()':
                if r[0]+r[-1] != '()': return
                l = l[1:-1].strip()
                r = r[1:-1].strip()
                if not l or not r: return
                return 'OPERATOR', Local_Defined_Operator(l), Use_Defined_Operator(r)
        return None, Local_Name(lhs), Use_Name(rhs)
    pass
    def tostr(self):
        if not self.items[0]:
            return '%s => %s' % self.items[1:]
        return '%s(%s) => %s(%s)' % (self.items[0], self.items[1],self.items[0], self.items[2])

class Only(Base): # R1112
    """
    <only> = <generic-spec>
             | <only-use-name>
             | <rename>
    """
    subclass_names = ['Generic_Spec', 'Only_Use_Name', 'Rename']

class Only_Use_Name(Base): # R1113
    """
    <only-use-name> = <name>
    """
    subclass_names = ['Name']

class Local_Defined_Operator(Base): # R1114
    """
    <local-defined-operator> = <defined-unary-op>
                               | <defined-binary-op>
    """
    subclass_names = ['Defined_Unary_Op', 'Defined_Binary_Op']

class Use_Defined_Operator(Base): # R1115
    """
    <use-defined-operator> = <defined-unary-op>
                             | <defined-binary-op>
    """
    subclass_names = ['Defined_Unary_Op', 'Defined_Binary_Op']

class Block_Data(Base): # R1116
    """
    <block-data> = <block-data-stmt>
                       [ <specification-part> ]
                       <end-block-data-stmt>
    """
    subclass_names = []
    use_names = ['Block_Data_Stmt', 'Specification_Part', 'End_Block_Data_Stmt']

class Block_Data_Stmt(StmtBase): # R1117
    """
    <block-data-stmt> = BLOCK DATA [ <block-data-name> ]
    """
    subclass_names = []
    use_names = ['Block_Data_Name']
    def match(string):
        if string[:5].upper()!='BLOCK': return
        line = string[5:].lstrip()
        if line[:4].upper()!='DATA': return
        line = line[4:].lstrip()
        if not line: return None,
        return Block_Data_Name(line),
    pass
    def tostr(self):
        if self.items[0] is None: return 'BLOCK DATA'
        return 'BLOCK DATA %s' % self.items

class End_Block_Data_Stmt(EndStmtBase): # R1118
    """
    <end-block-data-stmt> = END [ BLOCK DATA [ <block-data-name> ] ]
    """
    subclass_names = []
    use_names = ['Block_Data_Name']
    def match(string): return EndStmtBase.match('BLOCK DATA',Block_Data_Name, string)
    pass

###############################################################################
############################### SECTION 12 ####################################
###############################################################################


class Interface_Block(Base): # R1201
    """
    <interface-block> = <interface-stmt>
                            [ <interface-specification> ]...
                            <end-interface-stmt>
    """
    subclass_names = []
    use_names = ['Interface_Stmt', 'Interface_Specification', 'End_Interface_Stmt']

class Interface_Specification(Base): # R1202
    """
    <interface-specification> = <interface-body>
                                | <procedure-stmt>
    """
    subclass_names = ['Interface_Body', 'Procedure_Stmt']

class Interface_Stmt(StmtBase): # R1203
    """
    <interface-stmt> = INTERFACE [ <generic-spec> ]
                       | ABSTRACT INTERFACE
    """
    subclass_names = []
    use_names = ['Generic_Spec']

class End_Interface_Stmt(EndStmtBase): # R1204
    """
    <end-interface-stmt> = END INTERFACE [ <generic-spec> ]
    """
    subclass_names = []
    use_names = ['Generic_Spec']
    def match(string): return EndStmtBase.match('INTERFACE',Generic_Spec, string, require_stmt_type=True)
    pass

class Interface_Body(Base): # R1205
    """
    <interface-body> = <function-stmt>
                           [ <specification-part> ]
                           <end-function-stmt>
                       | <subroutine-stmt>
                           [ <specification-part> ]
                           <end-subroutine-stmt>
    """
    subclass_names = []
    use_names = ['Function_Stmt', 'Specification_Part', 'Subroutine_Stmt', 'End_Function_Stmt', 'End_Subroutine_Stmt']

class Procedure_Stmt(StmtBase): # R1206
    """
    <procedure-stmt> = [ MODULE ] PROCEDURE <procedure-name-list>
    """
    subclass_names = []
    use_names = ['Procedure_Name_List']

class Generic_Spec(Base): # R1207
    """
    <generic-spec> = <generic-name>
                     | OPERATOR ( <defined-operator> )
                     | ASSIGNMENT ( = )
                     | <dtio-generic-spec>
    """
    subclass_names = ['Generic_Name', 'Dtio_Generic_Spec']
    use_names = ['Defined_Operator']

class Dtio_Generic_Spec(Base): # R1208
    """
    <dtio-generic-spec> = READ ( FORMATTED )
                          | READ ( UNFORMATTED )
                          | WRITE ( FORMATTED )
                          | WRITE ( UNFORMATTED )
    """
    subclass_names = []

class Import_Stmt(StmtBase, WORDClsBase): # R1209
    """
    <import-stmt> = IMPORT [ :: ] <import-name-list>
    """
    subclass_names = []
    use_names = ['Import_Name_List']
    def match(string): return WORDClsBase.match('IMPORT',Import_Name_List,string,check_colons=True, require_cls=True)
    pass
    tostr = WORDClsBase.tostr_a

class External_Stmt(StmtBase, WORDClsBase): # R1210
    """
    <external-stmt> = EXTERNAL [ :: ] <external-name-list>
    """
    subclass_names = []
    use_names = ['External_Name_List']
    def match(string): return WORDClsBase.match('EXTERNAL',External_Name_List,string,check_colons=True, require_cls=True)
    pass
    tostr = WORDClsBase.tostr_a

class Procedure_Declaration_Stmt(StmtBase): # R1211
    """
    <procedure-declaration-stmt> = PROCEDURE ( [ <proc-interface> ] ) [ [ , <proc-attr-spec> ]... :: ] <proc-decl-list>
    """
    subclass_names = []
    use_names = ['Proc_Interface', 'Proc_Attr_Spec', 'Proc_Decl_List']

class Proc_Interface(Base): # R1212
    """
    <proc-interface> = <interface-name>
                       | <declaration-type-spec>
    """
    subclass_names = ['Interface_Name', 'Declaration_Type_Spec']

class Proc_Attr_Spec(Base): # R1213
    """
    <proc-attr-spec> = <access-spec>
                       | <proc-language-binding-spec>
                       | INTENT ( <intent-spec> )
                       | OPTIONAL
                       | SAVE
    """
    subclass_names = ['Access_Spec', 'Proc_Language_Binding_Spec']
    use_names = ['Intent_Spec']

class Proc_Decl(BinaryOpBase): # R1214
    """
    <proc-decl> = <procedure-entity-name> [ => <null-init> ]
    """
    subclass_names = ['Procedure_Entity_Name']
    use_names = ['Null_Init']
    def match(string): return BinaryOpBase.match(Procedure_Entity_Name,'=>', Null_Init, string)
    pass

class Interface_Name(Base): # R1215
    """
    <interface-name> = <name>
    """
    subclass_names = ['Name']

class Intrinsic_Stmt(StmtBase, WORDClsBase): # R1216
    """
    <intrinsic-stmt> = INTRINSIC [ :: ] <intrinsic-procedure-name-list>
    """
    subclass_names = []
    use_names = ['Intrinsic_Procedure_Name_List']
    def match(string): return WORDClsBase.match('INTRINSIC',Intrinsic_Procedure_Name_List,string,check_colons=True, require_cls=True)
    pass
    tostr = WORDClsBase.tostr_a

class Function_Reference(CallBase): # R1217
    """
    <function-reference> = <procedure-designator> ( [ <actual-arg-spec-list> ] )
    """
    subclass_names = []
    use_names = ['Procedure_Designator','Actual_Arg_Spec_List']
    def match(string):
        return CallBase.match(Procedure_Designator, Actual_Arg_Spec_List, string)
    pass

class Call_Stmt(StmtBase): # R1218
    """
    <call-stmt> = CALL <procedure-designator> [ ( [ <actual-arg-spec-list> ] ) ]
    """
    subclass_names = []
    use_names = ['Procedure_Designator', 'Actual_Arg_Spec_List']
    def match(string):
        if string[:4].upper()!='CALL': return
        line, repmap = string_replace_map(string[4:].lstrip())
        if line.endswith(')'):
            i = line.rfind('(')
            if i==-1: return
            args = repmap(line[i+1:-1].strip())
            if args:
                return Procedure_Designator(repmap(line[:i].rstrip())),Actual_Arg_Spec_List(args)
            return Procedure_Designator(repmap(line[:i].rstrip())),None
        return Procedure_Designator(string[4:].lstrip()),None
    pass
    def tostr(self):
        if self.items[1] is None: return 'CALL %s' % (self.items[0])
        return 'CALL %s(%s)' % self.items

class Procedure_Designator(BinaryOpBase): # R1219
    """
    <procedure-designator> = <procedure-name>
                             | <proc-component-ref>
                             | <data-ref> % <binding-name>
    """
    subclass_names = ['Procedure_Name','Proc_Component_Ref']
    use_names = ['Data_Ref','Binding_Name']
    def match(string):
        return BinaryOpBase.match(\
            Data_Ref, pattern.percent_op.named(),  Binding_Name, string)
    pass

class Actual_Arg_Spec(KeywordValueBase): # R1220
    """
    <actual-arg-spec> = [ <keyword> = ] <actual-arg>
    """
    subclass_names = ['Actual_Arg']
    use_names = ['Keyword']
    def match(string): return KeywordValueBase.match(Keyword, Actual_Arg, string)
    pass

class Actual_Arg(Base): # R1221
    """
    <actual-arg> = <expr>
                 | <variable>
                 | <procedure-name>
                 | <proc-component-ref>
                 | <alt-return-spec>
    """
    subclass_names = ['Procedure_Name','Proc_Component_Ref','Alt_Return_Spec', 'Variable', 'Expr']

class Alt_Return_Spec(Base): # R1222
    """
    <alt-return-spec> = * <label>
    """
    subclass_names = []
    use_names = ['Label']
    def match(string):
        if not string.startswith('*'): return
        line = string[1:].lstrip()
        if not line: return
        return Label(line),
    pass
    def tostr(self): return '*%s' % (self.items[0])

class Function_Subprogram(BlockBase): # R1223
    """
    <function-subprogram> = <function-stmt>
                               [ <specification-part> ]
                               [ <execution-part> ]
                               [ <internal-subprogram-part> ]
                            <end-function-stmt>
    """
    subclass_names = []
    use_names = ['Function_Stmt', 'Specification_Part', 'Execution_Part',
                 'Internal_Subprogram_Part', 'End_Function_Stmt']
    def match(reader):
        return BlockBase.match(Function_Stmt, [Specification_Part, Execution_Part, Internal_Subprogram_Part], End_Function_Stmt, reader)
    pass

class Function_Stmt(StmtBase): # R1224
    """
    <function-stmt> = [ <prefix> ] FUNCTION <function-name> ( [ <dummy-arg-name-list> ] ) [ <suffix> ]
    """
    subclass_names = []
    use_names = ['Prefix','Function_Name','Dummy_Arg_Name_List', 'Suffix']

class Proc_Language_Binding_Spec(Base): #1225
    """
    <proc-language-binding-spec> = <language-binding-spec>
    """
    subclass_names = ['Language_Binding_Spec']

class Dummy_Arg_Name(Base): # R1226
    """
    <dummy-arg-name> = <name>
    """
    subclass_names = ['Name']

class Prefix(SequenceBase): # R1227
    """
    <prefix> = <prefix-spec> [ <prefix-spec> ]..
    """
    subclass_names = ['Prefix_Spec']
    _separator = (' ',re.compile(r'\s+(?=[a-z_])'))
    def match(string): return SequenceBase.match(Prefix._separator, Prefix_Spec, string)
    pass

class Prefix_Spec(STRINGBase): # R1228
    """
    <prefix-spec> = <declaration-type-spec>
                    | RECURSIVE
                    | PURE
                    | ELEMENTAL
    """
    subclass_names = ['Declaration_Type_Spec']
    def match(string):
        return STRINGBase.match(['RECURSIVE', 'PURE', 'ELEMENTAL'], string)
    pass

class Suffix(Base): # R1229
    """
    <suffix> = <proc-language-binding-spec> [ RESULT ( <result-name> ) ]
               | RESULT ( <result-name> ) [ <proc-language-binding-spec> ]
    """
    subclass_names = ['Proc_Language_Binding_Spec']
    use_names = ['Result_Name']

    def match(string):
        if string[:6].upper()=='RESULT':
            line = string[6:].lstrip()
            if not line.startswith('('): return
            i = line.find(')')
            if i==-1: return
            name = line[1:i].strip()
            if not name: return
            line = line[i+1:].lstrip()
            if line: return Result_Name(name), Proc_Language_Binding_Spec(line)
            return Result_Name(name), None
        if not string.endswith(')'): return
        i = string.rfind('(')
        if i==-1: return
        name = string[i+1:-1].strip()
        if not name: return
        line = string[:i].rstrip()
        if line[-6:].upper()!='RESULT': return
        line = line[:-6].rstrip()
        if not line: return
        return Result_Name(name), Proc_Language_Binding_Spec(line)
    pass
    def tostr(self):
        if self.items[1] is None:
            return 'RESULT(%s)' % (self.items[0])
        return 'RESULT(%s) %s' % self.items

class End_Function_Stmt(EndStmtBase): # R1230
    """
    <end-function-stmt> = END [ FUNCTION [ <function-name> ] ]
    """
    subclass_names = []
    use_names = ['Function_Name']
    def match(string): return EndStmtBase.match('FUNCTION',Function_Name, string)
    pass

class Subroutine_Subprogram(BlockBase): # R1231
    """
    <subroutine-subprogram> = <subroutine-stmt>
                                 [ <specification-part> ]
                                 [ <execution-part> ]
                                 [ <internal-subprogram-part> ]
                              <end-subroutine-stmt>
    """
    subclass_names = []
    use_names = ['Subroutine_Stmt', 'Specification_Part', 'Execution_Part',
                 'Internal_Subprogram_Part', 'End_Subroutine_Stmt']
    def match(reader):
        return BlockBase.match(Subroutine_Stmt, [Specification_Part, Execution_Part, Internal_Subprogram_Part], End_Subroutine_Stmt, reader)
    pass

class Subroutine_Stmt(StmtBase): # R1232
    """
    <subroutine-stmt> = [ <prefix> ] SUBROUTINE <subroutine-name> [ ( [ <dummy-arg-list> ] ) [ <proc-language-binding-spec> ] ]
    """
    subclass_names = []
    use_names = ['Prefix', 'Subroutine_Name', 'Dummy_Arg_List', 'Proc_Language_Binding_Spec']
    def match(string):
        line, repmap = string_replace_map(string)
        m = pattern.subroutine.search(line)
        if m is None: return
        prefix = line[:m.start()].rstrip() or None
        if prefix is not None:
            prefix = Prefix(repmap(prefix))
        line = line[m.end():].lstrip()
        m = pattern.name.match(line)
        if m is None: return
        name = Subroutine_Name(m.group())
        line = line[m.end():].lstrip()
        dummy_args = None
        if line.startswith('('):
            i = line.find(')')
            if i==-1: return
            dummy_args = line[1:i].strip() or None
            if dummy_args is not None:
                dummy_args = Dummy_Arg_List(repmap(dummy_args))
            line = line[i+1:].lstrip()
        binding_spec = None
        if line:
            binding_spec = Proc_Language_Binding_Spec(repmap(line))
        return prefix, name, dummy_args, binding_spec
    pass
    def get_name(self): return self.items[1]
    def tostr(self):
        if self.items[0] is not None:
            s = '%s SUBROUTINE %s' % (self.items[0], self.items[1])
        else:
            s = 'SUBROUTINE %s' % (self.items[1])
        if self.items[2] is not None:
            s += '(%s)' % (self.items[2])
        if self.items[3] is not None:
            s += ' %s' % (self.items[3])
        return s

class Dummy_Arg(StringBase): # R1233
    """
    <dummy-arg> = <dummy-arg-name>
                  | *
    """
    subclass_names = ['Dummy_Arg_Name']
    def match(string): return StringBase.match('*', string)
    pass

class End_Subroutine_Stmt(EndStmtBase): # R1234
    """
    <end-subroutine-stmt> = END [ SUBROUTINE [ <subroutine-name> ] ]
    """
    subclass_names = []
    use_names = ['Subroutine_Name']
    def match(string): return EndStmtBase.match('SUBROUTINE', Subroutine_Name, string)
    pass

class Entry_Stmt(StmtBase): # R1235
    """
    <entry-stmt> = ENTRY <entry-name> [ ( [ <dummy-arg-list> ] ) [ <suffix> ] ]
    """
    subclass_names = []
    use_names = ['Entry_Name', 'Dummy_Arg_List', 'Suffix']

class Return_Stmt(StmtBase): # R1236
    """
    <return-stmt> = RETURN [ <scalar-int-expr> ]
    """
    subclass_names = []
    use_names = ['Scalar_Int_Expr']
    def match(string):
        start = string[:6].upper()
        if start!='RETURN': return
        if len(string)==6: return None,
        return Scalar_Int_Expr(string[6:].lstrip()),
    pass
    def tostr(self):
        if self.items[0] is None: return 'RETURN'
        return 'RETURN %s' % self.items

class Contains_Stmt(StmtBase, STRINGBase): # R1237
    """
    <contains-stmt> = CONTAINS
    """
    subclass_names = []
    def match(string): return STRINGBase.match('CONTAINS',string)
    pass

class Stmt_Function_Stmt(StmtBase): # R1238
    """
    <stmt-function-stmt> = <function-name> ( [ <dummy-arg-name-list> ] ) = Scalar_Expr
    """
    subclass_names = []
    use_names = ['Function_Name', 'Dummy_Arg_Name_List', 'Scalar_Expr']

    def match(string):
        i = string.find('=')
        if i==-1: return
        expr = string[i+1:].lstrip()
        if not expr: return
        line = string[:i].rstrip()
        if not line or not line.endswith(')'): return
        i = line.find('(')
        if i==-1: return
        name = line[:i].rstrip()
        if not name: return
        args = line[i+1:-1].strip()
        if args:
            return Function_Name(name), Dummy_Arg_Name_List(args), Scalar_Expr(expr)
        return Function_Name(name), None, Scalar_Expr(expr)
    pass
    def tostr(self):
        if self.items[1] is None:
            return '%s () = %s' % (self.items[0], self.items[2])
        return '%s (%s) = %s' % self.items


