from .mastercls import Page

import cibblbibbl

from .. import field


class PrestigeStandings(Page):

  season = field.instrep.keyigetterproperty(1)

  @classmethod
  def agent01(cls, group):
    yield from (cls(group, season) for season in group.seasons)

  @property
  def configfilepath(self):
    p = (
      cibblbibbl.data.path
      / self.group.key
      / "page"
      /  f'{self.clskey()}'
      / f'y{self.season.year.nr}s{self.season.nr}.json'
    )
    return p


cls = PrestigeStandings
