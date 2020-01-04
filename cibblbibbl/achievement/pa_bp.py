import collections
import cibblbibbl

from .mastercls import PlayerAchievement

from .. import field
from . import exporttools


class PA_BP_Mother(PlayerAchievement):

  children = {}

  rank = 10

  @classmethod
  def agent00(cls, group):
    for cls1 in cls.children.values():
      yield from cls1.agent00(group)

  @classmethod
  def agent01(cls, group):
    cls_StarPlayer = cibblbibbl.player.StarPlayer
    cls_MercenaryPlayer = cibblbibbl.player.MercenaryPlayer
    chldren_by_name = {}
    chldren_by_region = {}
    for cls_c in cls.children.values():
      CC = cls_c.defaultconfig_of_group(group)._data
      chldren_by_name[CC["name"]] = (cls_c, CC)
      region = CC.get("region")
      if region:
        chldren_by_region[region] = (cls_c, CC)
    for T in group.tournaments.values():
      if T.awarded == "yes":
        continue  # collected by the iterexisting agent
      if T.posonly == "yes":
        continue
      if T.status != "Completed":
        continue
      cls_c, CC = None, None
      name = T.bestplayersname
      if name:
        cls_c, CC = chldren_by_name[name]
      elif T.season.name != "Spring":
        continue
      PP = T.playerperformances()
      bestplayers0 = T.bestplayers()
      bestplayers = collections.defaultdict(set)
      for k, Pl in bestplayers0.items():
        if Pl:
          bestplayers[Pl].add(k)
      for Pl, categories in bestplayers.items():
        Te = PP[Pl]["team"]
        if not name:
          region = T.config.get("region")
          if not region:
            if isinstance(Pl, cls_StarPlayer):
              cls_c = PA_BPR_StarPlayersGuild
              CC = cls_c.defaultconfig_of_group(group)._data
            elif isinstance(Pl, cls_MercenaryPlayer):
              cls_c = PA_BPR_MercenaryGuild
              CC = cls_c.defaultconfig_of_group(group)._data
            else:
              region = G.rosterregion[Te.roster_name]
          if region:
            cls_c, CC = chldren_by_region[region]
        value = CC["value"]
        A_categories = set(cls_c.default_categories)
        categories = categories & A_categories
        if not categories:
          continue
        A = cls_c(T, Pl)
        if A["status"] == "proposed":
          A["prestige"] = value
          A["status"] = "proposed"  # explicit
          # TODO add team
          A["categs"] = sorted(categories)
        yield A

  @classmethod
  def agent99(cls, group):
    for cls1 in cls.children.values():
      yield from cls1.agent99(group)



class PA_BP_Child(PlayerAchievement):

  sortrank = 1005

  default_categories = (  # TODO hardcoded; make it config based
      "SPP",
      "Touchdowns",
      "Casualties",
      "Interceptions",
      "Completions",
      "Fouls",
      "Blocking Scorer",
      "Blocking Thrower",
      "Scoring Thrower",
      "Triple",
      "Allrounder",
  )

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    PA_BP_Mother.children[cls.clskey()] = cls

  def export_plaintext(self, show_Ids=False):
    s0 = exporttools.idpart(self, show_Ids)
    team = exporttools.team(self)
    if hasattr(team, "name"):
      teamname = team.name
    else:
      teamname = team
    s1 = f'{self.subject.name} ({teamname})'
    s2 = f' ({", ".join(sorted(self["categs"]))})'
    s3 = exporttools.alreadyearned(self)
    return s0 + s1 + s2 + s3


class PA_BP_Youngbloods(PA_BP_Child): pass

class PA_BPW_ChildOfWinter(PA_BP_Child): pass

class PA_BPR_Albion_Norsca(PA_BP_Child): pass
class PA_BPR_AthelLoren(PA_BP_Child): pass
class PA_BPR_Cathay_Nippon(PA_BP_Child): pass
class PA_BPR_ChaosWastelands(PA_BP_Child): pass
class PA_BPR_DarkLands(PA_BP_Child): pass
class PA_BPR_DeepCaverns(PA_BP_Child): pass
class PA_BPR_EasternSteppes_MountainsOfMourn(PA_BP_Child): pass
class PA_BPR_ElementalPlanes(PA_BP_Child): pass
class PA_BPR_Empire(PA_BP_Child): pass
class PA_BPR_GreatOcean(PA_BP_Child): pass
class PA_BPR_HauntedHills(PA_BP_Child): pass
class PA_BPR_Ind_Lumbria_Hinterlands(PA_BP_Child): pass
class PA_BPR_LandsOfTheDead(PA_BP_Child): pass
class PA_BPR_Lustria(PA_BP_Child): pass
class PA_BPR_MercenaryGuild(PA_BP_Child): pass
class PA_BPR_OldWorld(PA_BP_Child): pass
class PA_BPR_RealmsOfChaos(PA_BP_Child): pass
class PA_BPR_Skavenblight(PA_BP_Child): pass
class PA_BPR_Southlands_Araby(PA_BP_Child): pass
class PA_BPR_StarPlayersGuild(PA_BP_Child): pass
class PA_BPR_Sylvania(PA_BP_Child): pass
class PA_BPR_Ulthuan_Naggaroth(PA_BP_Child): pass
class PA_BPR_WorldEdgeMountains(PA_BP_Child): pass

class PA_BPS_ACC(PA_BP_Child): pass
class PA_BPS_BC(PA_BP_Child): pass
class PA_BPS_CAK(PA_BP_Child): pass
class PA_BPS_CBE(PA_BP_Child): pass
class PA_BPS_CVI(PA_BP_Child): pass
class PA_BPS_Climax(PA_BP_Child): pass
class PA_BPS_DG(PA_BP_Child): pass
class PA_BPS_EE(PA_BP_Child): pass
class PA_BPS_FG(PA_BP_Child): pass
class PA_BPS_GCECC(PA_BP_Child): pass
class PA_BPS_HoG(PA_BP_Child): pass
class PA_BPS_LC(PA_BP_Child): pass
class PA_BPS_LG(PA_BP_Child): pass
class PA_BPS_MS(PA_BP_Child): pass
class PA_BPS_MaG(PA_BP_Child): pass
class PA_BPS_MuG(PA_BP_Child): pass
class PA_BPS_OC(PA_BP_Child): pass
class PA_BPS_PC(PA_BP_Child): pass
class PA_BPS_SC(PA_BP_Child): pass
class PA_BPS_SG(PA_BP_Child): pass
class PA_BPS_TGB(PA_BP_Child): pass
class PA_BPS_TGW(PA_BP_Child): pass
class PA_BPS_VC(PA_BP_Child): pass
class PA_BPS_YS(PA_BP_Child): pass

class PA_BPA_Bronze(PA_BP_Child): pass
class PA_BPA_Clay(PA_BP_Child): pass
class PA_BPA_Cloth(PA_BP_Child): pass
class PA_BPA_Copper(PA_BP_Child): pass
class PA_BPA_Gold(PA_BP_Child): pass
class PA_BPA_Granite(PA_BP_Child): pass
class PA_BPA_Iron(PA_BP_Child): pass
class PA_BPA_Marble(PA_BP_Child): pass
class PA_BPA_Silver(PA_BP_Child): pass
class PA_BPA_Tin(PA_BP_Child): pass
class PA_BPA_Wood(PA_BP_Child): pass


cls = PA_BP_Mother
