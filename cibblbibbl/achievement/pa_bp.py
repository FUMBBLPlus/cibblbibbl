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
    chldren_by_code = {}
    for cls_c in cls.children.values():
      CC = cls_c.defaultconfig_of_group(group)._data
      chldren_by_name[CC["name"]] = (cls_c, CC)
      code = CC.get("code")
      if code is not None:
        chldren_by_code[code] = (cls_c, CC)
    for T in group.tournaments.values():
      if T.awarded == "yes":
        continue  # collected by the iterexisting agent
      if T.posonly == "yes":
        continue
      if T.status != "Completed":
        continue
      cls_c, CC = None, None
      name = T.bestplayersname
      if name == "<NONE>":
        continue
      if not name:
        code = T.code
        if code:
          codedata = group.code[code]
          name = codedata.get("bestplayersname")
      if name is None and T.season.name != "Spring":
        continue
      PP = T.playerperformances()
      bestplayers0 = T.bestplayers()
      bestplayers = collections.defaultdict(set)
      for k, Pl in bestplayers0.items():
        if Pl:
          bestplayers[Pl].add(k)
      for Pl, categories in bestplayers.items():
        if name == "<ROSTER>":
          if isinstance(Pl, cls_StarPlayer):
            code = "GSP"
          elif isinstance(Pl, cls_MercenaryPlayer):
            code = "GM"
          else:
            Te = PP[Pl]["team"]
            code = group.rostercode[Te.roster_name]
          cls_c, CC = chldren_by_code[code]
        else:
          cls_c, CC = chldren_by_name[name]
        value = CC["value"]
        A_categories = set(cls_c.default_categories)
        categories = categories & A_categories
        if not categories:
          continue
        A = cls_c(T, Pl)
        if A.get("status", "proposed") == "proposed":
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


#Friendlies
class PA_BP_ChildOfWinter(PA_BP_Child): pass

# Regionals
class PA_BP_BestOfTheBest(PA_BP_Child): pass
class PA_BP_BloodForTheBloodline(PA_BP_Child): pass
class PA_BP_BugmansFinest(PA_BP_Child): pass
class PA_BP_BullsEye(PA_BP_Child): pass
class PA_BP_CavernClimber(PA_BP_Child): pass
class PA_BP_DevastationFromBeyond(PA_BP_Child): pass
class PA_BP_ElementalMyDear(PA_BP_Child): pass
class PA_BP_EmpiresFameInfamy(PA_BP_Child): pass
class PA_BP_GreatestOfVileVermin(PA_BP_Child): pass
class PA_BP_HelpfulLoner(PA_BP_Child): pass
class PA_BP_Horrific(PA_BP_Child): pass
class PA_BP_NorthernProwess(PA_BP_Child): pass
class PA_BP_OldWorldValues(PA_BP_Child): pass
class PA_BP_OrientalAesthetics(PA_BP_Child): pass
class PA_BP_SnakeCharmer(PA_BP_Child): pass
class PA_BP_SouthlandSalvation(PA_BP_Child): pass
class PA_BP_SpillBloodAndRageOn(PA_BP_Child): pass
class PA_BP_TimelessDisplay(PA_BP_Child): pass
class PA_BP_TurnItUpToEleven(PA_BP_Child): pass
class PA_BP_VerdantVibes(PA_BP_Child): pass
class PA_BP_WastelandWarrior(PA_BP_Child): pass
class PA_BP_WaveRider(PA_BP_Child): pass
class PA_BP_WithLoveFromLustria(PA_BP_Child): pass

# Cups
class PA_BP_ASpecialSpecimenIndeed(PA_BP_Child): pass
class PA_BP_AltdorfCollegeHonoraryGraduate(PA_BP_Child): pass
class PA_BP_AwakenedAtLast(PA_BP_Child): pass
class PA_BP_BlueEagleAscending(PA_BP_Child): pass
class PA_BP_CabalVisionRatingAttraction(PA_BP_Child): pass
class PA_BP_ExemplarOfGlory(PA_BP_Child): pass
class PA_BP_FinderOfTheWay(PA_BP_Child): pass
class PA_BP_FlyingColors(PA_BP_Child): pass
class PA_BP_FungusSupreme(PA_BP_Child): pass
class PA_BP_Gargantuan(PA_BP_Child): pass
class PA_BP_GrowthPotential(PA_BP_Child): pass
class PA_BP_InspiredDrinker(PA_BP_Child): pass
class PA_BP_LordsOfBalanceObsidian(PA_BP_Child): pass
class PA_BP_LordsOfBalancePearl(PA_BP_Child): pass
class PA_BP_MagicMushroomMuncher(PA_BP_Child): pass
class PA_BP_MarkOfTheDragon(PA_BP_Child): pass
class PA_BP_MasterOfTheBlackGate(PA_BP_Child): pass
class PA_BP_MasterOfTheWhiteGate(PA_BP_Child): pass
class PA_BP_NotWithAWhimperButWithABang(PA_BP_Child): pass
class PA_BP_PromiseOfGreatness(PA_BP_Child): pass
class PA_BP_RisingOutOfCarnage(PA_BP_Child): pass
class PA_BP_SCRIBBLsOutstandingPerformance(PA_BP_Child): pass
class PA_BP_SippingTheWitchesBrew(PA_BP_Child): pass
class PA_BP_StylePoints(PA_BP_Child): pass

# Divisions
class PA_BP_BronzeExcellence(PA_BP_Child): pass
class PA_BP_ClayExcellence(PA_BP_Child): pass
class PA_BP_ClothExcellence(PA_BP_Child): pass
class PA_BP_CopperExcellence(PA_BP_Child): pass
class PA_BP_ForgedGreatness(PA_BP_Child): pass
class PA_BP_GoldExcellence(PA_BP_Child): pass
class PA_BP_RefinedExcellence(PA_BP_Child): pass
class PA_BP_SilverExcellence(PA_BP_Child): pass
class PA_BP_SolidFoundation(PA_BP_Child): pass
class PA_BP_TerrificMightOfTin(PA_BP_Child): pass
class PA_BP_WhispererInTheWoods(PA_BP_Child): pass

#Etc
class PA_BP_YouthfulVibrance(PA_BP_Child): pass

cls = PA_BP_Mother
