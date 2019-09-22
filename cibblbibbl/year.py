import cibblbibbl


class Year(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  def __init__(self, group_key, nr:int):
    pass

  def __repr__(self):
    return (self.__class__.__name__ + "(" +
        ", ".join(f'{a!r}' for a in self._KEY) + ")")

  @property
  def group(self):
    return cibblbibbl.group.Group(self.group_key)

  @property
  def group_key(self):
    return self._KEY[0]

  @property
  def nr(self):
    return self._KEY[1]
