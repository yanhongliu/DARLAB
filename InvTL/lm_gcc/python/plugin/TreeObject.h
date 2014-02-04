#ifndef __TREEOBJECT_H__
#define __TREEOBJECT_H__

#include "common.h"
#include "TreeCode.h"
#include "ParameterCode.h"

// TreeObject ///////////////////////////////////////////////////////////////////////////////

// TreeObject - interface

typedef struct {
  PyObject_HEAD
  tree _tree;
} TreeObject;

static int		TreeInit		(PyObject*, PyObject*, PyObject*);
static PyObject*	Tree_FromTree		(tree);
static tree 		Tree_AsTree		(PyObject*);
static int 		Tree_Check		(PyObject*);
static PyObject*	TreeRepr		(PyObject*);
static PyObject*	TreeGetCode		(PyObject*, PyObject*);
static PyObject*	TreeGetAttributes	(PyObject*, PyObject*);
static PyObject*	TreeGetOperands		(PyObject*, PyObject*);
static PyObject*	TreeSetAttribute	(PyObject*, PyObject*);
static PyObject*	TreeSetOperand		(PyObject*, PyObject*);

static PyMemberDef TreeMembers[] = {
	//	name	type	offset	flags	doc
	{	NULL,	0,	0,	0,	NULL	}
};

static PyMethodDef TreeMethods[] = {
	//	name			meth			flags		doc
	{	"getcode",		TreeGetCode,		METH_VARARGS,	"Get the tree code of a tree."	},
	{	"getoperands",		TreeGetOperands,	METH_VARARGS,	"Get the operands of a tree."	},
	{	"getattributes",	TreeGetAttributes,	METH_VARARGS,	"Get the attributes of a tree."	},
	{	"setoperand",		TreeSetOperand,		METH_VARARGS,	"Set an operand of a tree."	},
	{	"setattribute",		TreeSetAttribute,	METH_VARARGS,	"Set an attribute of a tree."	},
	{	NULL,			NULL,			0,		NULL				}
};

static PyTypeObject TreeObjectType = {
#ifdef Py_TRACE_REFS
  ._ob_next		= NULL,
  ._ob_prev		= NULL,
#endif

  .ob_refcnt		= 1,
  .ob_size		= 0,

  .tp_name		= "gcc.Tree",
  .tp_basicsize		= sizeof(TreeObject),
  .tp_itemsize		= 0,

  .tp_repr		= TreeRepr,
  .tp_str		= TreeRepr,
  .tp_flags		= Py_TPFLAGS_DEFAULT,

  .tp_methods		= TreeMethods,
  .tp_members		= TreeMembers,

  .tp_new		= PyType_GenericNew,
  .tp_init		= TreeInit,

  .tp_doc		= "Base type for Tree objects"
};

// TreeObject - implementation

static PyObject* Tree_FromTree(tree node)
{
  if(node == NULL || node == NULL_TREE)
    {
      Py_RETURN_NONE;
    }

  PyObject* ret = _PyObject_New(&TreeObjectType);

  PyObject* init_name	= PyString_FromString("__init__");
  PyObject* init_arg	= PyLong_FromVoidPtr(node);

  PyObject_CallMethodObjArgs(ret, init_name, init_arg, NULL);

  Py_DECREF(init_name);
  Py_DECREF(init_arg);

  return ret;
}

static tree Tree_AsTree(PyObject* object)
{
  return((TreeObject*)object)->_tree;
}

static int Tree_Check(PyObject* object)
{
  return(object->ob_type == &TreeObjectType);
}

static int TreeInit(PyObject* self, PyObject* arguments, PyObject* keywords)
{
  PyObject* argument;

  int ret = PyArg_UnpackTuple(arguments, "__init__", 1, 1, &argument);

  if(ret) 
    {
      if(PyLong_Check(argument) || PyInt_Check(argument))
        {
          ((TreeObject*)self)->_tree = PyLong_AsVoidPtr(argument);
        }
      else if(argument->ob_type == &TreeObjectType)
        {
          ((TreeObject*)self)->_tree = ((TreeObject*)argument)->_tree;
        }
      else
        {
          ret == 0;
        }
    }

  return (!ret);
}

static PyObject* TreeRepr(PyObject* self)
{
  PyObject* code = TreeGetCode(self, NULL);

  PyObject* ret = PyString_FromFormat("<Tree object (code %s) at [GCC %p]>",
                                      PyString_AsString(TreeCodeRepr(code)),
                                      ((TreeObject*)self)->_tree);
  assert(ret);

  Py_DECREF(code);

  return ret;
}

