import collections

import cibblbibbl


def export(T):
  dPAv1 = T.playerachievementvalues()
  dPP = T.playerperformances()
  achievements = sorted(T.achievements)
  d_achievements = collections.defaultdict(dict)
  for A in achievements:
    d_achievements[A.clskey()][A.subject] = A
  prev_tournament = {}
  for Te in T.teams:
    prev_tournament[Te] = Te.prev_tournament(T)

  parts = []

  nrsuffix = {1: "st", 2: "nd", 3: "rd"}
  standings = list(enumerate(T.standings(), 1))
  for nr, d in reversed(standings):
    Te = d["team"]
    nrstr = f'{nr}{nrsuffix.get(nr, "th")}'
    parts.append(f'{nrstr} place: {Te.name}')
    TP_matchv, TP_standingsv = 0, 0
    TP_match = d_achievements.get("tp_match", {}).get(Te)
    if TP_match:
      TP_matchv = TP_match.prestige(T.season)
    TP_standings = d_achievements.get("tp_standings").get(Te)
    if TP_standings:
      TP_standingsv = TP_standings.prestige(T.season)
    prestige = TP_matchv + TP_standingsv
    preststr = f'Prestige Points Earned: {prestige}'
    dTPAv1 = dPAv1[Te]
    T0 = prev_tournament[Te]
    if T0:
      dPAv0 = T0.playerachievementvalues()
      dTPAv0 = dPAv0[Te]
    else:
      dTPAv0 = 0
    if dTPAv1 - dTPAv0:
        sign = ("+" if -1 < dTPAv1 - dTPAv0 else "")
        preststr += f' (and {sign}{dTPAv1 - dTPAv0} Achiev.)'
    parts.append(preststr)
    parts.append("")

  parts.append("")

  prev_clskey = None
  for i, A in enumerate(sorted(
      A for A in T.achievements
      if not A.clskey().startswith("tp")
  )):
    clskey = A.clskey()
    if clskey != prev_clskey:
      if i:
        parts.append("")
      parts.append(f'=== {A["name"]} ({A.baseprestige}) ===')
    if clskey.startswith("ta"):
      s = f'{A.subject.name}'
    else:
      s = f'{A.subject.name} ({dPP[A.subject]["team"].name})'
      if clskey in (
          "pa_bewaresupremekiller",
          "pa_targeteliminated",
      ):
        victim = cibblbibbl.player.player(A["victimId"])
        s += f' ({A["reason"]} {victim.name})'
    try:
      categs = A["categs"]
    except KeyError:
      pass
    else:
      s += f' ({", ".join(sorted(categs))})'
    stack = A.stack(T.season)
    if 1 < len(stack):
      statidx = A.stackidx()
      p0 = sum(
          A1.prestige(T.season.prev)
          for A1 in stack if A1 is not A
      )
      p1 = sum(A1.prestige(T.season) for A1 in stack)
      dp = p1 - p0
      if dp:
        dpstr = f' {("+" if -1 < dp else "")}{dp}'
      else:
        dpstr = ""
      s += f' (Achievement already earned{dpstr})'
    #parts.append(statidx, A.prestige(T.season), s)
    parts.append(s)
    prev_clskey = clskey

  return "\n".join(parts)
