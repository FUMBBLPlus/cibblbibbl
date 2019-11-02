import collections

from . import field


import cibblbibbl


class Season(
    metaclass=cibblbibbl.helper.InstanceRepeater
):

  achievements = field.insts.self_tournament_achievements
  group = field.inst.group_by_self_group_key
  group_key = field.instrep.keyigetterproperty(0)
  matches = field.insts.matchups_matches
  matchups = field.insts.self_tournaments_matchups
  nr = field.instrep.keyigetterproperty(2)
  replays = field.insts.matches_replays
  year = field.inst.year_by_self_group_key_and_year_nr
  year_nr = field.instrep.keyigetterproperty(1)

  def __init__(self, group_key, year_nr:int, nr:int):
    self.tournaments = {}

  @property
  def name(self):
    seasons = self.group.config["seasons"]
    return seasons[self.nr - 1]

  @property
  def next(self):
    key = (self.group_key, self.year_nr, self.nr + 1)
    next = self.__class__.__members__.get(key)
    if next is None and self.year.next:
      next = sorted(self.year.next.seasons)[0]
    return next

  @property
  def prev(self):
    key = (self.group_key, self.year_nr, self.nr - 1)
    prev = self.__class__.__members__.get(key)
    if prev is None and self.year.prev:
      prev = sorted(self.year.prev.seasons)[-1]
    return prev

  @property
  def teams(self):
    return {
        Te for T in self.tournaments.values()
        for Te in T.teams
    }

  def consecutive_teams(self, past_seasons):
    fromS = self.group.config.get("partnership_introduced")
    if not fromS:
      return set()
    if [self.year_nr, self.nr] < fromS:
      return set()
    S = self
    seasons = set()
    for _ in range(past_seasons):
      if not S:
        return set()
      seasons.add(S)
      S = S.prev
    teams = set(self.group.teams)
    for S in seasons:
        if S.nr == 1:  # skip winter TODO: more sophisticated
            continue
        teams &= S.teams
    return teams

  def lastaliveplayers(self, allteams=False):
    d = {}
    if allteams:
      teams = set(self.group.teams)
    else:
      teams = set(self.teams)
    for Te in teams:
      tournaments = [
          T for T in Te.tournaments if T.season <= self
      ]
      i = -1
      while tournaments:
        lastT = tournaments[-1]
        try:
          d[Te] = lastT.lastaliveplayers(Te)
        except KeyError:
          tournaments = tournaments[:-1]
        else:
          break
    return d

  def achievementsofteams(self, allteams=False):
    d = collections.defaultdict(set)
    d_lap = self.lastaliveplayers(allteams=allteams)
    for Te, Pls in d_lap.items():
      d[Te] |= Te.achievements
      for Pl in Pls:
        d[Te] |= Pl.achievements
    return d

  def gold_partner_teams(self):
    return self.consecutive_teams(16)

  def prestigesofteams(self, allteams=False):
    ignore = {
        S for S in self.group.seasons if S.name == "Winter"
    }
    d = {}
    d_aot = self.achievementsofteams(allteams=allteams)
    for Te, As in d_aot.items():
      d2 = collections.defaultdict(lambda: 0)
      prestige = 0
      for A in As:
        value = A.prestige(season=self)
        prestige += value
        if A.subject_typename == "Team":
          T = A.tournament
          while T.above:
            T = T.above
          if T.friendly == "yes":
            continue
          if T.season <= self:
            d2[T.season] += value
      seasons = sorted(d2, reverse=True)
      ties = [d2[Se] for Se in seasons]
      if seasons:
        nonwintersince = self.since(seasons[0], ignore=ignore)
        ties = [0] * nonwintersince + ties
            # zeroes ahead if old
      ties += [0] * (6 - len(ties)) # ensure minlength (6)
      d[Te] = (prestige, tuple(ties[:6]))
    return d

  def silver_partner_teams(self):
    return self.consecutive_teams(8) - self.gold_partner_teams()

  def since(self, season, ignore=None):
    """
    Returns how many seasons has been passed since the given
    season including itself. The result is positive if the
    given season was earlier.
    """
    c = 0
    if season._KEY[1:] < self._KEY[1:]:
      while season is not self:
        if ignore is None or season not in ignore:
          c += 1
        season = season.next
    elif self._KEY[1:] < season._KEY[1:]:
      while season is not self:
        if ignore is None or season not in ignore:
          c -= 1
        season = season.prev
    return c

  def standings_without_partnership(self, allteams=False):
    d = self.prestigesofteams(allteams=allteams)
    L = [
        list(d[Te])+ [Te,]
        for Te in sorted(d, key=d.get, reverse=True)
    ]
    return L

  def standings_with_partnership(self, allteams=False):
    g = self.gold_partner_teams()
    s = self.silver_partner_teams()
    L = self.standings_without_partnership(allteams=allteams)
    for LL in L:
      if LL[2] in g:
        LL[0] += 50
      elif LL[2] in s:
        LL[0] += 25
    return sorted(L, reverse=True)

  def until(self, season):
    """
    Returns how many seasons has been passed until the given
    season including itself. The result is positive if the
    given season was later.
    """
    return -self.since(season)

