import cibblbibbl


@property
def excluded_teams(self):
  return frozenset(
      cibblbibbl.team.Team(teamId)
      for teamId in self.excluded_teamIds
  )


def exclude_teams(self, *teams):
  for v in teams:
    if hasattr(v, "Id"):
      teamId = v.Id
    else:
      teamId = int(v)
    s = set(self.excluded_teamIds)
    s.add(teamId)
    self.excluded_teamIds = sorted(s)  #TODO: remove
    team = cibblbibbl.team.Team(teamId)
    for Mu in self.matchups:
      if team in Mu.teams:
        Mu.excluded = "yes"


@property
def matches_replays(self):
  return tuple(
      Ma.replay for Ma in self.matches
  )


@property
def matchups_matches(self):
  return tuple(
      Mu.match for Mu in self.matchups if Mu.match
  )


@property
def self_tournament_achievements(self):
  return {
      A
      for T in self.tournaments.values()
      for A in T.achievements
  }


@property
def self_tournaments_matchups(self):
  if not hasattr(self, "_matchups"):
    self._matchups = tuple(
        cibblbibbl.matchup.sort_by_modified({
            Mu
            for T in self.tournaments.values()
            for Mu in T.matchups
        })
    )
  return self._matchups
