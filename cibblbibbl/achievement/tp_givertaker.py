import collections
import cibblbibbl

from . import exporttools
from .mastercls import TeamAchievement
from .pa_bp import PA_BP_Mother
from .tp_match import TP_Match



class TP_GiverTaker_Mother(TeamAchievement):

  children = {}

  rank = 20

  agent00 = PA_BP_Mother.agent00

  @classmethod
  def agent10(cls, group):
    OCA = cibblbibbl.achievement.ta_obsidianchalice.cls
    PCA = cibblbibbl.achievement.ta_pearlchalice.cls
    for T in group.tournaments.values():
      #if T.awarded == "yes":
      #  continue  # collected by the iterexisting agent
      if T.abstract:
        continue
      if T.posonly == "yes":
        continue
      if T.friendly == "yes":
        continue
      OCs = {
        A.subject for A in OCA.__members__.values()
        if A.active(T)
      }
      PCs = {
        A.subject for A in PCA.__members__.values()
        if A.active(T)
      }
      for Mu in T.matchups:
        if Mu.abstract:
          continue
        if Mu.excluded == "yes":
          continue
        Ma = Mu.match
        if not Ma:
          continue
        teams = sorted(Mu.teams)
        T1OC = (teams[0] in OCs)
        T1PC = (teams[0] in PCs)
        T2OC = (teams[1] in OCs)
        T2PC = (teams[1] in PCs)
        if (T1OC and T2PC) or (T1PC and T2OC):
          for Te in teams:
            dTe = Mu.config["team"][str(Te.Id)]
            scorediff = dTe["scorediff"]
            if 0 < scorediff:
              A = TP_Taker(T, Te, Ma)
              value = 50
            elif scorediff < 0:
              A = TP_Giver(T, Te, Ma)
              value = -50
            else:
              continue
            if A.get("status", "proposed") == "proposed":
              A["prestige"] = value
              A["status"] = "proposed"  # explicit
            yield A



class TP_GiverTaker_Child(TeamAchievement):

  export_plaintext = TP_Match.export_plaintext



class TP_Giver(TP_GiverTaker_Child):
  sortrank = 60



class TP_Taker(TP_GiverTaker_Child):
  sortrank = 61


cls = TP_GiverTaker_Mother
