#ifndef __TREECODE_H__
#define __TREECODE_H__

#include "common.h"

// TreeCodeObject ///////////////////////////////////////////////////////////////////////////

// TreeCodeObject - interface

typedef struct {
  PyObject_HEAD
  enum tree_code _code;
} TreeCodeObject;

static int		TreeCodeInit		(PyObject*, PyObject*, PyObject*);
static PyObject*	TreeCode_FromCode	(enum tree_code);
static enum tree_code	TreeCode_AsCode		(PyObject*);
static int		TreeCode_Check		(PyObject*);
static PyObject*	TreeCodeRepr		(PyObject*);

static PyMemberDef TreeCodeMembers[] = {
	//	name	type	offset	flags	doc
	{	NULL,	0,	0,	0,	NULL	}
};

static PyMethodDef TreeCodeMethods[] = {
	//	name			meth			flags		doc
	{	NULL,			NULL,			0,		NULL	}
};

static PyTypeObject TreeCodeObjectType = {
#ifdef Py_TRACE_REFS
  ._ob_next		= NULL,
  ._ob_prev		= NULL,
#endif

  .ob_refcnt		= 1,
  .ob_size		= 0,

  .tp_name		= "gcc.TreeCode",
  .tp_basicsize		= sizeof(TreeCodeObject),
  .tp_itemsize		= 0,

  .tp_repr		= TreeCodeRepr,
  .tp_str		= TreeCodeRepr,
  .tp_flags		= Py_TPFLAGS_DEFAULT,

  .tp_methods		= TreeCodeMethods,
  .tp_members		= TreeCodeMembers,

  .tp_new		= PyType_GenericNew,
  .tp_init		= TreeCodeInit,

  .tp_doc		= "Base type for TreeCode objects"
};

// TreeCodeObject - implementation

static int TreeCodeInit(PyObject* self, PyObject* arguments, PyObject* keywords)
{
  PyObject* argument;

  int ret = PyArg_UnpackTuple(arguments, "__init__", 1, 1, &argument);

  if(ret) 
    {
      if(PyLong_Check(argument) || PyInt_Check(argument))
        {
          ((TreeCodeObject*)self)->_code = PyLong_AsLong(argument);
        }
      else
        {
          ret == 0;
        }
    }

  return (!ret);
}

static PyObject* TreeCode_FromCode(enum tree_code code)
{
  PyObject* ret = _PyObject_New(&TreeCodeObjectType);

  PyObject* init_name	= PyString_FromString("__init__");
  PyObject* init_arg	= PyLong_FromLong(code);

  PyObject_CallMethodObjArgs(ret, init_name, init_arg, NULL);

  Py_DECREF(init_name);
  Py_DECREF(init_arg);

  return ret;
}

static enum tree_code TreeCode_AsCode(PyObject* object)
{
  return((TreeCodeObject*)object)->_code;
}

static int TreeCode_Check(PyObject* object)
{
  return((object->ob_type == &TreeCodeObjectType));
}

static PyObject* TreeCodeRepr(PyObject* object)
{
  char* code_string;

  #define DEFTREECODE(code, string, supertype, numargs) \
  case code:						\
    code_string = string;				\
    break;

  switch(TreeCode_AsCode(object)) 
    {
      #include <tree.def>
    }

  #undef DEFTREECODE

  return PyString_FromFormat("<%s>", code_string);
}

// TreeCodeObject - setup

static PyObject* setupTreeCodeType()
{
  TreeCodeObjectType.ob_type = &PyType_Type;

  assert(!PyType_Ready(&TreeCodeObjectType));

  return (PyObject*)&TreeCodeObjectType;
}

#define DEFTREECODE(code, string, supertype, numargs)	\
  PyObject* code;

static struct
{
  #include <tree.def>
} treeCodes;

#undef DEFTREECODE

#define DEFTREECODE(code, string, supertype, numargs)		\
  treeCodes.code = TreeCode_FromCode(code);			\
  PyModule_AddObject(treeCode_module, string, treeCodes.code);

static PyObject* setupTreeCodes()
{
  PyObject* treeCode_module = PyModule_New("treecodes");
  #include <tree.def> 
  return treeCode_module;
}

#undef DEFTREECODE

#endif  //TREECODE_H//
