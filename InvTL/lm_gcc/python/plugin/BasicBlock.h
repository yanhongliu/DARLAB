#ifndef __BASICBLOCK_H__
#define __BASICBLOCK_H__

#include "common.h"
#include "Statement.h"

// BasicBlockObject /////////////////////////////////////////////////////////////////////////

// BasicBlockObject - interface

typedef struct {
  PyObject_HEAD
  basic_block		_block;
} BasicBlockObject;

static int		BasicBlockInit			(PyObject*, PyObject*, PyObject*);
static PyObject*	BasicBlock_FromBlock		(basic_block);
static PyObject*	BasicBlockRepr			(PyObject*);
static PyObject* 	BasicBlockGetStatements		(PyObject*, PyObject*);
static PyObject* 	BasicBlockGetPredecessors	(PyObject*, PyObject*);
static PyObject* 	BasicBlockGetSuccessors		(PyObject*, PyObject*);
static PyObject*	BasicBlockInsertBefore		(PyObject*, PyObject*);
static PyObject*	BasicBlockInsertAfter		(PyObject*, PyObject*);

static PyMemberDef BasicBlockMembers[] = {
	//	name	type	offset	flags	doc
	{	NULL,	0,	0,	0,	NULL	}
};

static PyMethodDef BasicBlockMethods[] = {
	//	name			meth				flags		doc
	{	"getstatements",	BasicBlockGetStatements,	METH_VARARGS,	"Get a list of all statements in the block."	},
	{	"getpredecessors",	BasicBlockGetPredecessors,	METH_VARARGS,	"Get all the predecessors of the block."	},
	{	"getsuccessors",	BasicBlockGetSuccessors,	METH_VARARGS,	"Get all the successors of the block."		},
	{	"insertbefore",		BasicBlockInsertBefore,		METH_VARARGS,	"Insert a statement before a given statement."	},
	{	"insertafter",		BasicBlockInsertAfter,		METH_VARARGS,	"Insert a statement after a given statement."	},
	{	NULL,			NULL,				0,		NULL						}
};

static PyTypeObject BasicBlockObjectType = {
#ifdef Py_TRACE_REFS
  ._ob_next		= NULL,
  ._ob_prev		= NULL,
#endif

  .ob_refcnt		= 1,
  .ob_size		= 0,

  .tp_name		= "gcc.BasicBlock",
  .tp_basicsize		= sizeof(BasicBlockObject),
  .tp_itemsize		= 0,

  .tp_repr		= BasicBlockRepr,
  .tp_str		= BasicBlockRepr,
  .tp_flags		= Py_TPFLAGS_DEFAULT,

  .tp_methods		= BasicBlockMethods,
  .tp_members		= BasicBlockMembers,

  .tp_new		= PyType_GenericNew,
  .tp_init		= BasicBlockInit,

  .tp_doc		= "A view of a basic block"
};

// BasicBlockObject - implementation

static int BasicBlockInit(PyObject* self, PyObject* arguments, PyObject* keywords)
{
  PyObject* argument;

  int ret = PyArg_UnpackTuple(arguments, "__init__", 1, 1, &argument);

  if(ret) 
    {
      if(PyLong_Check(argument) || PyInt_Check(argument))
        {
          ((BasicBlockObject*)self)->_block = PyLong_AsVoidPtr(argument);
        }
      else if(argument->ob_type == &BasicBlockObjectType)
        {
          ((BasicBlockObject*)self)->_block = ((BasicBlockObject*)argument)->_block;
        }
      else
        {
          ret == 0;
        }
    }

  return (!ret);
}

static PyObject* BasicBlock_FromBlock(basic_block block)
{
  assert(block != NULL);

  PyObject* ret = _PyObject_New(&BasicBlockObjectType);

  PyObject* init_name	= PyString_FromString("__init__");
  PyObject* init_arg	= PyLong_FromVoidPtr(block);

  PyObject_CallMethodObjArgs(ret, init_name, init_arg, NULL);

  Py_DECREF(init_name);
  Py_DECREF(init_arg);

  return ret;
}

