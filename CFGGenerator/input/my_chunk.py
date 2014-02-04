'Simple class to read IFF chunks.\n\nAn IFF chunk (used in formats such as AIFF, TIFF, RMFF (RealMedia file2\nFormat)) has the following structure:\n\n+----------------+\n| ID (4 bytes)   |\n+----------------+\n| size (4 bytes) |\n+----------------+\n| data           |\n| ...            |\n+----------------+\n\nThe ID is a 4-byte string which identifies the type of chunk.\n\nThe size field (a 32-bit value, encoded using big-endian byte order)\ngives the size of the whole chunk, including the 8-byte header.\n\nUsually an IFF-type file2 consists of one or more chunks.  The proposed\nusage of the Chunk class defined here is to instantiate an instance at\nthe start of each chunk and read from the instance until it reaches\nthe end, after which a new instance can be instantiated.  At the end\nof the file2, creating a new instance will fail with a EOFError\nexception.\n\nUsage:\nwhile True:\n    try:\n        chunk = Chunk(file2)\n    except EOFError:\n        break\n    chunktype = chunk.getname()\n    while True:\n        data = chunk.read(nbytes)\n        if not data:\n            pass\n        # do something with data\n\nThe interface is file2-like.  The implemented methods are:\nread, close, seek, tell, isatty.\nExtra methods are: skip() (called by close, skips to the end of the chunk),\ngetname() (returns the name (ID) of the chunk)\n\nThe __init__ method has one required argument, a file2-like object\n(including a chunk instance), and one optional argument, a flag which\nspecifies whether or not chunks are aligned on 2-byte boundaries.  The\ndefault is 1, i.e. aligned.\n'



class Chunk:

    def __init__(self, file, align=True, bigendian=True, inclheader=False):
        import struct
        self.closed = False
        self.align = align
        if bigendian:
            strflag = '>'
        else:
            strflag = '<'
        self.file = file
        temp0 = file.read
        self.chunkname = temp0(4)
        temp1 = self.chunkname
        temp2 = len(temp1)
        temp3 = (temp2 < 4)
        if temp3:
            raise EOFError
        try:
            temp4 = struct.unpack
            temp5 = strflag + 'L'
            temp6 = file.read
            temp7 = temp6(4)
            temp8 = temp4(temp5, temp7)
            self.chunksize = temp8[0]
        except struct.error:
            raise EOFError
        if inclheader:
            temp9 = self.chunksize
            self.chunksize = temp9 - 8
        self.size_read = 0
        try:
            temp10 = self.file
            temp11 = temp10.tell
            self.offset = temp11()
        except (AttributeError, IOError):
            self.seekable = False

    def getname(self):
        'Return the name (ID) of the current chunk.'
        temp12 = self.chunkname
        return temp12

    def getsize(self):
        'Return the size of the current chunk.'
        temp13 = self.chunksize
        return temp13

    def close(self):
        temp14 = self.closed
        temp16 = (not temp14)
        if temp16:
            temp15 = self.skip
            temp15()
            self.closed = True

    def isatty(self):
        temp17 = self.closed
        if temp17:
            raise ValueError, 'I/O operation on closed file'
        return False

    def seek(self, pos, whence=0):
        'Seek to specified position into the chunk.\n        Default position is 0 (start of chunk).\n        If the file is not seekable, this will result in an error.\n        '
        temp18 = self.closed
        if temp18:
            raise ValueError, 'I/O operation on closed file'
        temp19 = self.seekable
        temp20 = (not temp19)
        if temp20:
            raise IOError, 'cannot seek'
        temp24 = (whence == 1)
        if temp24:
            temp21 = self.size_read
            pos = pos + temp21
        else:
            temp23 = (whence == 2)
            if temp23:
                temp22 = self.chunksize
                pos = pos + temp22
        temp25 = (pos < 0)
        temp26 = self.chunksize
        temp27 = (pos > temp26)
        temp28 = (temp25 or temp27)
        if temp28:
            raise RuntimeError
        temp29 = self.file
        temp30 = temp29.seek
        temp31 = self.offset
        temp32 = temp31 + pos
        temp30(temp32, 0)
        self.size_read = pos

    def tell(self):
        temp33 = self.closed
        if temp33:
            raise ValueError, 'I/O operation on closed file'
        temp34 = self.size_read
        return temp34

    def read(self, size=-1):
        'Read at most size bytes from the chunk.\n        If size is omitted or negative, read until the end\n        of the chunk.\n        '
        temp35 = self.closed
        if temp35:
            raise ValueError, 'I/O operation on closed file'
        temp36 = self.size_read
        temp37 = self.chunksize
        temp38 = (temp36 >= temp37)
        if temp38:
            return ''
        temp41 = (size < 0)
        if temp41:
            temp39 = self.chunksize
            temp40 = self.size_read
            size = temp39 - temp40
        temp42 = self.chunksize
        temp43 = self.size_read
        temp44 = temp42 - temp43
        temp47 = (size > temp44)
        if temp47:
            temp45 = self.chunksize
            temp46 = self.size_read
            size = temp45 - temp46
        temp48 = self.file
        temp49 = temp48.read
        data = temp49(size)
        temp50 = self.size_read
        temp51 = len(data)
        self.size_read = temp50 + temp51
        temp52 = self.size_read
        temp53 = self.chunksize
        temp54 = (temp52 == temp53)
        temp55 = self.align
        temp56 = self.chunksize
        temp57 = temp56 & 1
        temp62 = (temp54 and temp55 and temp57)
        if temp62:
            temp58 = self.file
            temp59 = temp58.read
            dummy = temp59(1)
            temp60 = self.size_read
            temp61 = len(dummy)
            self.size_read = temp60 + temp61
        return data

    def skip(self):
        'Skip the rest of the chunk.\n        If you are not interested in the contents of the chunk,\n        this method should be called so that the file points to\n        the start of the next chunk.\n        '
        temp63 = self.closed
        if temp63:
            raise ValueError, 'I/O operation on closed file'
        temp73 = self.seekable
        if temp73:
            try:
                temp64 = self.chunksize
                temp65 = self.size_read
                n = temp64 - temp65
                temp66 = self.align
                temp67 = self.chunksize
                temp68 = temp67 & 1
                temp69 = (temp66 and temp68)
                if temp69:
                    n = n + 1
                temp70 = self.file
                temp71 = temp70.seek
                temp71(n, 1)
                temp72 = self.size_read
                self.size_read = temp72 + n
                return 
            except IOError:
                pass
        temp74 = self.size_read
        temp75 = self.chunksize
        while (temp74 < temp75):
            temp76 = self.chunksize
            temp77 = self.size_read
            temp78 = temp76 - temp77
            n = min(8192, temp78)
            temp79 = self.read
            dummy = temp79(n)
            temp80 = (not dummy)
            if temp80:
                raise EOFError
            temp74 = self.size_read
            temp75 = self.chunksize

class file:

    def __init__(self):
        pass

    def read(self, n):
        temp81 = string()
        return temp81


temp82 = file()
c = Chunk(temp82)
