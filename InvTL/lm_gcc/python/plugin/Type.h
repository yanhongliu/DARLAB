#ifndef __TYPE_H__
#define __TYPE_H__

#include "common.h"
#include "TreeObject.h"

static tree va_list_ref_type_node;
static tree va_list_arg_type_node;

#define DEF_PRIMITIVE_TYPE(name, expansion) PyObject* name;
#define DEF_FUNCTION_TYPE_0(name, ret)
#define DEF_FUNCTION_TYPE_1(name, ret, arg1)
#define DEF_FUNCTION_TYPE_2(name, ret, arg1, arg2)
#define DEF_FUNCTION_TYPE_3(name, ret, arg1, arg2, arg3)
#define DEF_FUNCTION_TYPE_4(name, ret, arg1, arg2, arg3, arg4)
#define DEF_FUNCTION_TYPE_5(name, ret, arg1, arg2, arg3, arg4, arg5)
#define DEF_FUNCTION_TYPE_6(name, ret, arg1, arg2, arg3, arg4, arg5, arg6)
#define DEF_FUNCTION_TYPE_VAR_0(name, ret)
#define DEF_FUNCTION_TYPE_VAR_1(name, ret, arg1)
#define DEF_FUNCTION_TYPE_VAR_2(name, ret, arg1, arg2)
#define DEF_FUNCTION_TYPE_VAR_3(name, ret, arg1, arg2, arg3)
#define DEF_FUNCTION_TYPE_VAR_4(name, ret, arg1, arg2, arg3, arg4)
#define DEF_FUNCTION_TYPE_VAR_5(name, ret, arg1, arg2, arg3, arg4, arg5)
#define DEF_POINTER_TYPE(name, expansion)

static struct
{
  #include <builtin-types.def>
} primitiveTypes;

#undef DEF_PRIMITIVE_TYPE

#define DEF_PRIMITIVE_TYPE(name, expansion)				\
  primitiveTypes.name = Tree_FromTree(expansion);			\
  PyModule_AddObject(primitiveTypes_module, #name, primitiveTypes.name);

static PyObject* setupPrimitiveTypes()
{
  PyObject* primitiveTypes_module = PyModule_New("primitivetypes");
  #include <builtin-types.def> 
  return primitiveTypes_module;
}

#undef DEF_PRIMITIVE_TYPE
#undef DEF_FUNCTION_TYPE_0
#undef DEF_FUNCTION_TYPE_1
#undef DEF_FUNCTION_TYPE_2
#undef DEF_FUNCTION_TYPE_3
#undef DEF_FUNCTION_TYPE_4
#undef DEF_FUNCTION_TYPE_5
#undef DEF_FUNCTION_TYPE_VAR_0
#undef DEF_FUNCTION_TYPE_VAR_1
#undef DEF_FUNCTION_TYPE_VAR_2
#undef DEF_FUNCTION_TYPE_VAR_3
#undef DEF_FUNCTION_TYPE_VAR_4
#undef DEF_POINTER_TYPE

#endif  //TREECODE_H//
