import collections
import cibblbibbl

from .mastercls import Achievement

class TP_Match(Achievement):

  @classmethod
  def agent01(cls):
    playerId = ""
    prestiges = collections.defaultdict(lambda: 0)
    for Mu in cls.group.matchups:
      year_nr = Mu.year_nr
      season_nr = Mu.season_nr
      for teamId, d in Mu.config["team_performance"].items():
        key = year_nr, season_nr, teamId, playerId
        prestiges[key] += d.get("prestige", 0)
    for key, prestige in prestiges.items():
      if prestige:
        i = cls(*key)
        if i.status != "accepted":
          i.baseprestige = prestige
        yield i

  @classmethod
  def byteam(cls, team):
    if hasattr(team, "Id"):
      team = team.Id
    return set(cls.inst_by_subjec.get((str(team), ""), ()))


cls = TP_Match
