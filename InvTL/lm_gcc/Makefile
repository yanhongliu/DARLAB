MAKEFLAGS	= -j 4

PLATFORM	:= $(shell uname -s)

SO_EXTENSION	= so

ifeq ($(PLATFORM),Darwin)
SO_EXTENSION	= dylib
endif

GCC_CONFIGURE_TARGET	= build-4.1.2/Makefile
GCC_BUILD_TARGET	= build-4.1.2/gcc/cc1
GCC_TARGET	= install-4.1.2/bin/gcc
OLD_GCC_TARGET	= install-4.1.0/bin/gcc
PYTHON_TARGET	= python/plugin/.libs/libpython.$(SO_EXTENSION)
ELSA_TARGET     = elsa/elsa-2005.08.22b/ccparse
all:	$(GCC_TARGET) $(ELSA_TARGET) $(PYTHON_TARGET)

gcc:	$(GCC_TARGET) 

elsa:	$(ELSA_TARGET)

plugin:	$(PYTHON_TARGET)

$(GCC_CONFIGURE_TARGET):
	cd build-4.1.2; rm -rf *; `pwd`/../gcc-4.1.2/configure --prefix=`pwd`/../install-4.1.2

$(GCC_BUILD_TARGET): $(GCC_CONFIGURE_TARGET)
	cd build-4.1.2; make $(MAKEFLAGS)
    
$(GCC_TARGET): $(GCC_BUILD_TARGET)
	cd build-4.1.2; make install

$(OLD_GCC_TARGET):
	cd build-4.1.0; rm -rf *; `pwd`/../gcc-4.1.0/configure --prefix=`pwd`/../install-4.1.0; make $(MAKEFLAGS); make install

$(ELSA_TARGET):
	cd elsa/elsa-2005.08.22b; find . -name configure -exec chmod +x {} \; ; ./configure ; make $(MAKEFLAGS)

$(PYTHON_TARGET): $(GCC_TARGET)
	cd python; ./cleanup.sh; ./bootstrap.sh; CFLAGS="-g -O0" ./configure --with-gcc-source=../gcc-4.1.2 --with-gcc-build=../build-4.1.2; make $(MAKEFLAGS)

.PHONY:	test test_plugin

test:
	cd ..; python2.4 InvTS.py --clean --verbose lm_gcc lm_gcc/test/rule_db.invtl lm_gcc/test/rule.invtl lm_gcc/test/dummy.c "" lm_gcc/test/dummy_out.c 

test_plugin:
	./$(GCC_TARGET) -g -O0 -ftree-plugin=$(PYTHON_TARGET):INVTS_BASE="$(PWD)/..":RULEDB=test/rule_db.invtl:RULEFILE=test/rule.invtl -o test/dummy test/dummy.c

clean:
	cd build-4.1.0; rm -rf *
	cd install-4.1.0; rm -rf *
	cd build-4.1.2; rm -rf *
	cd install-4.1.2; rm -rf *
	cd elsa/elsa-2005.08.22b; make clean
	cd python; ./cleanup.sh
