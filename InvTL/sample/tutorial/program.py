import collections
import sets

def incr(query, o):
    # We ignore the query for now.
    
    rv = rcset()

    # Don't want to pay for a rcset constructor that takes an iterator,
    # so we do it the hard way.
    for i in (a for a in o.S for a in o.T):
        rv.add(i)

    return rv


class rcset(dict):
    """
    Implements a halfway-reasonable reference-counted set (bag).
    """
    def add(self, v):
        self[v] = self.get(v, 0) + 1

    def remove(self, v):
        c = self.get(v) - 1
        if c:
            self[v] -= 1
        else:
            del self[v]


class multimap(collections.defaultdict):
    """
    Implements a multi-map. The internal container is given to it as an argument.
    """

    def __init__(self, container):
        collections.defaultdict.__init__(self, container)
    
    def add(self, k, v):
        self[k].add(v)

    def remove(self, k, v):
        self[k].remove(v)



class C(object):
    def __init__(self):
        self.S = sets.Set()
        self.T = sets.Set()

class D(object):
    pass

d = D()
o = C()

print incr("a for a in o.S for a in o.T", o=o)

o.S.add(d)
o.T.add(d)

print incr("a for a in o.S for a in o.T", o=o)
