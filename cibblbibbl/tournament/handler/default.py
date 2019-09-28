import collections
import copy
import itertools

import pytourney

import pyfumbbl

import cibblbibbl

from .. import tools



class BaseTournament:

  def __init__(self, group_key, Id):
    self._config = ...

  def __lt__(self, other):
    return (self.group_key, self.sortId).__lt__((other.group_key, other.sortId))
  def __le__(self, other):
    return (self.group_key, self.sortId).__le__((other.group_key, other.sortId))
  def __gt__(self, other):
    return (self.group_key, self.sortId).__gt__((other.group_key, other.sortId))
  def __ge__(self, other):
    return (self.group_key, self.sortId).__ge__((other.group_key, other.sortId))

  config = cibblbibbl.group.Group.config
  group = cibblbibbl.year.Year.group
  group_key = cibblbibbl.year.Year.group_key

  @property
  def Id(self):
    return self._KEY[1]

  @property
  def matchups(self):
    return tuple()

  @property
  def next(self):
    Id = self.config.get("next")
    if Id is not None:
      return self.group.tournaments[str(Id)]
  @next.setter
  def next(self, T):
    assert T.group_key == self.group_key
    assert str(T.Id) != str(self.Id)
    self.config["next"] = T.Id
    T.config["prev"] = self.Id
  @next.deleter
  def next(self):
    T = self.group.tournaments[str(self.next)]
    assert T.group_key == self.group_key
    assert str(T.config["prev"]) == str(self.Id)
    del self.config["next"], T.config["prev"]

  ppos = cibblbibbl.config.field("ppos")

  @property
  def prev(self):
    Id = self.config.get("prev")
    if Id is not None:
      return self.group.tournaments[str(Id)]
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
  def sortId(self):
    sort_id = self.config.get("sortId")
    if sort_id is None:
      sort_id = self.Id
    return int(sort_id)
  sortId = sortId.setter(cibblbibbl.config.setter("sortId"))
  sortId = sortId.deleter(cibblbibbl.config.deleter("sortId"))

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
    if self.Id.isdecimal():
      filename = f'{self.Id:0>8}.json'
    else:
      filename = f'{self.Id}.json'
    p = cibblbibbl.data.path
    p /= f'{self.group_key}/tournament/{key}/{filename}'
    return p

  def deregister(self):
    del self.group.tournaments[str(self.Id)]
    del self.year.tournaments[str(self.Id)]
    del self.season.tournaments[str(self.Id)]
    if not self.season.tournaments:
      self.group.seasons.remove(self.season)
      self.year.seasons.remove(self.season)
    if not self.year.tournaments:
      self.group.years.remove(self.year)

  def register(self):
    self.group.tournaments[str(self.Id)] = self
    self.year.tournaments[str(self.Id)] = self
    self.season.tournaments[str(self.Id)] = self
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


class AbstractTournament(BaseTournament):

  name = cibblbibbl.config.field("name")



