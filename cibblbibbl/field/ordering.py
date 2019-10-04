from . import base

class PropTupCompar(base.CustomKeyDescriptorBase):
  """
  Property tuple comparisor descriptor. The getter returns a
  comparision method.
  """

  def __init__(self, *propnames, key=None):
    super().__init__(key=key)
    self.propnames = propnames

  def __get__(self, instance, owner):
    if instance is None:
      return self
    return (
      lambda other:
      getattr(
        tuple(getattr(instance, na) for na in self.propnames),
        self.key
      )(
        tuple(getattr(other, na) for na in self.propnames),
      )
    )
