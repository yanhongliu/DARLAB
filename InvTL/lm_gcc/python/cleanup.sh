#!/bin/sh

# stuff to preserve:
#.
#./plugin
#./plugin/plugin.c
#./plugin/find-element.h
#./plugin/Makefile.am
#./bootstrap.sh
#./cleanup.sh
#./config
#./Makefile.am
#./configure.in

set -x

rm -f config.h.in
rm -f config.h

rm -f aclocal.m4
rm -rf autom4te.cache
rm -f stamp-h1

ls config/* | grep -v CVS | xargs rm -rf

rm -f libtool

rm -f configure
rm -f config.log config.status

rm -f scripts/py2s

find . -name Makefile | xargs rm -f
find . -name Makefile.in | xargs rm -f
find . -name "*.s" | xargs rm -f
find . -name "*.o" | xargs rm -f
find . -name "*.lo" | xargs rm -f
find . -name "*.loT" | xargs rm -f
find . -name "*.a" | xargs rm -f
find . -name "*.la" | xargs rm -f

find . -name .deps | xargs rm -rf 
find . -name .libs | xargs rm -rf

rm -f COPYING INSTALL NEWS README ChangeLog AUTHORS
