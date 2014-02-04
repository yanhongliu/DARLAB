#!/bin/bash

set -x

wget http://www.gnu.org/licenses/gpl.txt
mv gpl.txt COPYING
touch INSTALL NEWS README ChangeLog AUTHORS
touch aclocal.m4

if [ -e /usr/local/share/aclocal/libtool.m4 ]
then
	cat /usr/local/share/aclocal/libtool.m4 >> aclocal.m4
fi

if [ -e /usr/share/aclocal/libtool.m4 ]
then
	cat /usr/share/aclocal/libtool.m4 >> aclocal.m4
fi

libtoolize
aclocal
#autoheader
automake --gnu --add-missing
autoconf

cp -r config config.new
rm -rf config
mv config.new config
