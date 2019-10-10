import collections
import copy
import datetime
import itertools

import pytourney

import pyfumbbl

import cibblbibbl

from ... import field
from ...jsonfile import jsonfile
from .. import tools
from . import get_handlername


class TournamentTime(field.base.TimeFieldProxyDDescriptorBase):

  def __get__(self, instance, owner):
    if instance is None:
      return self
    t = instance.config.get(self.key)
    if t:
      return datetime.datetime.strptime(t, self.fmt)
    elif instance.next:
      return getattr(instance.next, self.name)
    elif instance.above:
      return getattr(instance.above, self.name)
    elif instance.status == "In Progress":
      return
    elif instance.matchups:
      return max(Mu.modified for Mu in instance.matchups)
    return t



class BaseTournament(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  above = field.config.TournamentField()
  config = field.config.CachedConfig()
  configfilename = field.filepath.idfilename
  end = TournamentTime()
  excluded_teamIds = field.config.DDField(
      key = "excluded_teams",
      default = lambda i, d: list(),
      get_f_typecast = set,
      set_f_typecast = list,
  )
  excluded_teams = field.insts.excluded_teams
  exclude_teams = field.insts.exclude_teams
  group = field.inst.group_by_self_group_key
  group_key = field.instrep.keyigetterproperty(0)
  handlername = property(
      lambda self: get_handlername(
          self.group_key, self.Id
      )
  )
  Id = field.instrep.keyigetterproperty(1)
  ismain = property(lambda self: (not self.next))
  friendly = field.config.yesnofield("friendly",
      default=lambda inst: (inst.season.name == "Winter"),
  )
  matches = field.insts.matchups_matches
  matchups = field.common.Call(tuple)
  matchupsconfigdir = field.config.MatchupsDirectory("Id")
  name = field.config.DDField()
  posonly = field.config.yesnofield(
      "!posonly", default="no"
  )
  ppos = field.config.DDField()
  replays = field.insts.matches_replays
  rprestige = field.config.DDField(
      default=dict, set_f_typecast=dict
  )
  rpts = field.config.DDField(default=dict, set_f_typecast=dict)
  season_nr = field.config.NDField(key="season",
      f_typecast = (
          lambda v, instance:
          instance.group.season_names.index(v) + 1
      )
  )
  sortId = field.config.DDField(
      default = (lambda instance, descriptor: instance.Id),
      get_f_typecast = float, set_f_typecast = float,
  )
  year = field.config.YearField()
  year_nr = field.config.YearNrField()

  def __init__(self, group_key, Id):
    self.achievements = set()

  propnames = ("group_key", "sortId")
  __lt__ = field.ordering.PropTupCompar(*propnames)
  __le__ = field.ordering.PropTupCompar(*propnames)
  __gt__ = field.ordering.PropTupCompar(*propnames)
  __ge__ = field.ordering.PropTupCompar(*propnames)
  del propnames

  @property
  def configfilepath(self):
    return self.filepath("config")

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
  season = season.deleter(field.config.deleter("season"))

  @property
  def status(self):
    status = self.config.get("status")
    if status:
      return status
    if self.next:
      return self.next.status
    elif self.above:
      return self.above.status
    return "Unknown"
  status = status.setter(field.config.setter("status"))
  status = status.deleter(field.config.deleter("status"))

  def filepath(self, key):
    p = cibblbibbl.data.path
    fname = self.configfilename
    p /= f'{self.group_key}/tournament/{key}/{fname}'
    return p

  def unregister(self):
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


class AbstractTournament(BaseTournament):
  abstract = field.common.Constant(True)



class Tournament(BaseTournament):

  abstract = field.common.Constant(False)
  apiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.tournament.get, "cache/api-tournament"
  )
  apischedule = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.tournament.schedule,
      "cache/api-tournament-schedule",
  )
  name = field.config.DDField(
      default=lambda inst, desc: inst.apiget(desc.key)
  )

  def __init__(self, group_key, Id):
    super().__init__(group_key, Id)
    self._matchups = ...
    self._season = ...

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
    for p in self.matchupsconfigdir.glob("a-*.json"):
      jf = jsonfile(
          p,
          default_data = {},
          autosave = True,
          dump_kwargs = dict(self.dump_kwargs),
      )
      d = jf.data
      filekeys = p.name.split("-")[1:]
      keys = jf.data.get("keys") or filekeys
      matchup = cibblbibbl.matchup.AbstractMatchup(
        self.group_key,
        self.Id,
        *keys,
        filekeys=filekeys
      )
      matchup._config = d
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
  def rprestige(self):
    d = self.config.get("rprestige", {})
    if not d and self.friendly == "no":
       d = {
          "W": 3,
          "B": 3,
          "D": 1,
          "C": -10,
      }
    return d
  rprestige = rprestige.setter(field.config.setter("rprestige"))
  rprestige = rprestige.deleter(field.config.deleter(
      "rprestige"
  ))

  @property
  def rpts(self):
    d = self.config.get("rpts", {})
    if not d:
      if self.season.name == "Summer":
        d = {
            "W": 2,
            "D": 1,
            "B": 2,
        }
      else:
        d = {
            "W": 3,
            "D": 1,
            "B": 3,
        }
    return d
  rpts = rpts.setter(field.config.setter("rpts"))
  rpts = rpts.deleter(field.config.deleter("rpts"))

  @property
  def season_nr(self):
    season_name = self.config.get("season", ...)
    season_names = self.group.season_names
    if season_name is ...:
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
    status = self.config.get("status")
    if status:
      return status
    if self.next:
      return self.next.status
    elif self.above:
      return self.above.status
    return self.apiget["status"]
    status = status.setter(BaseTournament.status.fset)
    status = status.deleter(BaseTournament.status.fdel)

  @property
  def style(self):
    style_idx = int(self.apiget["type"]) - 1
    return pyfumbbl.tournament.styles[style_idx]

  @property
  def year_nr(self):
    year_nr = self.config.get("year", ...)
    if year_nr is ...:
      year_nr = int(self.apiget["season"])
      self.year = year_nr  # saves in the config
      return self.year_nr
    else:
      return int(year_nr)

  def standings(self):
    tpkeys = (
        "cas", "casdiff",
        "score", "scorediff",
        "td", "tddiff",
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
      for teamId, TP in Mu.config["team"].items():
        if teamId.isdecimal():
          Te = cibblbibbl.team.Team(int(teamId))
        else:
          Te = self.get_team(teamId)
        r = TP["r"]
        matchId = (Mu.match.Id if Mu.match else None)
        perf = r, matchId
        d = S[teamId]
        d.setdefault("team", Te)
        d["perf"].append(perf)
        for k in tpkeys:
          d[k] += TP.get(k, 0)
        if r.lower() not in ("b", "f", "x", "-", ""):
          HTH_result[teamId] = TP["td"]
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
              -S[teamId]["tddiff"],
              -S[teamId]["casdiff"],
              -S[teamId]["cto"]
          )
      ))
    else:
      order = [str(teamId) for teamId in Co]
    S.default_factory = None
        # close defaultdict so it can raise KeyError exceptions
    return [S[teamId] for teamId in order if teamId in S]



def init(group_key, Id):
  return Tournament(group_key, Id)
