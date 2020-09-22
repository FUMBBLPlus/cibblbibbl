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
from .. import performance
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
    elif instance.matchups:
      return max(Mu.modified for Mu in instance.matchups)
    return t



class BaseTournament(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  above = field.config.TournamentField()
  awarded = field.config.yesnofield("awarded", default="no")
  bestplayersname = field.config.DDField(default=None)
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
  code = field.config.DDField(default=None)
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

  __str__ = field.inst.id_and_name_str

  @property
  def configfilepath(self):
    return self.filepath("config")

  @property
  def longname(self):
    C = self.config
    G = self.group
    try:
      codedata = G.code[self.code]
    except KeyError:
      return self.name
    name = f'{G.name}'
    name += f' – Y{self.year.nr}, {self.season.name}'
    name += f' – {codedata["longname"]}'
    if C.get("suffix") and C.get("suffixpublish", True):
      name += f' {C["suffix"]}'
    return name

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
  def shortname(self):
    C = self.config
    G = self.group
    try:
      codedata = G.code[self.code]
    except KeyError:
      return self.name
    name = f'{G.name}'
    name += f' – Y{self.year.nr}, {self.season.name}'
    name += f' – {codedata["shortname"]}'
    if C.get("suffix"):
      name += f' {C["suffix"]}'
    return name

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

  def teams(self,
      with_match=False,
      friendly_all=True,
      uncompleted_all=True,
  ):
    S = set()
    teamIds = self.config.get("teamIds")
    if teamIds:
      if (
          not with_match
          or (friendly_all and self.friendly == "yes")
          or (uncompleted_all and self.status != "Completed")
      ):
        S |= {
            cibblbibbl.team.Team(int(teamId))
            for teamId in teamIds
        }
    for Mu in self.matchups:
      if Mu.excluded == "yes":
        continue
      if with_match:
        if Mu.match:
          S |= Mu.teams
        elif friendly_all and self.friendly == "yes":
          S |= Mu.teams
        elif uncompleted_all and self.status != "Completed":
          S |= Mu.teams
      else:
        S |= Mu.teams
    S -= self.excluded_teams
    S -= self.group.excluded_teams
    return S


class AbstractTournament(BaseTournament):
  abstract = field.common.Constant(True)



class Tournament(BaseTournament):

  def _apiget_force_update_func(self, o):
    self.prev_cached_status = o["status"]
    if o["status"] != "Completed":
      return True
    else:
      return False

  def _apischedule_force_update_func(self, o):
    if self.apiget["status"] != "Completed":
      return True
    elif self.prev_cached_status != "Completed":
      # defined by the previous o.status call
      return True
    else:
      return False

  abstract = field.common.Constant(False)
  apiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.tournament.get, "cache/api-tournament",
      force_update_func = _apiget_force_update_func,
  )
  apischedule = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.tournament.schedule,
      "cache/api-tournament-schedule",
      force_update_func = _apischedule_force_update_func,
  )
  name = field.config.DDField(
      default=lambda inst, desc: inst.apiget[desc.key],
      default_set_delete = False,
      delete_set_default = True,
  )

  def __init__(self, group_key, Id):
    super().__init__(group_key, Id)
    self._matchups = ...
    self._season = ...
    self.name = self.name  # ensure it in the config

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
    # admin matchups
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
          "W": 30,
          "B": 30,
          "D": 10,
          "C": -100,
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
      if self.style == "Swiss":
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

  def bestplayers(self):
    dPP = self.playerperformances()
    return performance.bestperformers(dPP)

  def deadplayers(self, *, RPP=None):
    RaisedDeadPlayer = cibblbibbl.player.RaisedDeadPlayer
    StarPlayer = cibblbibbl.player.StarPlayer
    RPP = RPP or self.rawplayerperformances()
    return {
        Pl: d["dead"] for Pl, d in RPP.items()
        if d.get("dead")
        and not Pl.nexts
    }

  def export_awards_bbcode(self):
    f = cibblbibbl.tournament.export.awards.bbcode.export
    return f(self)

  def export_awards_plaintext(self, show_Ids = False):
    f = cibblbibbl.tournament.export.awards.plaintext.export
    return f(self, show_Ids=show_Ids)

  def extraplayerperformances(self, join=False):
    dPP = self.playerperformances()
    return performance.extraperformances(dPP, join=join)

  def firstteammatches(self):
    d = {}
    for ds in self.standings():
      Te = ds["team"]
      perf = ds["perf"]
      for r, matchId in perf:
        if matchId:
          d[Te] = cibblbibbl.match.Match(matchId)
          break
      else:
        d[Te] = None
    return d

  def lastaliveplayers(self, team):
    Ma = self.lastteammatches()[team]
    if not Ma:
      Tprev = team.prev_tournament(self)
      if Tprev:
        return Tprev.lastaliveplayers(team)
      return set()
    else:
      with Ma.replay as Re:
        d = Re.aliveplayers
      Pls = d[team]
      return {
        Pl for Pl in Pls
        if Pl.permanent
      }

  def lastteammatches(self):
    d = {}
    for ds in self.standings():
      Te = ds["team"]
      perf = ds["perf"]
      for r, matchId in reversed(perf):
        if matchId:
          d[Te] = cibblbibbl.match.Match(matchId)
          break
      else:
        d[Te] = None
    return d

  def playerachievements(self):
    d = {}
    for Te in self.teams():
      lastPls = self.lastaliveplayers(Te)
      lastAs = {
        A
        for Pl in lastPls
        for A in Pl.achievements
        if A.tournament <= self
      }
      d[Te] = lastAs
    return d

  def playerachievementvalues(self):
    d = {}
    season = self.season
    for Te, lastAs in self.playerachievements().items():
      if lastAs:
        d[Te] = sum(
            A.prestige(season, maxtournament=self)
            for A in lastAs
        )
      else:
        d[Te] = 0
    return d

  def playerperformancesources(self, *, RPP=None):
    RaisedDeadPlayer = cibblbibbl.player.RaisedDeadPlayer
    StarPlayer = cibblbibbl.player.StarPlayer
    RPP = RPP or self.rawplayerperformances()
    deadplayers = {Pl for Pl, d in RPP.items() if d.get("dead")}
    perfsource0 = {Pl: {Pl} for Pl in RPP}
    exclude = set()
    for Pl in sorted(deadplayers):
      if Pl in exclude:
        continue
      if not Pl.nexts:
        continue
      if isinstance(Pl, StarPlayer):
          # Raised Star Players are too complicated to handle
          # because of their personal apothecary. Best to
          # exclude them from performance stacking.
        continue
      for Pl1 in Pl.nexts:
        if (
            isinstance(Pl1, RaisedDeadPlayer)
            and Pl1.nexts
        ):
          for Pl2 in Pl1.nexts:
            s0 = perfsource0.get(Pl2, set())
            perfsource0[Pl2] = s0 | {Pl, Pl1}
            exclude |= {Pl, Pl1}
        else:
          s0 = perfsource0.get(Pl1, set())
          perfsource0[Pl1] = s0 | {Pl,}
          exclude |= {Pl,}
    perfsource1 = {
        Pl: S
        for Pl, S in perfsource0.items()
        if Pl not in exclude
    }
    return perfsource1

  def playerperformances(self):
    perfkeys = set(performance.performancekeytrans.values())
    RPP = self.rawplayerperformances()
    d = {}
    for Pl, S in self.playerperformancesources(RPP=RPP).items():
      dt = d[Pl] = {k: 0 for k in perfkeys}
      dt["perf"] = []
      perfS = set()
      tookpart = False
      for Pl1 in sorted(S):
        ds = RPP[Pl1]
        if Pl1 is Pl:
          tookpart = True
          for k in {"team", "name", "type"} & set(ds):
            dt[k] = ds[k]
        for k in perfkeys:
          dt[k] += ds[k]
        for t in ds["perf"]:
          if t not in perfS:
            dt["perf"].append(t)
            perfS.add(t)
      else:
        for k in {"dead", "retired", "retiredlast"} & set(ds):
          dt[k] = ds[k]
      if not tookpart:
        dt["name"] = Pl.name
        dt["team"] = Pl.team
        dt["type"] = Pl.typechar
    return d

  def rawplayerperformances(self):
    perfkeys = set(performance.performancekeytrans.values())
    lastteammatchIds = {
      Te: (Ma.Id if Ma else None)
      for Te, Ma in self.lastteammatches().items()
    }
    d = {}
    for Mu in self.matchups:
      if Mu.excluded == "yes":
        continue
      matchId = (Mu.match.Id if Mu.match else None)
      for teamId, d0 in Mu.config["player"].items():
        Te = cibblbibbl.team.Team(int(teamId))
        r = Mu.config["team"][teamId]["r"]
        for playerId, d1 in d0.items():
          Pl = cibblbibbl.player.player(playerId)
          if not (Pl in d):
            d[Pl] = {k: d1.get(k, 0) for k in perfkeys}
            d[Pl]["team"] = Te
            d[Pl]["name"] = d1["name"]
            d[Pl]["type"] = d1["type"]
            d[Pl]["perf"] = [(r, matchId),]
          else:
            for k in perfkeys:
              d[Pl][k] += d1.get(k, 0)
            d[Pl]["perf"].append((r, matchId))
          if d1.get("dead") is not None:
            d[Pl]["dead"] = copy.copy(d1["dead"]._data)
            d[Pl]["dead"].insert(0, Mu.match.Id)
          if d1.get("retired") is not None:
            d[Pl]["retired"] = d1["retired"]
            if matchId == lastteammatchIds[Te]:
                # retirements of last matches are tagged
                d[Pl]["retiredlast"] = True

    return d

  def retiredplayers(self,
      last=False,
      carrylast=True,
      dPP=None,
  ):
    RaisedDeadPlayer = cibblbibbl.player.RaisedDeadPlayer
    StarPlayer = cibblbibbl.player.StarPlayer
    dPP = dPP or self.playerperformances()
    D = {}
    for Pl, d in dPP.items():
      if d.get("retired"):
        if last or not d.get("retiredlast"):
          D[Pl] = copy.deepcopy(d)
          D[Pl]["tournament"] = self
    if carrylast:
      for Te in self.teams():
        T = Te.prev_tournament(self)
        if T:
          for Pl, d in T.playerperformances().items():
            if d["team"] is Te:
              if d.get("retiredlast"):
                D[Pl] = copy.deepcopy(d)
                D[Pl]["tournament"] = T
    return D

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
    for Te in self.teams(True):
      S[str(Te.Id)].update({"team": Te})
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
        r = TP.get("r")
        if r is None:
          continue  # no result yet
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
      if d["perf"]:
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
        hth_mname = self.config.get("hth_module", "sweep")
        hth_module = getattr(pytourney.tie, f'hth_{hth_mname}')
        #print(pts_HTH_results)
        pts_HTH = hth_module.calculate(pts_HTH_results)
        for teamId, hth_val in pts_HTH.items():
          S[teamId]["hth"] = Chth.get(teamId, hth_val)
    for teamId, cto_val in Ccto.items():
      S[teamId]["cto"] = cto_val
    # determine missing coin toss
    bytie = collections.defaultdict(list)
    keys = ("pts", "hth", "scorediff", "casdiff", "cto")
    for teamId, d in S.items():
      key = tuple(d[k] for k in keys) + ((not d["perf"]),)
      bytie[key].append(teamId)
    if self.status == "Completed":
      for k, teamIds in bytie.items():
        if 1 < len(teamIds):
          cto_val = -112  # indicate missing
          for teamId in teamIds:
            if not S[teamId]["perf"]:
              continue
            S[teamId]["cto"] = cto_val
            Ccto = self.config.setdefault("cto", {})
                # this ensures that I write to the config file
            Ccto[teamId] = cto_val
      cto_val = -999  # indicate no performance
      for teamId, d in S.items():
        if not d["perf"]:
          d["cto"] = cto_val
    else:
      try:
        del self.config["cto"]
      except KeyError:
        pass
    # determine order
    if Co is None:
      order = sorted(S, key=(
          lambda teamId: (
              (not S[teamId]["perf"]),
              -S[teamId]["pts"],
              +S[teamId]["hth"],
              -S[teamId]["tddiff"],
              -S[teamId]["casdiff"],
              -S[teamId]["cto"],
              S[teamId]["team"].name,
          )
      ))
    else:
      order = [str(teamId) for teamId in Co]
    S.default_factory = None
        # close defaultdict so it can raise KeyError exceptions
    L = [S[teamId] for teamId in order if teamId in S]
    prev_sortkey = None
    prev_nr = None
    for nr, d in enumerate(L, 1):
      if not d["perf"]:
        d["nr"] = None  # no performance
      else:
        sortkey = (
            d["pts"],
            d["hth"],
            d["tddiff"],
            d["casdiff"],
            d["cto"],
        )
        if sortkey == prev_sortkey:
          d["nr"] = prev_nr
        else:
          d["nr"] = prev_nr = nr
    return L

  def teamachievements(self):
    d = {Te: set() for Te in self.teams()}
    for A in self.achievements:
      if A.subject_typename != "Team":
        continue
      Te = A.subject
      d[Te].add(A)
    return d

  def teamachievementvalues(self,
      with_admin = True,
      with_match = True,
      with_standings = True,
      with_partnership = True,
  ):
    d = {}
    season = self.season
    excluded_clskeys = set()
    if not with_admin:
      excluded_clskeys.add("tp_admin")
    if not with_match:
      excluded_clskeys.add("tp_match")
    if not with_standings:
      excluded_clskeys.add("tp_standings")
    if not with_partnership:
      excluded_clskeys.add("ta_cvgoldpartner")
      excluded_clskeys.add("ta_cvsilverpartner")
    for Te, As in self.teamachievements().items():
      As = {A for A in As if A.clskey() not in excluded_clskeys}
      if As:
        d[Te] = sum(
            A.prestige(season, maxtournament=self) for A in As
        )
      else:
        d[Te] = 0
    return d

  def transferredplayers(self, *, RPP=None):
    RaisedDeadPlayer = cibblbibbl.player.RaisedDeadPlayer
    StarPlayer = cibblbibbl.player.StarPlayer
    RPP = RPP or self.rawplayerperformances()
    return {
        Pl: d["dead"] for Pl, d in RPP.items()
        if d.get("dead")
        and Pl.nexts
    }


def init(group_key, Id):
  return Tournament(group_key, Id)
