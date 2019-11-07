import itertools

import pyfumbbl

import cibblbibbl

from . import default
from . import cbe
from .. import tools

class HighestR5Tournament(default.Tournament):

  sub = cbe.CBETournament.sub

  @property
  def matchups(self):
    if self._matchups is ...:
      ranks = self.teamranks()
      matchups = default.Tournament.matchups.fget(self)
      if self.status == "Completed":
        # ensure the highest ranked matchup win got over 100 pts
        sortf = (
            lambda Mu: sum(
                ranks[cibblbibbl.team.Team(int(teamId))]
                for teamId in Mu.config["team"]
            )
        )
        matchups_by_rank = sorted(matchups, key=sortf)
        for Mu in matchups_by_rank:
          for TP in Mu.config["team"].values():
            if not TP.get("r"):
              break  # not yet played
            elif TP["r"] == "W":
              if TP["pts"] < 1000000:
                TP["pts"] += 1000000
              break
          else:
            continue
          break
      self._matchups = tuple(
          cibblbibbl.matchup.sort_by_modified(itertools.chain(
              (
                  Mu
                  for T in self.sub.values()
                  for Mu in T._iter_matchups()
              ),
              matchups
          ))
      )
    return self._matchups

  def teamranks(self):
    ranks = {}
    for T in self.sub.values():
      for n, d in enumerate(T.standings(), 1):
        ranks[d["team"]] = n
    return ranks


def init(group_key, Id):
  return HighestR5Tournament(group_key, Id)
