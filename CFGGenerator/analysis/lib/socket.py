# Wrapper module for _socket, providing some additional facilities
# implemented in Python.

"""\
This module provides socket operations and some related functions.
On Unix, it supports IP (Internet Protocol) and Unix domain sockets.
On other systems, it only supports IP. Functions specific for a
socket are available as methods of the socket object.

Functions:

socket() -- create a new socket object
socketpair() -- create a pair of new socket objects [*]
fromfd() -- create a socket object from an open file descriptor [*]
gethostname() -- return the current hostname
gethostbyname() -- map a hostname to its IP number
gethostbyaddr() -- map an IP number or hostname to DNS info
getservbyname() -- map a service name and a protocol name to a port number
getprotobyname() -- mape a protocol name (e.g. 'tcp') to a number
ntohs(), ntohl() -- convert 16, 32 bit int from network to host byte order
htons(), htonl() -- convert 16, 32 bit int from host to network byte order
inet_aton() -- convert IP addr string (123.45.67.89) to 32-bit packed format
inet_ntoa() -- convert 32-bit packed format IP to string (123.45.67.89)
ssl() -- secure socket layer support (only available if configured)
socket.getdefaulttimeout() -- get the default timeout value
socket.setdefaulttimeout() -- set the default timeout value

 [*] not available on all platforms!

Special objects:

SocketType -- type object for socket objects
error -- exception raised for I/O errors
has_ipv6 -- boolean value indicating if IPv6 is supported

Integer constants:

AF_INET, AF_UNIX -- socket domains (first argument to socket() call)
SOCK_STREAM, SOCK_DGRAM, SOCK_RAW -- socket types (second argument)

Many other constants may be defined; these may be used in calls to
the setsockopt() and getsockopt() methods.
"""

_have_ssl = False

EBADF = 9



#def ssl(sock, keyfile=None, certfile=None):
#    if hasattr(sock, "_sock"):
#        sock = sock._sock
#    return _realssl(sock, keyfile, certfile)

# WSA error codes


def getfqdn(name=''):
    return string()

def gethostbyname(hostname):
    return string()

def gethostbyname_ex(  	hostname):
    return string()

def gethostname():
    return string()

def gethostbyaddr(  	ip_address): 
    return string()

def getnameinfo(  	sockaddr, flags):
    return (string(),int())
def getprotobyname( 	protocolname):
    return int()
def getservbyname( 	servicename, protocolname=""):
    return int()

def getservbyport( 	port, protocolname=""):
    return string()

def socket( family=0, type=0, proto=0):
    return Socket()

def ssl(sock, keyfile="", certfile=""):
    return SSLObject(sock)

def socketpair( family=0,type=0, proto=0):
    return Socket()

def fromfd(	fd, family, type, proto=0):
    return int()

def ntohl( 	x):
    return x

def ntohs( 	x):
    return x

def htonl( 	x):
    return x

def htons( 	x):
    return x

def inet_aton( 	ip_string):
    int()

def inet_ntoa( packed_ip):
    return string()

def inet_pton( 	address_family, ip_string):
    return string()

def inet_ntop( 	address_family, packed_ip):
    return string()
def getdefaulttimeout( 	):
    return float()

def setdefaulttimeout( 	timeout):
    pass

class Socket:
    def __init__(self, family=AF_INET, type=SOCK_STREAM, proto=0, _sock=None):
        pass

    def close(self):
        pass

    def accept(self):
        return 

    def dup(self):
        """dup() -> socket object

        Return a new socket object connected to the same system resource."""
        return _socketobject(_sock=self._sock)

    def makefile(self, mode='r', bufsize=-1):
        """makefile([mode[, bufsize]]) -> file object

        Return a regular file object corresponding to the socket.  The mode
        and bufsize arguments are as for the built-in open() function."""
        return _fileobject(self._sock, mode, bufsize)

    def accept(self):
        return Socket(),string()

    def bind(s):
        pass

    def connect(self,a):
        pass
    def connect_ex(self,a):
        return int()

    def fileno():
        return int()

    def getpeername():
        return string()

    def getsockname():
        return string()
    def getsockopt(l,o,b=0):
        return int()
    def listen(b):
        pass
    def recv(b,f=0):
        return string()
    def recvfrom(b,f=0):
        return (string(),string())
    def send( s, flags=0):
        return int()
    def sendall( 	string, flags=0):
        pass
    def sendto( s, flags,addr):
        return int()
    def setblocking( 	flag):
        pass
    def settimeout( 	value):
        pass
    def gettimeout( 	):
        return float()

    def setsockopt( 	level, optname, value):
        pass
    def shutdown( 	how):
        pass   

SocketType = Socket

class _closedsocket(object):
    __slots__ = []
    def _dummy(*args):
        raise error(EBADF, 'Bad file descriptor')
    send = recv = sendto = recvfrom = __getattr__ = _dummy


class _fileobject(object):
    """Faux file object attached to a socket object."""

    name = "<socket>"

    def __init__(self, sock, mode='rb', bufsize=-1):
        self._sock=sock

    def _getclosed(self):
        boolean()

    def close(self):
        self._sock = None

    def __del__(self):
        pass

    def flush(self):
        pass           

    def fileno(self):
        return self._sock.fileno()

    def write(self, data):
        pass

    def writelines(self, list):
        pass

    def _get_wbuf_len(self):
       return int()

    def read(self, size=-1):
       return string()

    def readline(self, size=-1):
        return string()

    def readlines(self, sizehint=0):
        return []

    # Iterator protocols

    def __iter__(self):
        return self

    def next(self):
        return string()