static PyObject* BasicBlockRepr(PyObject* self)
{
  PyObject* ret = PyString_FromFormat("<BasicBlock object at [GCC %p]>", ((BasicBlockObject*)self)->_block);
  assert(ret);

  return ret;
}

static PyObject* BasicBlockGetStatements(PyObject* self, PyObject* argv)
{
  PyObject* ret;

  ret = PyList_New(0);

  block_stmt_iterator	iter;
  tree			stmt;

  for(iter = bsi_start(((BasicBlockObject*)self)->_block);
      !bsi_end_p(iter);
      bsi_next(&iter))
    {
      stmt = bsi_stmt(iter);
   
      PyObject* statement = Statement_FromStatement(stmt);
      PyList_Append(ret, statement);

      Py_DECREF(statement);
    }

  return ret;
}

static PyObject* BasicBlockGetPredecessors(PyObject* self, PyObject* argv)
{
  PyObject* ret;

  ret = PyList_New(0);

  block_stmt_iterator	iter;
  tree			stmt;

  edge		my_edge;
  edge_iterator	my_edge_iterator;

  FOR_EACH_EDGE(my_edge, my_edge_iterator, (((BasicBlockObject*)self)->_block->preds))
    {
      PyObject* block = BasicBlock_FromBlock(my_edge->src);
      PyList_Append(ret, block);

      Py_DECREF(block);
    }

  return ret;
}

static PyObject* BasicBlockGetSuccessors(PyObject* self, PyObject* argv)
{
  PyObject* ret;

  ret = PyList_New(0);

  block_stmt_iterator	iter;
  tree			stmt;

  edge		my_edge;
  edge_iterator	my_edge_iterator;

  FOR_EACH_EDGE(my_edge, my_edge_iterator, (((BasicBlockObject*)self)->_block->succs))
    {
      PyObject* block = BasicBlock_FromBlock(my_edge->dest);
      PyList_Append(ret, block);

      Py_DECREF(block);
    }

  return ret;
}

static int findMarker(basic_block block, tree marker, block_stmt_iterator* iter)
{
  for(*iter = bsi_start(block);
      !bsi_end_p(*iter);
      bsi_next(iter))
    {
      if(bsi_stmt(*iter) == marker)
        {
          return 1;
        }
    }

  return 0;
}

#define WRAP_BSI_FUNC(bsi_func)									\
  do												\
    {												\
      PyObject* marker_object;									\
      PyObject* statement_object;								\
    												\
      if(PyArg_UnpackTuple(argv, "insertbefore", 2, 2, &marker_object, &statement_object) &&	\
         marker_object->ob_type == &StatementObjectType &&					\
         statement_object->ob_type == &StatementObjectType)					\
        {											\
          tree marker = ((StatementObject*)marker_object)->_stmt;				\
          tree statement = ((StatementObject*)statement_object)->_stmt;				\
    												\
          block_stmt_iterator iterator;								\
    												\
          if(findMarker(((BasicBlockObject*)self)->_block, marker, &iterator))			\
            {											\
              bsi_func(&iterator, ((StatementObject*)statement)->_stmt, BSI_SAME_STMT);		\
            }											\
        }											\
    												\
      Py_RETURN_NONE;										\
    }												\
  while(0)

static PyObject* BasicBlockInsertBefore(PyObject* self, PyObject* argv)
{
  WRAP_BSI_FUNC(bsi_insert_before);
}

static PyObject* BasicBlockInsertAfter(PyObject* self, PyObject* argv)
{
  WRAP_BSI_FUNC(bsi_insert_after);
}

#undef WRAP_BSI_FUNC

// BasicBlockObject - setup

static PyObject* setupBasicBlockType()
{
  BasicBlockObjectType.ob_type = &PyType_Type;

  assert(!PyType_Ready(&BasicBlockObjectType));

  return (PyObject*)&BasicBlockObjectType;
}

#endif  //BASICBLOCK_H//
