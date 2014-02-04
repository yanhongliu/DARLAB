import weakref
_extent_dict = {}

def register(O):
    if str(O.__class__) not in _extent_dict:
        _extent_dict[str(O.__class__)]=weakref.WeakKeyDictionary()
    _extent_dict[str(O.__class__)][O]=None

def extent(Class):
    if str(Class) not in _extent_dict:
        return []
    return _extent_dict[str(Class)]

