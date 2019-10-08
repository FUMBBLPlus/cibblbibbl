import inspect

from . import base


class AttrKey(base.CustomKeyDescriptorBase):

  def __init__(self, attrname, key=None, default=None):
    super().__init__(key=key)
    self.attrname = attrname
    self.default = default

  def __get__(self, instance, owner):
    if instance is None:
      return self
    o = getattr(instance, self.attrname)
    try:
      return o[self.key]
    except KeyError as e:
      if self.default is KeyError:
        raise
      else:
        return self.default


class Call:

  def __init__(self, f, *args, **kwargs):
    self.f = f
    self.args = args
    self.kwargs = kwargs

  def __get__(self, instance, owner):
    if instance is None:
      return self
    return self.f(*self.args, **self.kwargs)


class Constant:

  def __init__(self, value):
    self._value = value

  def __get__(self, instance, owner):
    if instance is None:
      return self
    return self._value


class DiggedAttr:

  def __init__(self, *attrkeys):
    self.attrkeys = attrkeys

  def __get__(self, instance, owner):
    if instance is None:
      return self
    v = instance
    for k in self.attrkeys:
      v = getattr(v, k)
    return v


class DiggedKeys:

  def __init__(self, attrname, *keys,
      default = None,
      f_typecast = None,
  ):
    self.attrname = attrname
    self.keys = keys
    self.default = default
    self.f_typecast = f_typecast
    try:
      self.f_typecast_a = len(
          inspect.getargspec(f_typecast).args
      )
    except TypeError:
      self.f_typecast_a = 1

  def __get__(self, instance, owner):
    if instance is None:
      return self
    o = getattr(instance, self.attrname)
    for k in self.keys:
      try:
        o = o[k]
      except KeyError as e:
        if self.default is KeyError:
          raise
        else:
          return self.default
    if self.f_typecast:
      if self.f_typecast_a == 2:
        o = self.f_typecast(o, instance)
      elif self.f_typecast_a == 3:
        o = self.f_typecast(o, instance, self)
      else:
        o = self.f_typecast(o)
    return o

