.text
.globl _pre_py
_pre_py:
.asciz "import gcc\nimport sys\n\nprint \"Pre\"\n\ngccargs = gcc.getargs()\n\ndef extract_arg(key):\n\tglobal gccargs\n\tfor arg in gccargs:\n\t\tif arg[0] == key:\n\t\t\treturn arg[1]\n\tprint \"Warning: \"+key+\" was not specified.\"\n\treturn None;\n\ninvtsbase\t= extract_arg(\"INVTS_BASE\");\n\nlm\t\t= \"lm_gcc:_\"\nruledb\t\t= extract_arg(\"RULEDB\")\nrulefile\t= extract_arg(\"RULEFILE\")\noutfile\t\t= \"NONE\"\ninfile\t\t= \"NONE\"\ndriverfile\t= \"\"\n\nargv = [ \"--verbose\", \"--force\", lm, ruledb, rulefile, outfile, infile, driverfile, gcc ]\n\nsys.path += [invtsbase]\n\ngcc.invts_base = invtsbase\nprint \"InvTS Base: %s\"%invtsbase\nimport InvTS\n\nres = InvTS.init_main(argv)\n"
