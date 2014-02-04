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

#include "common.h"
#include "TreeCode.h"
#include "ParameterCode.h"
#include "TreeObject.h"
#include "Statement.h"
#include "BasicBlock.h"
#include "Type.h"

//////////////////////////
// Internal definitions //
//////////////////////////

static PyObject* args = NULL;

static PyObject* getargs_interface(PyObject* self, PyObject* argv)
{
  if(args)
    {
      Py_INCREF(args);
      return args;
    }
  else
    {
      Py_RETURN_NONE;
    }
}

static PyObject* getblocks_interface(PyObject* self, PyObject* argv)
{
  PyObject* ret;

  ret = PyList_New(0);

  basic_block bb;

  FOR_ALL_BB(bb)
    {
      PyObject* block = _PyObject_New(&BasicBlockObjectType);

      PyObject* init_name	= PyString_FromString("__init__");
      PyObject* init_arg	= PyLong_FromVoidPtr(bb);

      PyObject_CallMethodObjArgs(block, init_name, init_arg, NULL);

      Py_DECREF(init_name);
      Py_DECREF(init_arg);

      PyList_Append(ret, block);

      Py_DECREF(block);
    }

  return ret;
} 

static tree tree_with_code(enum tree_code code, tree type, int numargs, PyObject* argv)
{
  tree args[7];

  if(numargs != PyTuple_Size(argv) - 2)
    {
      return NULL;
    }

  if(numargs > 7)
    {
      return NULL;
    }

  int i;

  for(i = 2; i < PyTuple_Size(argv); i++)
    {
      PyObject* current_tree_object = PyTuple_GetItem(argv, i);

      if(current_tree_object->ob_type != &TreeObjectType)
        {
          return NULL;
        }
 
      args[i - 2] = ((TreeObject*)current_tree_object)->_tree;
    }

  switch(numargs)
    {
    case 0:
      return build0(code, type);
    case 1:
      return build1(code, type, args[0]);
    case 2:
      return build2(code, type, args[0], args[1]);
    case 3:
      return build3(code, type, args[0], args[1], args[2]);
    case 4:
      return build4(code, type, args[0], args[1], args[2], args[3]);
    case 7:
      return build7(code, type, args[0], args[1], args[2], args[3], args[4], args[5], args[6]);
    default:
      return NULL;
    }
}

static PyObject* buildtree_interface(PyObject* self, PyObject* argv)
{
  if(!PyTuple_Check(argv))
    {
      Py_RETURN_NONE;
    }

  tree new_tree;
  int tree_size = PyTuple_Size(argv) - 2;

  PyObject* tree_code = PyTuple_GetItem(argv, 0);
  PyObject* tree_type = PyTuple_GetItem(argv, 1);

  if(!TreeCode_Check(tree_code) ||
     !Tree_Check(tree_type))
    {
      Py_RETURN_NONE;
    }

  #define DEFTREECODE(code, string, supertype, numargs)				\
    case code:									\
      new_tree = tree_with_code(code, Tree_AsTree(tree_type), numargs, argv);	\
      break;

  switch(TreeCode_AsCode(tree_code))
    {
      #include <tree.def>
    }

  #undef DEFTREECODE

  if(!new_tree)
    {
      Py_RETURN_NONE;
    }

  return Tree_FromTree(new_tree);
}

//////////////////////////
// External definitions //
//////////////////////////

struct PyMethodDef lm_gcc_interfaces[] = {
  { "getargs",		getargs_interface,	METH_VARARGS,	"Get the arguments passed to lm_gcc."	},
  { "getblocks",	getblocks_interface,	METH_VARARGS,	"Get a list of all basic blocks."	},
  { "buildtree",	buildtree_interface,	METH_VARARGS,	"Build a tree."				},
  { NULL,		NULL,			0,		NULL					}
};

static void lm_gcc_setup_args()
{
  int i;

  int argc;
  struct plugin_argument* argv;

  get_plugin_arguments(&argc, &argv);

  args = PyList_New(argc);

  assert(args);

  for(i = 0; i < argc; i++) 
    {
      PyObject* key;
      PyObject* value;
      PyObject* tuple;
      
      key	= argv[i].key	? PyString_FromString(argv[i].key)	: Py_None;
      value	= argv[i].value	? PyString_FromString(argv[i].value)	: Py_None;

      tuple	= PyTuple_Pack(2, key, value);

      PyList_SetItem(args, i, tuple);
    } 
}

static void lm_gcc_setup_classes(PyObject* module)
{
#define SETUP_CLASS(class)				\
  do 							\
    {							\
      PyObject* class##Type = setup##class##Type();	\
      Py_INCREF(class##Type);				\
      PyModule_AddObject(module, #class, class##Type);	\
    }							\
  while(0)

  SETUP_CLASS(BasicBlock);
  SETUP_CLASS(Statement);
  SETUP_CLASS(Tree);
  SETUP_CLASS(TreeCode);
  SETUP_CLASS(ParameterCode);
#undef SETUP_CLASS

  PyObject* treeCodeModule = setupTreeCodes();
  PyObject* parameterCodeModule = setupParameterCodes();
  PyObject* primitiveTypesModule = setupPrimitiveTypes();

  PyModule_AddObject(module, "treeCodes", treeCodeModule);
  PyModule_AddObject(module, "parameterCodes", parameterCodeModule);
  PyModule_AddObject(module, "primitiveTypes", primitiveTypesModule);

  lm_gcc_setup_args();
}

void lm_gcc_init(PyObject* globals)
{
  PyObject* module = Py_InitModule("gcc", lm_gcc_interfaces);
  assert(module);

  lm_gcc_setup_classes(module);

  PyDict_SetItemString(globals, "gcc", module);
}
