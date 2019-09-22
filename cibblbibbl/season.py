import cibblbibbl


class Season(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  def __init__(self, group_key, year_nr:int, nr:int):
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
  def name(self):
    seasons = self.group.settings["seasons"]
    return seasons[self.nr - 1]

  @property
  def nr(self):
    return self._KEY[2]

  @property
  def year(self):
    return cibblbibbl.year.Year(self.group_key, self.yearnr)

  @property
  def yearnr(self):
    return self._KEY[1]
