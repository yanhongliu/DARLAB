lib_LTLIBRARIES = libpython.la
libpython_la_SOURCES = plugin.c lm-gcc.c main.s pre.s post.s common.h lm-gcc.h BasicBlock.h ParameterCode.h Statement.h TreeCode.h TreeObject.h Type.h
libpython_la_LIBADD = @PYTHON_LDFLAGS@ @PYTHON_EXTRA_LDFLAGS@ @PYTHON_EXTRA_LIBS@ -lm
libpython_la_LDFLAGS = -version-info 1:0:0
libpython_la_CPPFLAGS = -DHAVE_CONFIG_H -DIN_GCC -I$(gcc_build)/gcc -I$(gcc_source)/gcc -I$(gcc_source)/include -I$(gcc_build)/intl -I$(gcc_source)/libcpp/include @PYTHON_CPPFLAGS@

main.s:	../scripts/py2s ../scripts/main.py
	../scripts/py2s -o main.s ../scripts/main.py

pre.s:	../scripts/py2s ../scripts/pre.py
	../scripts/py2s -o pre.s ../scripts/pre.py

post.s:	../scripts/py2s ../scripts/post.py
	../scripts/py2s -o post.s ../scripts/post.py
