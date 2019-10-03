import datetime


class CustomKeyDescriptorBase:

  def __init__(self, *, key=None):
    self.key = key

  def __set_name__(self, owner, name):
    self.name = name
    if self.key is None:
      self.key = name


class TimeFieldDescriptorBase(CustomKeyDescriptorBase):

  default_fmt = "%Y-%m-%d %H:%M:%S"

  def __init__(self, *args, fmt=None, **kwargs):
    super().__init__(*args, **kwargs)
    self.fmt = fmt or self.default_fmt

  def __set_name__(self, owner, name):
    self.name = name
    if self.key is None:
      self.key = name


class TimeFieldProxyNDescriptorBase(TimeFieldDescriptorBase):

  def __get__(self, instance, owner):
    if instance is None:
      return self
    t = getattr(instance, self.attrname).get(self.key)
    if t:
      return datetime.datetime.strptime(t, self.fmt)


class TimeFieldProxyDDescriptorBase(
    TimeFieldProxyNDescriptorBase
):

  def __set__(self, instance, value):
    if isinstance(value, str):
      dt = datetime.datetime.strptime(value, self.fmt)  # test
    else:
      value = value.strftime(self.fmt)
    getattr(instance, self.attrname)[self.key] = value

  def __delete__(self, instance):
    del getattr(instance, self.attrname)[self.key]
