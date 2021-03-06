import re

import sortedcontainers

import pyfumbbl

from . import field

import cibblbibbl


@cibblbibbl.helper.idkey
class Team(metaclass=cibblbibbl.helper.InstanceRepeater):

  apiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.team.get, "cache/api-team"
  )
  apimatches = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.team.get_all_matches, "cache/api-team-matches"
  )
  config = field.config.CachedConfig()
  configfilename = field.filepath.idfilename
  legacyapiget = field.fumbblapi.CachedFUMBBLAPIGetField(
      pyfumbbl.team.get_legacy_data, "cache/lagacy-api-team",
      flags = pyfumbbl.team.PAST_PLAYERS
  )
  replays = field.insts.matches_replays


  def __init__(self, teamId: int):
    self._matchups = {}
    self.achievements = set()
    self.tournaments = sortedcontainers.SortedSet()

  __str__ = field.inst.id_and_name_str

  @property
  def coach_name(self):
    s = self.apiget["coach"]["name"]
    return cibblbibbl.helper.norm_name(s)

  @property
  def configfilepath(self):
    return (
        cibblbibbl.data.path
        / "team"
        / self.configfilename
    )

  @property
  def matches(self):
    return tuple(
        cibblbibbl.match.Match(int(d["id"]))
        for d in reversed(self.apimatches)
    )

  @property
  def name(self):
    s = self.apiget["name"]
    return cibblbibbl.helper.norm_name(s)

  @property
  def players(self):
    return {
        cibblbibbl.player.player(str(d["id"]))
        for k in ("players", "pastplayers")
        for d in self.legacyapiget.get(k, [])
    }

  @property
  def roster(self):
    return cibblbibbl.roster.Roster(int(self.rosterId))

  @property
  def rosterId(self):
    return self.apiget["roster"]["id"]

  @property
  def roster_name(self):
    s = self.apiget["roster"]["name"]
    s = re.sub(r'\s*\(.+$', '', s)  # CIBBL/BIBBL specific!
    return cibblbibbl.helper.norm_name(s)

  def matchups(self, group_key):
    return tuple(self._matchups.get(group_key, []))

  def next_match(self, match, *, _second_run=False):
    matchId = int(match.Id if hasattr(match, "Id") else match)
    gen = iter(self.apimatches)
    prev_d = None
    for d in gen:
      if int(d["id"]) == matchId:
        break
      else:
        prev_d = d
    else:
      if _second_run:
        raise ValueError(f'match #{match} not found')
      else:  # update cache
        descriptor = self.__class__.apimatches
        jf = descriptor.jf(self)
        o = descriptor.update(self, jf)
        descriptor.cache[self] = o
        return self.next_match(match, _second_run=True)
    if prev_d:
      return cibblbibbl.match.Match(int(prev_d["id"]))

  def prev_match(self, match):
    matchId = int(match.Id if hasattr(match, "Id") else match)
    gen = iter(self.apimatches)
    for d in gen:
      if int(d["id"]) == matchId:
        break
    else:
      raise ValueError(f'match #{match} not found')
    try:
      return cibblbibbl.match.Match(int(next(gen)["id"]))
    except StopIteration:
      pass

  def next_tournament(self, tournament, anygroup=False):
    G = tournament.group
    i = self.tournaments.index(tournament)
    I = len(self.tournaments) - 1
    while i < I:
      T = self.tournaments[i + 1]
      if not anygroup or T.group is G:
        return T
      i += 1

  def prev_tournament(self, tournament,
      anygroup=False,
      withmatch=True,
  ):
    i = self.tournaments.index(tournament)
    for i in range(i, 0,-1):
      T = self.tournaments[i - 1]
      if not anygroup and T.group is not tournament.group:
        continue
      if withmatch and self not in {
          Te for Ma in T.matches for Te in Ma.teams
      }:
        continue
      return T

  def search_player(self, name,
      in_pastplayers = True,
      _second_run = False,
  ):
    S = set()
    d = self.legacyapiget
    if in_pastplayers and d.get("pastplayers"):
      L = d["players"] + d["pastplayers"]
    else:
      L = d["players"]
    for p in L:
      if p["name"] == name:
        playerId = str(p["id"])
        S.add(cibblbibbl.player.player(playerId, name=name))
    if not _second_run and not S:  # update and research
      descriptor = self.__class__.legacyapiget
      jf = descriptor.jf(self)
      o = descriptor.update(self, jf)
      descriptor.cache[self] = o
      return self.search_player(name,
          in_pastplayers = in_pastplayers,
          _second_run = True,
      )
    return S



class GroupOfTeams(tuple):

  def __repr__(self):
    return f'{self.__class__.__name__}{super().__repr__()}'

  @property
  def Id(self):
    return "\n".join(str(Te.Id) for Te in self)

  @property
  def name(self):
    return "\n".join(Te.name for Te in self)

  @property
  def coach_name(self):
    return "\n".join(Te.coach_name for Te in self)

  @property
  def rosterId(self):
    return "\n".join(str(Te.rosterId) for Te in self)

  @property
  def roster_name(self):
    return "\n".join(Te.roster_name for Te in self)
