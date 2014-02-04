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

static PyObject* globals = NULL;
static PyObject* locals = NULL;

extern char main_py[];		// text of scripts/main.py
extern char pre_py[];		// text of scripts/pre.py
extern char post_py[];		// text of scripts/post.py

void pre_translation_unit()
{
  Py_Initialize();

  globals = PyDict_New();

  PyDict_SetItemString(globals, "__builtins__", PyEval_GetBuiltins());

  lm_gcc_init(globals);

  PyRun_String(pre_py, Py_file_input, globals, globals);
}

void run()
{
  basic_block         my_basic_block;
  block_stmt_iterator my_statement_iterator;

  PyRun_String(main_py, Py_file_input, globals, globals);

  FOR_EACH_BB(my_basic_block)
    {
      for (my_statement_iterator = bsi_start(my_basic_block);
           !bsi_end_p(my_statement_iterator);
           bsi_next(&my_statement_iterator))
        {
          tree my_statement = bsi_stmt(my_statement_iterator);
        }
    }
}

void post_translation_unit()
{
  PyRun_String(post_py, Py_file_input, globals, globals);

  Py_Finalize();

  globals = NULL;
}
