from . import base

class PropTupCompar(base.CustomKeyDescriptorBase):
  """
  Property tuple comparisor descriptor. The getter returns a
  comparision method.
  """

  def __init__(self, *propnames, key=None):
    super().__init__(key=key)
    self.propnames = propnames

  def _comparer(self, instance, other):
    t0 = tuple(getattr(instance, na) for na in self.propnames)
    a = getattr(t0, self.key)
    t1 = tuple(getattr(other, na) for na in self.propnames)
    r = a(t1,)
    return r

  def __get__(self, instance, owner):
    if instance is None:
      return self
    return (
        lambda other, instance=instance:
        self._comparer(instance, other)
    )


def eq_when_is(self, other):
  return (self is other)


def ne_when_is_not(self, other):
  return not (self is other)
