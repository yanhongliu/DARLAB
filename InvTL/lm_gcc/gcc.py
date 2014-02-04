class GIMPLE:
    pass

def find_locs(pattern,bound_vars):
    """Matches pattern in gcc tree. 
        returns a list of (a,b,c), where:
        a = The GimpleObject that matched. Must be instance of GIMPLE
        b = dict containing all bound variables.
            Effectively, union of bound_vars, and all newly bound variables.
            Looks like: {"String": GIMPLE, ...}
        c = The GimpleObject that contains a. Must be instance of GIMPLE
    """
    return []
def find_locs_constrained(pattern,whatin,bound_vars):
    """Same as find_locs, but searches in whatin.
        Arguments will be from the 'c' result of find_locs
    """
    return []
#invts_base="."
