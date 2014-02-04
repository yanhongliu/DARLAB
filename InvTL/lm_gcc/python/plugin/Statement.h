#ifndef __STATEMENT_H__
#define __STATEMENT_H__

#include "common.h"
#include "TreeObject.h"

// StatementObject //////////////////////////////////////////////////////////////////////////

// StatementObject - interface

typedef struct {
  PyObject_HEAD
  tree			_stmt;
} StatementObject;

static int		StatementInit		(PyObject*, PyObject*, PyObject*);
static PyObject*	Statement_FromStatement	(tree);
static PyObject*	StatementRepr		(PyObject*);
static PyObject*	StatementGetTree	(PyObject*, PyObject*);

static PyMemberDef StatementMembers[] = {
	//	name	type	offset	flags	doc
	{	NULL,	0,	0,	0,	NULL	}
};

static PyMethodDef StatementMethods[] = {
	//	name		meth			flags		doc
	{	"gettree",	StatementGetTree,	METH_VARARGS,	"Get the top-level tree for the statement."	},
	{	NULL,		NULL,			0,		NULL						}
};

static PyTypeObject StatementObjectType = {
#ifdef Py_TRACE_REFS
  ._ob_next		= NULL,
  ._ob_prev		= NULL,
#endif

  .ob_refcnt		= 1,
  .ob_size		= 0,

  .tp_name		= "gcc.Statement",
  .tp_basicsize		= sizeof(StatementObject),
  .tp_itemsize		= 0,

  .tp_repr		= StatementRepr,
  .tp_str		= StatementRepr,
  .tp_flags		= Py_TPFLAGS_DEFAULT,

  .tp_methods		= StatementMethods,
  .tp_members		= StatementMembers,

  .tp_new		= PyType_GenericNew,
  .tp_init		= StatementInit,

  .tp_doc		= "A view of a statement"
};

// StatementObject - implementation

static PyObject* Statement_FromStatement(tree node)
{
  assert(node != NULL);

  PyObject* ret = _PyObject_New(&StatementObjectType);

  PyObject* init_name	= PyString_FromString("__init__");
  PyObject* init_arg	= PyLong_FromVoidPtr(node);

  PyObject_CallMethodObjArgs(ret, init_name, init_arg, NULL);

  Py_DECREF(init_name);
  Py_DECREF(init_arg);

  return ret;
}

static int StatementInit(PyObject* self, PyObject* arguments, PyObject* keywords)
{
  PyObject* argument;

  int ret = PyArg_UnpackTuple(arguments, "__init__", 1, 1, &argument);

  if(ret) 
    {
      if(PyLong_Check(argument) || PyInt_Check(argument))
        {
          ((StatementObject*)self)->_stmt = PyLong_AsVoidPtr(argument);
        }
      else if(argument->ob_type == &StatementObjectType)
        {
          ((StatementObject*)self)->_stmt = ((StatementObject*)argument)->_stmt;
        }
      else if(argument->ob_type == &TreeObjectType)
        {
          ((StatementObject*)self)->_stmt = ((TreeObject*)argument)->_tree;
        }
      else
        {
          ret == 0;
        }
    }

  return (!ret);
}

static PyObject* StatementRepr(PyObject* self)
{
  PyObject* ret = PyString_FromFormat("<Statement object at [GCC %p]>", ((StatementObject*)self)->_stmt);
  assert(ret);

  return ret;
}

static PyObject* StatementGetTree(PyObject* self, PyObject* argv)
{
  PyObject* ret = Tree_FromTree(((StatementObject*)self)->_stmt);

  return ret;
}

// StatementObject - setup

static PyObject* setupStatementType()
{
  StatementObjectType.ob_type = &PyType_Type;

  assert(!PyType_Ready(&StatementObjectType));

  return (PyObject*)&StatementObjectType;
}

#endif  //STATEMENT_H//
