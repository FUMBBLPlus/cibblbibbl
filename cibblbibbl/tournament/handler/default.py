import pyfumbbl

import cibblbibbl

class BaseTournament:
  pass


class AbstractTournament(BaseTournament):
  pass


class RealTournament(BaseTournament):

  def __init__(self, group_key, ID):
    self._group_key = group_key
    self._ID = ID
    self._apiget = None
    self._apischedule = None
    self._config = None
    self._season = None

  def __repr__(self):
    return f'Tournament({self._group_key!r},{self._ID!r})'

  @property
  def apiget(self):
    if self._apiget is None:
      self.reload_apiget()
    return self._apiget

  @property
  def apischedule(self):
    if self._apischedule is None:
      self.reload_apischedule()
    return self._apischedule

  @property
  def config(self):
    if self._config is None:
      filename = f'{self.ID:0>8}.json'
      p = cibblbibbl.data.path
      p /= f'{self.group_key}/tournament/config/{filename}'
      dump_kwargs = cibblbibbl.settings.dump_kwargs
      jf = cibblbibbl.data.jsonfile(
          p,
          default_data = {},
          autosave=True,
          dump_kwargs=dump_kwargs
      )
      self._config = jf.data
    return self._config

  @property
  def name(self):
    return self.config.get("name") or self.apiget["name"]

  @property
  def group_key(self):
    return self._group_key

  @property
  def ID(self):
    return self._ID

  @property
  def PPOS(self):
    return self.config.get("PPOS")

  @property
  def season(self):
    if self._season is None:
      self.reload_season()
    return self._season

  @property
  def status(self):
    return self.get_api_data_data()["status"]

  @property
  def style(self):
    style_idx = int(self.get_api_data_data()["type"]) - 1
    return pyfumbbl.tournament.styles[style_idx]

  @property
  def year(self):
    return int(self.get_api_data_data()["season"])

  @property
  def schedule(self):
    return self.apischedule

  def reload_apiget(self):
    self._apiget = cibblbibbl._helper.get_api_data(
        self.ID,
        "cache/api-tournament",
        pyfumbbl.tournament.get,
        reload=True,
    )

  def reload_apischedule(self):
    self._apischedule = cibblbibbl._helper.get_api_data(
        self.ID,
        "cache/api-tournament-schedule",
        pyfumbbl.tournament.schedule,
        reload=True,
    )

  def reload_season(self):
    t = cibblbibbl.tournament.tools.types.Season
    S = cibblbibbl.settings.settings(self.group_key)
    seasons = tuple(S["seasons"])
    lowname = self.name.lower()
    for n, s in reversed(list(enumerate(seasons, 1))):
      if s.lower() in lowname:
        self._season = t(n, s)
    return t(None, "")



class Tournament(RealTournament):
  pass


def init(group_key, ID):
  return Tournament(group_key, ID)
