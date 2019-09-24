import copy

import pyfumbbl

import cibblbibbl

from .. import tools



class BaseTournament:

  def __init__(self, group_key, ID):
    self._config = None

  def __lt__(self, other):
    return (self.group_key, self.sortID).__lt__((other.group_key, other.sortID))
  def __le__(self, other):
    return (self.group_key, self.sortID).__le__((other.group_key, other.sortID))
  def __gt__(self, other):
    return (self.group_key, self.sortID).__gt__((other.group_key, other.sortID))
  def __ge__(self, other):
    return (self.group_key, self.sortID).__ge__((other.group_key, other.sortID))

  config = cibblbibbl.group.Group.config
  group = cibblbibbl.year.Year.group
  group_key = cibblbibbl.year.Year.group_key

  @property
  def ID(self):
    return self._KEY[1]

  matchups = cibblbibbl.group.Group.matchups

  @property
  def next(self):
    ID = self.config.get("next")
    if ID is not None:
      return self.group.tournaments[str(ID)]
  @next.setter
  def next(self, T):
    assert T.group_key == self.group_key
    assert str(T.ID) != str(self.ID)
    self.config["next"] = T.ID
    T.config["prev"] = self.ID
  @next.deleter
  def next(self):
    T = self.group.tournaments[str(self.next)]
    assert T.group_key == self.group_key
    assert str(T.config["prev"]) == str(self.ID)
    del self.config["next"], T.config["prev"]

  ppos = cibblbibbl.config.field("ppos")

  @property
  def prev(self):
    ID = self.config.get("prev")
    if ID is not None:
      return self.group.tournaments[str(ID)]
  @prev.setter
  def prev(self, T):
    T.next = self
  @prev.deleter
  def prev(self):
    T = self.group.tournaments[str(self.prev)]
    del T.next

  @property
  def rsym(self):
    return self.config.get("rsym", {})

  @property
  def sortID(self):
    sort_id = self.config.get("sortID")
    if sort_id is None:
      sort_id = self.ID
    return int(sort_id)
  sortID = sortID.setter(cibblbibbl.config.setter("sortID"))
  sortID = sortID.deleter(cibblbibbl.config.deleter("sortID"))

  @property
  def season(self):
    return cibblbibbl.season.Season(
        self.group.key, self.year.nr, self.season_nr
    )
  @season.setter
  def season(self, season):
    if hasattr(season, "nr"):
      assert season.group is self.group
      assert season.year is self.year
    else:
      season_lownames = tuple(
          s.lower() for s in self.group.season_names
      )
      if hasattr(season, "isdecimal") and season.isdecimal():
        assert season <= len(season_lownames)
        season = cibblbibbl.season.Season(
          self.group.key, self.year.nr, int(season)
        )
      elif hasattr(season, "lower"):
        season = season.lower()
        try:
          season_i = season_lownames.index(season)
        except ValueError:
          raise ValueError(f'season not found: {season!r}')
        else:
          season_nr = season_i + 1
        season = cibblbibbl.season.Season(
          self.group.key, self.year.nr, season_nr
        )
      else:
        raise ValueError(f'season not found: {season!r}')
    self.config["season"] = season.name
  season = season.deleter(cibblbibbl.config.deleter("season"))

  @property
  def season_nr(self):
    season_name = self.config["season"]
    return self.group.season_names.index(season_name) + 1

  year = cibblbibbl.season.Season.year
  @year.setter
  def year(self, year):
    if hasattr(year, "nr"):
      assert year.group is self.group
      year_nr = year.nr
    else:
      year_nr = int(year)
    self.config["year"] = year_nr
  year = year.deleter(cibblbibbl.config.deleter("year"))

  @property
  def year_nr(self):
    return int(self.config["year"])



  def filepath(self, key):
    if self.ID.isdecimal():
      filename = f'{self.ID:0>8}.json'
    else:
      filename = f'{self.ID}.json'
    p = cibblbibbl.data.path
    p /= f'{self.group_key}/tournament/{key}/{filename}'
    return p

  def deregister(self):
    del self.group.tournaments[str(self.ID)]
    del self.year.tournaments[str(self.ID)]
    del self.season.tournaments[str(self.ID)]
    if not self.season.tournaments:
      self.group.seasons.remove(self.season)
      self.year.seasons.remove(self.season)
    if not self.year.tournaments:
      self.group.years.remove(self.year)

  def itermatchups(self):
    yield from []

  def register(self):
    self.group.tournaments[str(self.ID)] = self
    self.year.tournaments[str(self.ID)] = self
    self.season.tournaments[str(self.ID)] = self
    self.group.years.add(self.year)
    self.group.seasons.add(self.season)
    self.year.seasons.add(self.season)

  def reload_config(self):
    dump_kwargs = cibblbibbl.settings.dump_kwargs
    jf = cibblbibbl.data.jsonfile(
        self.filepath("config"),
        default_data = {},
        autosave=True,
        dump_kwargs=dump_kwargs
    )
    self._config = jf.data

  def standings_keyf(self, d, ID):
    row = d[ID]
    return (
      -row["pts"],
      +row["hth"],
      -row["scorediff"],
      -row["casdiff"],
      -row["cto"]
  )



