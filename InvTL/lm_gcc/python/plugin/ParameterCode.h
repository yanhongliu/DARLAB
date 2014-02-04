#ifndef __PARAMETERCODE_H__
#define __PARAMETERCODE_H__

#include "common.h"

// ParameterCodeObject //////////////////////////////////////////////////////////////////////

// ParameterCodeObject - interface

#define DEFTREEPARAMETER(name, perms, type, accessor, ...)		\
  name,

#define DEFTREEPARAM_VECTOR(name, perms, type, accessor, count, ...)	\
  name,

enum tree_parameter_code {
  #include "parameter.def"
};

#undef DEFTREEPARAM_VECTOR
#undef DEFTREEPARAMETER

typedef struct {
  PyObject_HEAD
  enum tree_parameter_code _code;
} ParameterCodeObject;

static int		ParameterCodeInit		(PyObject*, PyObject*, PyObject*);
static int		ParameterCode_Check		(PyObject*);
static PyObject*	ParameterCode_FromCode		(enum tree_parameter_code);
static enum tree_code	ParameterCode_AsCode		(PyObject*);
static int		ParameterCodeCompare		(PyObject*, PyObject*);
static PyObject*	ParameterCodeRepr		(PyObject*);
static long		ParameterCodeHash		(PyObject*);

static PyMemberDef ParameterCodeMembers[] = {
	//	name	type	offset	flags	doc
	{	NULL,	0,	0,	0,	NULL	}
};

static PyMethodDef ParameterCodeMethods[] = {
	//	name			meth			flags		doc
	{	NULL,			NULL,			0,		NULL	}
};

static PyTypeObject ParameterCodeObjectType = {
#ifdef Py_TRACE_REFS
  ._ob_next		= NULL,
  ._ob_prev		= NULL,
#endif

  .ob_refcnt		= 1,
  .ob_size		= 0,

  .tp_name		= "gcc.ParameterCode",
  .tp_basicsize		= sizeof(ParameterCodeObject),
  .tp_itemsize		= 0,

  .tp_compare		= ParameterCodeCompare,
  .tp_repr		= ParameterCodeRepr,
  .tp_hash		= ParameterCodeHash,
  .tp_str		= ParameterCodeRepr,
  .tp_flags		= Py_TPFLAGS_DEFAULT,

  .tp_methods		= ParameterCodeMethods,
  .tp_members		= ParameterCodeMembers,

  .tp_new		= PyType_GenericNew,
  .tp_init		= ParameterCodeInit,

  .tp_doc		= "Base type for ParameterCode objects"
};

// ParameterCodeObject - implementation

static int ParameterCodeInit(PyObject* self, PyObject* arguments, PyObject* keywords)
{
  PyObject* argument;

  int ret = PyArg_UnpackTuple(arguments, "__init__", 1, 1, &argument);

  if(ret) 
    {
      if(PyLong_Check(argument) || PyInt_Check(argument))
        {
          ((ParameterCodeObject*)self)->_code = PyLong_AsLong(argument);
        }
      else
        {
          ret == 0;
        }
    }

  return (!ret);
}

static int ParameterCode_Check(PyObject* object)
{
  return((object->ob_type == &ParameterCodeObjectType));
}

static PyObject* ParameterCode_FromCode(enum tree_parameter_code code)
{
  PyObject* ret = _PyObject_New(&ParameterCodeObjectType);

  PyObject* init_name	= PyString_FromString("__init__");
  PyObject* init_arg	= PyLong_FromLong(code);

  PyObject_CallMethodObjArgs(ret, init_name, init_arg, NULL);

  Py_DECREF(init_name);
  Py_DECREF(init_arg);

  return ret;
}

static enum tree_code ParameterCode_AsCode(PyObject* object)
{
  return((ParameterCodeObject*)object)->_code;
}

static int ParameterCodeCompare(PyObject* self, PyObject* other)
{
  if(!ParameterCode_Check(self) ||
     !ParameterCode_Check(other))
    {
      return -1;
    }

  enum tree_parameter_code self_code = ((ParameterCodeObject*)self)->_code;
  enum tree_parameter_code other_code = ((ParameterCodeObject*)other)->_code;

  if(self_code == other_code)
    {
      return 0;
    }
  else if(self_code > other_code)
    {
      return 1;
    }
  else
    {
      return -1;
    }
}

static PyObject* ParameterCodeRepr(PyObject* object)
{
  char* code_string;

#define DEFTREEPARAMETER(name, perms, type, accessor, ...)		\
  case name:								\
    code_string = #name;						\
    break;

#define DEFTREEPARAM_VECTOR(name, perms, type, accessor, count, ...)	\
  case name:								\
    code_string = #name;						\
    break;

  switch(ParameterCode_AsCode(object)) 
    {
      #include "parameter.def"
    }

#undef DEFTREEPARAM_VECTOR
#undef DEFTREEPARAMETER

  return PyString_FromFormat("<%s>", code_string);
}

static long ParameterCodeHash(PyObject* self)
{
  if(!ParameterCode_Check(self))
    {
      return -1;
    }

  enum tree_parameter_code self_code = ((ParameterCodeObject*)self)->_code;

  return self_code;
}

// ParameterCodeObject - setup

static PyObject* setupParameterCodeType()
{
  ParameterCodeObjectType.ob_type = &PyType_Type;

  assert(!PyType_Ready(&ParameterCodeObjectType));

  return (PyObject*)&ParameterCodeObjectType;
}

#define DEFTREEPARAMETER(name, perms, type, accessor, ...)		\
  PyObject* name;

#define DEFTREEPARAM_VECTOR(name, perms, type, accessor, count, ...)	\
  PyObject* name;

static struct
{
  #include "parameter.def"
} parameterCodes;

#undef DEFTREEPARAM_VECTOR
#undef DEFTREEPARAMETER

#define DEFTREEPARAMETER(name, perms, type, accessor, ...)		\
  parameterCodes.name = ParameterCode_FromCode(name);			\
  PyModule_AddObject(parameterCode_module, #name, parameterCodes.name);

#define DEFTREEPARAM_VECTOR(name, perms, type, accessor, count, ...)	\
  parameterCodes.name = ParameterCode_FromCode(name);			\
  PyModule_AddObject(parameterCode_module, #name, parameterCodes.name);


static PyObject* setupParameterCodes()
{
  PyObject* parameterCode_module = PyModule_New("parametercodes");
  #include "parameter.def"
  return parameterCode_module;
}

#undef DEFTREEPARAM_VECTOR
#undef DEFTREEPARAMETER

#endif  //PARAMETERCODE_H//
