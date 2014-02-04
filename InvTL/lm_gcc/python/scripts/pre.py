import gcc
import sys

print "Pre"

gccargs = gcc.getargs()

def extract_arg(key):
	global gccargs
	for arg in gccargs:
		if arg[0] == key:
			return arg[1]
	print "Warning: "+key+" was not specified."
	return None;

invtsbase	= extract_arg("INVTS_BASE");

lm		= "lm_gcc:_"
ruledb		= extract_arg("RULEDB")
rulefile	= extract_arg("RULEFILE")
outfile		= "NONE"
infile		= "NONE"
driverfile	= ""

argv = [ "--verbose", "--force", lm, ruledb, rulefile, outfile, infile, driverfile, gcc ]

sys.path += [invtsbase]

gcc.invts_base = invtsbase
print "InvTS Base: %s"%invtsbase
import InvTS

res = InvTS.init_main(argv)
