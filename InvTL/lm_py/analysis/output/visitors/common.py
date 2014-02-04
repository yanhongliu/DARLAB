from compiler.visitor import ASTVisitor
import analysis.reference
from analysis.common import has_docstring_annotation

class Visitor(ASTVisitor):

    "A common visitor superclass."

    def __init__(self):
        ASTVisitor.__init__(self)

    def uses_call(self, node):
        return hasattr(node, "_targets") and len(node._targets) != 0

    def is_native(self, node):
        return node.doc is not None and has_docstring_annotation(node, "NATIVE")

    def is_builtin_module(self, node):
        return node._module_name is None

# vim: tabstop=4 expandtab shiftwidth=4
