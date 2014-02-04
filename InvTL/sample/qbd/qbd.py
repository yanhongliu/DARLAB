import weakref
import sys
import os
from pdb import Pdb
import __builtin__
import qbdlib
import traceback
def debug():
    if not sys.argv[1:]:
        print "usage: qbd.py args --run scriptfile [arg] ..."
        sys.exit(2)

    mainpyfile =  sys.argv[1]     # Get script filename
    if not os.path.exists(mainpyfile):
        print 'Error:', mainpyfile, 'does not exist'
        print 'Not launching debugger!!!!'
        sys.exit(1)

    del sys.argv[0]         # Hide "pdb.py" from argument list

    # Replace pdb's dir with script's dir in front of module search path.
    sys.path[0] = os.path.dirname(mainpyfile)

    pdb = Pdb()
    try:
        print "Ready to launch program. Type 'cont' to run the program."
        pdb._runscript(mainpyfile)
        print "The program finished. No exceptions were caught."
    except SystemExit:
        print "The program exited via sys.exit(). Exit status: ",
        print sys.exc_info()[1]
    except AssertionError:
        traceback.print_exc()
        print "Assertion Caught. Most likely reason: Query-Based Assertion"           
        print "Running 'cont' or 'step' will quit the debugger."
        t = sys.exc_info()[2]
        while t.tb_next is not None:
            t = t.tb_next
        pdb.interaction(t.tb_frame,t)
        print "Post mortem debugger finished."
    except:
        traceback.print_exc()
        print "Uncaught exception. Entering post mortem debugging"
        print "Running 'cont' or 'step' will quit the debugger."
        t = sys.exc_info()[2]
        while t.tb_next is not None:
            t = t.tb_next
        pdb.interaction(t.tb_frame,t)
        print "Post mortem debugger finished. The "+mainpyfile+" will be restarted"

def run_program():
    while len(sys.argv)>0:
        if sys.argv[0]=="--run":
            print "AAA"
            debug()
            break
        sys.argv=sys.argv[1:]
   
run_program()

