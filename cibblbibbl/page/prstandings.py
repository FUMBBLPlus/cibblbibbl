from .mastercls import Page

import cibblbibbl

from .. import field


class PrestigeStandings(Page):

  category = "prstandings"
  season = field.instrep.keyigetterproperty(1)

  @classmethod
  def agent01(cls, group):
    yield from (cls(group, season) for season in group.seasons)


cls = PrestigeStandings
