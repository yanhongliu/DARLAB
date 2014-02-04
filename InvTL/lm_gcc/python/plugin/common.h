/* Python plugin executor
   Copyright 2005, 2006 Sean Callanan

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2, or (at your option)
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; see the file COPYING.  If not, write to
the Free Software Foundation, 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.  */

#ifndef __COMMON_H__
#define __COMMON_H__

#include "config.h"
#include "system.h"
#include "coretypes.h"
#include "tm.h"
#include "toplev.h"
#include "tree.h"
#include "rtl.h"
#include "expr.h"
#include "flags.h"
#include "params.h"
#include "input.h"
#include "insn-config.h"
#include "integrate.h"
#include "varray.h"
#include "hashtab.h"
#include "pointer-set.h"
#include "splay-tree.h"
#include "langhooks.h"
#include "cgraph.h"
#include "intl.h"
#include "function.h"
#include "diagnostic.h"
#include "debug.h"

#include "timevar.h"

#include "tree-gimple.h"
#include "tree-inline.h"
#include "tree-mudflap.h"
#include "tree-flow.h"
#include "tree-pass.h"
#include "tree-plugin.h"

#include "c-common.h"
#include "c-tree.h"

#include "lm-gcc.h"

#define PYMALLOC_DEBUG
#include <Python.h>
#include <structmember.h>

#include <inttypes.h>
#include <math.h>

//#define LMGCC_DEBUG

#ifdef LMGCC_DEBUG
  #define dprintf(...) fprintf(stderr, __VA_ARGS__)
#else
  #define dprintf(...) do {} while(0)
#endif

#endif  //COMMON_H//
