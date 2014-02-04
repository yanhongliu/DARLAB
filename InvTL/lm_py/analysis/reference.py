from analysis.common import has_docstring_annotation, lclassname, lname
import compiler
import sys

class Reference:
    def __init__(self, class_, identifier=None):
        self._namespace = {}
        self._class = class_
        self.name = class_._qualified_name
        self._qualified_name = self.name

    def __repr__(self):
        return "<Reference %s of type %s with name %s>" % (id(self), self._class.name, self.name)

class Instantiator:

    "Special object creation."

    def instantiate_class(self, class_, instantiator, annotation="_instantiates"):
        if not hasattr(class_, "_instances"):
            class_._instances = []

        # For interchangeable classes, return the instance associated with the class.

        if class_._instances:
            ref = class_._instances[-1]

        # For other classes, create a new instance and associate it with the class
        # and instantiator node.

        else:
            ref = Reference(class_, id(instantiator))
            class_._instances.append(ref)

        # Note the instantiation operation on the instantiator.

        if not hasattr(instantiator, annotation):
            setattr(instantiator, annotation, [])
        if class_ not in getattr(instantiator, annotation):
            getattr(instantiator, annotation).append(class_)

        return ref

def get_reference_for_class(node, cls):
    return node._instances[cls]

# vim: tabstop=4 expandtab shiftwidth=4