class AbstractTournament(BaseTournament):

  name = cibblbibbl.config.field("name")



class Tournament(
    BaseTournament,
    metaclass=cibblbibbl.helper.InstanceRepeater,
):

  def __init__(self, group_key, ID):
    super().__init__(group_key, ID)
    self._apiget = None
    self._apischedule = None
    self._season = None
    self._standings = None

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

  excluded_teams = cibblbibbl.group.Group.excluded_teams
  excluded_team_ids = cibblbibbl.group.Group.excluded_team_ids
  exclude_teams = cibblbibbl.group.Group.exclude_teams

  @property
  def name(self):
    return self.config.get("name") or self.apiget["name"]
  name = name.setter(cibblbibbl.config.setter("name"))
  name = name.deleter(cibblbibbl.config.deleter("name"))

  @property
  def rsym(self):
    d = self.config.get("rsym", {})
    dprest = d.setdefault("prestige", {})
    if not dprest and self.season.name != "Winter":
      dprest.update({
          "W": 3,
          "B": 3,
          "D": 1,
          "C": -10,
      })
    dpts = d.setdefault("pts", {})
    if not dpts:
      if self.season.name == "Summer":
        dpts.update({
          "W": 2,
          "D": 1,
          "B": 2,
        })
      else:
        dpts.update({
          "W": 3,
          "D": 1,
          "B": 3,
        })
    dscore = d.setdefault("score", {
        "B": 2,
    })
    dscorediff = d.setdefault("scorediff", {
        "B": 2,
        "b": -2,
        "F": -2,
    })
    return d
  rsym = rsym.setter(cibblbibbl.config.setter("rsym"))
  rsym = rsym.deleter(cibblbibbl.config.deleter("rsym"))

  @property
  def season_nr(self):
    season_name = self.config.get("season")
    season_names = self.group.season_names
    if season_name is None:
      tournament_name = self.name.lower()
      gen = reversed(list(enumerate(season_names, 1)))
          # I go reversed as I want a Spring/Summer tournament
          # to be handled as Summer
      for season_nr, season_name in gen:
        if season_name.lower() in tournament_name:
          self.season = season_name
              # I want to save it in the config
          return self.season_nr  # now from the config
      else:
        raise Exception(f'season not found for {self}')
    else:
      return season_names.index(season_name) + 1

  @property
  def standings(self):
    if self._standings is None:
      self.reload_standings()
    return self._standings

  @property
  def status(self):
    return self.apiget["status"]

  @property
  def style(self):
    style_idx = int(self.apiget["type"]) - 1
    return pyfumbbl.tournament.styles[style_idx]

  @property
  def year_nr(self):
    year_nr = self.config.get("year")
    if year_nr is None:
      year_nr = int(self.apiget["season"])
      self.year = year_nr
      return self.year_nr
    else:
      return int(year_nr)

  def itermatchups(self):
    for d in self.apischedule:
      team_ids = sorted(d2["id"] for d2 in d["teams"])
      matchup = cibblbibbl.matchup.Matchup(
        self.group_key,
        self.ID,
        d["round"],
        team_ids[0],
        team_ids[1],
      )
      yield matchup

  def reload_apiget(self, reload=False):
    self._apiget = cibblbibbl.helper.get_api_data(
        self.ID,
        "cache/api-tournament",
        pyfumbbl.tournament.get,
        reload=reload,
    )

  def reload_apischedule(self, reload=False):
    self._apischedule = cibblbibbl.helper.get_api_data(
        self.ID,
        "cache/api-tournament-schedule",
        pyfumbbl.tournament.schedule,
        reload=reload,
    )

  def reload_standings(self):
    self._standings = tools.standings.tiebroken(self)
    dump_kwargs = cibblbibbl.settings.dump_kwargs
    jf = cibblbibbl.data.jsonfile(
        self.filepath("standings"),
        data = tools.standings.export(self._standings),
        default_data = {},
        autosave=True,
        dump_kwargs=dump_kwargs
    )







def init(group_key, ID):
  return Tournament(group_key, ID)
