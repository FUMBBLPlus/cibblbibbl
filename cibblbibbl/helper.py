import json
import functools
import pathlib
import re

import cibblbibbl

EXTRA_STRIP = " ⠀"
IGNORE = "\xad"
NOTYPECAST = lambda v: v


class InstanceRepeater(type):

  def __new__(meta, name, bases, dict_):
    dict_["__members__"] = {}
    keys = set(dict_)
    for b in bases:
      keys |= set(b.__dict__)
    if "__hash__" not in keys:
      dict_["__hash__"] = (
          lambda self: hash(self._KEY)
      )
    if "__eq__" not in keys:
      dict_["__eq__"] = (
          lambda self, other: hash(self) == hash(other)
      )
    for k in (
        "__lt__",
        "__le__",
        "__ne__",
        "__gt__",
        "__ge__",
    ):
      if k not in keys:
        dict_[k] = (
            lambda self, other, k=k:
            getattr(self._KEY, k)(other._KEY)
        )
    return type.__new__(meta, name, bases, dict_)

  def __call__(cls, *args, **kwargs):
    #print("__call__", cls, args)
    if hasattr(cls, "_get_key"):
      key = cls._get_key(*args)
    else:
      key = tuple(args)
    #print("__call__", cls, args, "..")
    if key in cls.__members__:
      instance = cls.__members__[key]
    else:
      #print("type.__call__(cls, *args)")
      #instance = type.__call__(cls, *args)
      #print("instance = cls.__new__(cls)")
      instance = cls.__new__(cls)
      #print("object.__setattr__(instance, \"_KEY\", key)")
      object.__setattr__(instance, "_KEY", key)
      #print("hash(instance)")
      hash(instance)  # this raises TypeError if key is mutable
      instance.__init__(*args, **kwargs)
      cls.__members__[key] = instance
    #print("__call__", cls, args, "instance")
    return instance



# https://stackoverflow.com/a/14412901/2334951
def doublewrap(f):
  '''
  a decorator decorator, allowing the decorator to be used as:
  @decorator(with, arguments, and=kwargs)
  or
  @decorator
  '''
  @functools.wraps(f)
  def new_dec(*args, **kwargs):
    if (
        len(args) == 1
        and len(kwargs) == 0
        and callable(args[0])
    ):
      # actual decorated function
      return f(args[0])
    else:
      # decorator arguments
      return lambda realf: f(realf, *args, **kwargs)
  return new_dec



def get_api_data(ID, dir_path, api_func, *, reload=False):
  filename = f'{ID:0>8}.json'
  p = cibblbibbl.data.path / dir_path / filename
  jf = cibblbibbl.data.jsonfile(p)
  #print([p, reload, p.is_file(), p.stat().st_size])
  if reload or not p.is_file() or not p.stat().st_size:
    jf.dump_kwargs = cibblbibbl.settings.dump_kwargs
    jf.data = api_func(ID)
    jf.save()
  return jf.data



@doublewrap
def idkey(cls, attrname="ID", ftypecast=int):
  def _get_key(cls, id_: ftypecast):
    return ftypecast(id_)
  if not hasattr(cls, "_get_key"):
    setattr(cls, "_get_key", classmethod(_get_key))
  if not hasattr(cls, attrname):
    setattr(cls, attrname, property(lambda self: self._KEY))
  if "__repr__" not in cls.__dict__:  # hasattr is always True
    setattr(cls, "__repr__",
        lambda self: (
            f'{self.__class__.__name__}'
            f'({getattr(self, attrname).__repr__()})'
        )
    )
  return cls



def norm_name(s):
  s = s.strip(EXTRA_STRIP)
  s = re.sub(f'[{IGNORE}]', "", s)
  return s
