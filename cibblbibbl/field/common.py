from . import base


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


class DictAttrGetterNDescriptor(base.CustomKeyDescriptorBase):

  def __init__(self, attrname, key=None, default=None):
    super().__init__(key=key)
    self.attrname = attrname
    self.default = default

  def __get__(self, instance, owner):
    if instance is None:
      return self
    d = getattr(instance, self.attrname)
    return d.get(self.key, self.default)


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
