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
    self.excluded_team_ids.append(teamId)


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
        cibblbibbl.matchup.sort_by_modified(
            M
            for T in self.tournaments.values()
            for M in T.matchups
        )
    )
  return self._matchups