class Tournament(
    BaseTournament,
    metaclass=cibblbibbl.helper.InstanceRepeater,
):

  def __init__(self, group_key, Id):
    super().__init__(group_key, Id)
    self._apiget = ...
    self._apischedule = ...
    self._matchups = ...
    self._season = ...

  @property
  def apiget(self):
    if self._apiget is ...:
      self.reload_apiget()
    return self._apiget

  @property
  def apischedule(self):
    if self._apischedule is ...:
      self.reload_apischedule()
    return self._apischedule

  excluded_teams = cibblbibbl.group.Group.excluded_teams
  excluded_team_ids = cibblbibbl.group.Group.excluded_team_ids
  exclude_teams = cibblbibbl.group.Group.exclude_teams

  def _iter_matchups(self):
    for d in self.apischedule:
      team_ids = sorted(d2["id"] for d2 in d["teams"])
      matchup = cibblbibbl.matchup.Matchup(
        self.group_key,
        self.Id,
        d["round"],
        team_ids[0],
        team_ids[1],
      )
      yield matchup

  @property
  def matchups(self):
    if self._matchups is ...:
      p, n = self.prev, self.next
      if n:
        self._matchups = tuple()
      else:
        self._matchups = tuple(
            cibblbibbl.matchup.sort_by_modified(itertools.chain(
                (p._iter_matchups() if p else []),
                self._iter_matchups()
            ))
        )
    return self._matchups

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

  def reload_apiget(self, reload=False):
    self._apiget = cibblbibbl.helper.get_api_data(
        self.Id,
        "cache/api-tournament",
        pyfumbbl.tournament.get,
        reload=reload,
    )

  def reload_apischedule(self, reload=False):
    self._apischedule = cibblbibbl.helper.get_api_data(
        self.Id,
        "cache/api-tournament-schedule",
        pyfumbbl.tournament.schedule,
        reload=reload,
    )

  def standings(self):
    tpkeys = (
        "cas", "casdiff",
        "score", "scorediff",
        "tds", "tdsdiff",
        "pts", "prestige"
    )
    template = {k: 0 for k in tpkeys}
    template["cto"] = -1
    template["hth"] = -1
    template["perf"] = []
    S = collections.defaultdict(lambda: copy.deepcopy(template))
    Ccto = self.config.get("cto", {})
    Chth = self.config.get("hth", {})
    Co = self.config.get("order")
    HTH_results = []
    for Mu in self.matchups:
      if Mu.excluded == "yes":
        continue
      HTH_result = {}
      for teamId, TP in Mu.config["team_performance"].items():
        Te = cibblbibbl.team.Team(int(teamId))
        rsym = TP["rsym"]
        matchId = (Mu.match.Id if Mu.match else None)
        perf = rsym, matchId
        d = S[teamId]
        d.setdefault("team", Te)
        d["perf"].append(perf)
        for k in tpkeys:
          d[k] += TP[k]
        if rsym.lower() not in ("b", "f", "x", "-"):
          HTH_result[teamId] = TP["tds"]
      if len(HTH_result) == 2:
        HTH_results.append(HTH_result)
    bypts = collections.defaultdict(list)
    for teamId, d in S.items():
      bypts[d["pts"]].append(teamId)
    for pts, teamIds in bypts.items():
      if 1 < len(teamIds):
        pts_HTH_results = [{teamId: 0} for teamId in teamIds]
            # this ensures all nodes for HTH calculation
        for r0 in HTH_results:
            # generate edges by passing results of the group
            # members within the group
          r1 = {
              teamId: tds
              for teamId, tds in r0.items()
              if teamId in teamIds
          }
          if 1 < len(r1):
            # I do not want to pass empty dictionaries nor nodes
            # as those were ensured before
            pts_HTH_results.append(r1)
        pts_HTH = pytourney.tie.hth.calculate(pts_HTH_results)
        for teamId, hth_val in pts_HTH.items():
          S[teamId]["hth"] = Chth.get(teamId, hth_val)
    for teamId, cto_val in Ccto.items():
      S[teamId]["cto"] = cto_val
    # determine missing coin toss
    bytie = collections.defaultdict(list)
    keys = ("pts", "hth", "scorediff", "casdiff", "cto")
    for teamId, d in S.items():
      bytie[tuple(d[k] for k in keys)].append(teamId)
    for k, teamIds in bytie.items():
      if 1 < len(teamIds):
        cto_val = -112  # indicate missing
        for teamId in teamIds:
          S[teamId]["cto"] = cto_val
          Ccto = self.config.setdefault("cto", {})
              # this ensures that I write to the config file
          Ccto[teamId] = cto_val
    # determine order
    if Co is None:
      order = sorted(S, key=(
          lambda teamId: (
              -S[teamId]["pts"],
              +S[teamId]["hth"],
              -S[teamId]["scorediff"],
              -S[teamId]["casdiff"],
              -S[teamId]["cto"]
          )
      ))
    else:
      order = Co
    return [S[teamId] for teamId in order]



def init(group_key, Id):
  return Tournament(group_key, Id)