static PyObject* TreeGetCode(PyObject* self, PyObject* argv)
{
  tree local_tree = ((TreeObject*)self)->_tree;
  enum tree_code code = TREE_CODE(local_tree);

  PyObject* code_object = TreeCode_FromCode(code);

  return code_object;
}

static PyObject* TreeGetOperands(PyObject* self, PyObject* argv)
{
  PyObject* ret;

  int numoperands = 0;

  #define DEFTREECODE(code, string, supertype, numargs) \
  case code:						\
    numoperands = numargs;				\
    break;

  switch(TREE_CODE(((TreeObject*)self)->_tree)) 
    {
      #include <tree.def>
    }

  #undef DEFTREECODE

  ret = PyList_New(0);

  int index;
  tree current_operand;

  for(index = 0; index < numoperands; index++)
    {
      current_operand = TREE_OPERAND(((TreeObject*)self)->_tree, index);
   
      PyObject* tree_object = Tree_FromTree(current_operand);

      PyList_Append(ret, tree_object);

      Py_DECREF(tree_object);
    }

  return ret;
}

static int is_one_of(tree node, int code_vector[])
{
  int index = 0;
  int current_code;

  while((current_code = code_vector[index++]) != -1)
    {
      if(TREE_CODE(node) == current_code)
        return 1;
    }

  return 0;
}

static PyObject* GET_SIZE_T(tree node, size_t data)
{
  return PyLong_FromUnsignedLongLong((uint64_t)data);
}

static PyObject* GET_TREE(tree node, tree data)
{
  return Tree_FromTree(data);
}

static PyObject* GET_BOOL(tree node, int data)
{
  return PyBool_FromLong(data);
}

static PyObject* GET_MACHINE_MODE(tree node, enum machine_mode data)
{
  return PyLong_FromLong((long)data);
}

static PyObject* GET_INT_CST_LOW(tree node, uint32_t data)
{
  return PyLong_FromUnsignedLongLong((uint64_t)TREE_INT_CST_LOW(node));
}

static PyObject* GET_INT_CST_HIGH(tree node, uint32_t data)
{
  return PyLong_FromLongLong((int64_t)TREE_INT_CST_HIGH(node));
}

static PyObject* GET_REAL(tree node, REAL_VALUE_TYPE data)
{
  char real_version[128];
  memset(real_version, 0, sizeof(real_version));

  real_to_decimal(real_version, &data, 128, 0, 1);

  return PyFloat_FromDouble(strtod(real_version, NULL));
}

static PyObject* GET_STRING(tree node, const char* data)
{
  return PyString_FromString(data);
}

static PyObject* GET_OFF_T(tree node, off_t data)
{
  return PyLong_FromLongLong((int64_t)data);
}

static PyObject* GET_BUILT_IN_FUNCTION(tree node, enum built_in_function data)
{
  return PyLong_FromLong((long)data);
}

static PyObject* GET_PHI_ARG(tree node, struct phi_arg_d arg)
{
  return Tree_FromTree(arg.def);
}

static PyObject* TreeGetAttributes(PyObject* self, PyObject* argv)
{
  PyObject* ret;

  ret = PyDict_New();

  tree node = ((TreeObject*)self)->_tree;

  #define DEFTREEPARAMETER(name, perms, type, accessor, ...)		\
    do									\
      {									\
        int code_vector[] = { __VA_ARGS__, -1 };			\
        if(is_one_of(node, code_vector))				\
          {								\
            PyObject* param_code = parameterCodes.name;			\
            								\
            PyObject* param = GET_##type(node, accessor(node));		\
									\
            PyDict_SetItem(ret, param_code, param);			\
          								\
            Py_DECREF(param);						\
          }								\
      }									\
    while(0);

  #define DEFTREEPARAM_VECTOR(name, perms, type, accessor, count, ...)			\
    do											\
      {											\
        int code_vector[] = { __VA_ARGS__, -1 };					\
        if(is_one_of(node, code_vector))						\
          {										\
            PyObject* param_code = parameterCodes.name;					\
            PyObject* param_list = PyList_New(0);					\
											\
            int index;									\
            for(index = 0; index < count(node); index++)				\
              {										\
                PyObject* current_param = GET_##type(node, accessor(node, index));	\
                PyList_Append(param_list, current_param);				\
                Py_DECREF(current_param);						\
              }										\
											\
            PyDict_SetItem(ret, param_code, param_list);				\
											\
            Py_DECREF(param_list);							\
          }										\
      }											\
    while(0);

  #include "parameter.def"

  #undef DEFTREEPARAM_VECTOR
  #undef DEFTREEPARAMETER

  return ret;
}

#define SET_RDWR_SIZE_T(data, object)					\
  if(PyLong_Check(object))						\
    {									\
      data = (size_t)PyLong_AsUnsignedLongLong(object);			\
    }

