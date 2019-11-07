import collections
import cibblbibbl

from . import agent
from .. import field
from . import exporttools
from .mastercls import TeamAchievement


class TA_CVGoldPartner(TeamAchievement):

  rank = 26
  sortrank = 40

  f_partners = lambda S: S.gold_partner_teams()

  @classmethod
  def agent01(cls, group_key):
    C = cls.defaultconfig_of_group(group_key)._data
    value = C["value"]
    G = cibblbibbl.group.Group(group_key)
    startT = G.tournaments[C["start_tournamentId"]]
    partners_of_seasons = {}
    for T in sorted(
        T for T in G.tournaments.values()
        if startT <= T
    ):
      if T.awarded == "yes":
        continue  # collected by the iterexisting agent
      if T.abstract:
        continue
      if T.posonly == "yes":
        continue
      active_partners = collections.defaultdict(set)
      for A in list(cls.__members__.values()):
        if not A.active(T):
          continue
        if A["status"] in ("proposed", "awarded"):
          active_partners[A.subject].add(A)
      if T.season in partners_of_seasons:
        partners = partners_of_seasons[T.season]
      else:
        partners = cls.f_partners(T.season)
        partners_of_seasons[T.season] = partners
      if T.status == "Completed":
        for Te in (set(active_partners) - partners):
          for A1 in active_partners[Te]:
            A1["end_tournamentId"] = T.Id
      teams = (partners - set(active_partners)) & T.teams(True)
      for Te in teams:
        A = cls(T, Te)
        if A["status"] == "proposed":
          A["prestige"] = value
          A["status"] = "proposed"  # explicit; easier to edit
        yield A

  agent50 = classmethod(agent.iterpostponed)

  def nexttournament(self):
    nexttournamentId = self.config.get("nexttournamentId")
    if nexttournamentId:
      return self.group.tournament[nexttournamentId]
    return self.subject.next_tournament(self.tournament)


cls = TA_CVGoldPartner