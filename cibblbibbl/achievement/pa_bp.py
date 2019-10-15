import collections
import cibblbibbl

from .mastercls import PlayerAchievement

from .. import field


class PA_BP_Mother(PlayerAchievement):

  children = {}

  rank = 10

  @classmethod
  def agent00(cls, group_key):
    yield from ()

  @classmethod
  def agent01(cls, group_key):
    cls_StarPlayer = cibblbibbl.player.StarPlayer
    cls_MercenaryPlayer = cibblbibbl.player.MercenaryPlayer
    chldren_by_name = {}
    chldren_by_region = {}
    for cls_c in cls.children.values():
      CC = cls_c.defaultconfig_of_group(group_key)._data
      chldren_by_name[CC["name"]] = (cls_c, CC)
      region = CC.get("region")
      if region:
        chldren_by_region[region] = (cls_c, CC)
    G = cibblbibbl.group.Group(group_key)
    for T in G.tournaments.values():
      if T.posonly == "yes":
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
          if isinstance(Pl, cls_StarPlayer):
            cls_c = PA_BPR_StarPlayersGuild
            CC = cls_c.defaultconfig_of_group(group_key)._data
          elif isinstance(Pl, cls_MercenaryPlayer):
            cls_c = PA_BPR_MercenaryGuild
            CC = cls_c.defaultconfig_of_group(group_key)._data
          else:
            region = G.regions[Te.roster_name]
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


  agent99 = agent00



class PA_BP_Child(PlayerAchievement):

  agent00 = PA_BP_Mother.agent00
  agent99 = agent00

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



class PA_BP_Youngbloods(PA_BP_Child): pass

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
class PA_BPS_Climax(PA_BP_Child): pass
class PA_BPS_CVI(PA_BP_Child): pass
class PA_BPS_DG(PA_BP_Child): pass
class PA_BPS_EE(PA_BP_Child): pass
class PA_BPS_GCECC(PA_BP_Child): pass
class PA_BPS_HoG(PA_BP_Child): pass
class PA_BPS_LC(PA_BP_Child): pass
class PA_BPS_MS(PA_BP_Child): pass
class PA_BPS_OC(PA_BP_Child): pass
class PA_BPS_PC(PA_BP_Child): pass
class PA_BPS_SC(PA_BP_Child): pass
class PA_BPS_VC(PA_BP_Child): pass
class PA_BPS_YS(PA_BP_Child): pass


cls = PA_BP_Mother