#define SET_RDONLY_SIZE_T(data, object)					\
  Py_RETURN_NONE;

#define SET_RDWR_TREE(data, object)					\
  if(Tree_Check(object))						\
    {									\
      data = Tree_AsTree(object);					\
    }

#define SET_RDONLY_TREE(data, object)					\
  Py_RETURN_NONE;

#define SET_RDWR_BOOL(data, object)					\
  if(PyLong_Check(object))						\
    {									\
      data = (int)PyLong_AsBool(object);				\
    }

#define SET_RDWR_MACHINE_MODE(data, object)				\
  if(PyLong_Check(object))						\
    {									\
      data = (enum machine_mode)PyLong_AsLong(object);			\
    }

#define SET_RDWR_INT_CST_LOW(data, object)				\
  if(PyLong_Check(object))						\
    {									\
      data = (uint32_t)PyLong_AsUnsignedLongLong(object);		\
    }

#define SET_RDWR_INT_CST_HIGH(data, object)				\
  if(PyLong_Check(object))						\
    {									\
      data = (int32_t)PyLong_AsUnsignedLongLong(object);		\
    }

#define SET_RDWR_REAL(data, object)					\
  if(PyFloat_Check(object))						\
    {									\
      char real_version[128];						\
      memset(real_version, 0, sizeof(real_version));			\
      snprintf(real_version, 127, "%g", PyFloat_AsDouble(object));	\
      real_from_string(&(data), real_version);				\
    }

#define SET_RDONLY_STRING(data, object)					\
  Py_RETURN_NONE;

#define SET_RDWR_OFF_T(data, object)					\
  if(PyLong_Check(object))						\
    {									\
      data = (off_t)Long_AsLongLong(object);				\
    }

#define SET_RDONLY_OFF_T(data, object)					\
  Py_RETURN_NONE;

#define SET_RDWR_BUILT_IN_FUNCTION(data, object)			\
  if(PyLong_Check(object))						\
    {									\
      data = (enum built_in_function)Long_AsLong(object);		\
    }

#define SET_RDONLY_PHI_ARG(data, object)				\
  if(Tree_Check(object))						\
    {									\
      data.def = Tree_AsTree(object);					\
    }

static PyObject* TreeSetAttribute(PyObject* self, PyObject* argv)
{
  PyObject* name_object;
  PyObject* value_object;

  tree node = ((TreeObject*)self)->_tree;

  if(!PyArg_UnpackTuple(argv, "setattribute", 2, 2, &name_object, &value_object))
    {
      Py_RETURN_NONE;
    }

  if(!ParameterCode_Check(name_object))
    {
      Py_RETURN_NONE;
    }


#define DEFTREEPARAMETER(name, perms, type, accessor, ...)		\
case name:								\
  {									\
    int code_vector[] = { __VA_ARGS__, -1 };				\
									\
    if(is_one_of(node, code_vector))					\
      {									\
        SET_##perms##_##type(accessor(node), value_object)		\
      }									\
  }									\
  									\
  break;

#define DEFTREEPARAM_VECTOR(name, perms, type, accessor, count, ...)	\
case name:								\
   Py_RETURN_NONE;
        
  int* code_vector;

  switch(ParameterCode_AsCode(name_object))
    {
      #include "parameter.def"
    }

#undef DEFTREEPARAM_VECTOR
#undef DEFTREEPARAMETER

  Py_RETURN_NONE;
}

static PyObject* TreeSetOperand(PyObject* self, PyObject* argv)
{
  PyObject* index_object;
  PyObject* value_object;

  tree node = ((TreeObject*)self)->_tree;

  if(!PyArg_UnpackTuple(argv, "setoperand", 2, 2, &index_object, &value_object))
    {
      Py_RETURN_NONE;
    }

  if(!PyLong_Check(index_object) ||
     !Tree_Check(value_object))
    {
      Py_RETURN_NONE;
    }

  int index = PyLong_AsInt(index_object);
  tree value = Tree_AsTree(value_object);

  #define DEFTREECODE(code, string, supertype, numargs)		\
    case code:							\
      if(index >= numargs)					\
        {							\
          Py_RETURN_NONE;					\
        }

  switch(TREE_CODE(node))
    {
      #include <tree.def>
    }

  #undef DEFTREECODE

  TREE_OPERAND(node, index) = value;
}

// TreeObject - setup

static PyObject* setupTreeType()
{
  TreeObjectType.ob_type = &PyType_Type;

  assert(!PyType_Ready(&TreeObjectType));

  return (PyObject*)&TreeObjectType;
}

#endif  //TREEOBJECT_H//
