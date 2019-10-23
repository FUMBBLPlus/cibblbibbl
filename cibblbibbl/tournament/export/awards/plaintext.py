import collections

import cibblbibbl



def _diedstr(dRPP, killerId, reason):
  reasontrans = {"chainsaw": "sawed", "bomb": "bombed"}
  if killerId:
    killer = cibblbibbl.player.player(killerId)
    oppoTe = dRPP[killer]["team"]
    return (
        f', {reasontrans.get(reason, reason)} '
        f'by {killer.name} ({_teamstr(killer, oppoTe)})'
    )
  else:
    return f', died by {reason}'


def _playersseq(T, source_playersseq):
  StarPlayer = cibblbibbl.player.StarPlayer
  players = []
  for Pl in sorted(source_playersseq, key=lambda Pl: Pl.name):
    if Pl.achievements:
      prestige = sum(
          A.prestige(T.season) for A in Pl.achievements
      )
      if prestige or isinstance(Pl, StarPlayer):
        players.append([Pl, prestige])
    elif isinstance(Pl, StarPlayer):
      players.append([Pl, 0])
  return players


def _teamstr(player, team):
  if isinstance(player, cibblbibbl.player.StarPlayer):
    return "Star Player"
  elif isinstance(player, cibblbibbl.player.MercenaryPlayer):
    return "Mercenary"
  else:
    return team


def export(T, *,
    show_Ids = False,
):
  cls_StarPlayer = cibblbibbl.player.StarPlayer
  cls_RaisedDeadPlayer = cibblbibbl.player.RaisedDeadPlayer
  dTAv1 = T.teamachievementvalues(False, False)
  dPAv1 = T.playerachievementvalues()
  dRPP = T.rawplayerperformances()
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
    nrstr = f'{nr}{nrsuffix.get(nr, "th")} place: '
    idstr = (f'[{Te.Id}] ' if show_Ids else "")
    parts.append(nrstr + idstr + Te.name)
    tp_keys = ("tp_admin", "tp_match", "tp_standings")
    dtp = {k: 0 for k in tp_keys}
    for k in dtp:
      A = d_achievements.get(k, {}).get(Te)
      if A:
        dtp[k] = A.prestige(T.season)
    prestige = sum(dtp.values())
    if T.friendly == "no":
      preststr = f'Prestige Points Earned: {prestige}'
      dTTAv1 = dTAv1[Te]
      dTPAv1 = dPAv1[Te]
      T0 = prev_tournament[Te]
      if T0:
        dPAv0 = T0.playerachievementvalues()
        dTPAv0 = dPAv0[Te]
      else:
        dTPAv0 = 0
      achiev = dTTAv1 + dTPAv1 - dTPAv0
      if achiev:
          sign = ("+" if -1 < achiev else "")
          preststr += f' (and {sign}{achiev} Achiev.)'
      parts.append(preststr)
      parts.append("")

  parts.append("")

  prev_clskey = None
  for i, A in enumerate(sorted(
      A for A in T.achievements
      if not A.clskey().startswith("tp")
      and A["status"] in {"awarded", "proposed"}
      and not isinstance(A.subject, cls_RaisedDeadPlayer)
  )):
    clskey = A.clskey()
    if clskey != prev_clskey:
      if i:
        parts.append("")
      parts.append(f'=== {A["name"]} ({A.baseprestige}) ===')
      prev_clskey = clskey
    parts.append(A.export_plaintext(show_Ids=show_Ids))


  players = _playersseq(T, T.deadplayers())
  if players:
    parts.append("")
    parts.append("*** Famous and Died ***")
    for Pl, prestige in players:
      d = dPP[Pl]
      matchId, half, turn, reason, killerId = d["dead"]
      Ma = cibblbibbl.match.Match(matchId)
      teams = Ma.teams
      Te = d["team"]
      s = ""
      if show_Ids:
        s += f'[{Pl.Id}] '
      s += f'{Pl.name} ({_teamstr(Pl, Te)})'
      if prestige:
        s += f' ({prestige} Achiev.)'
      s += _diedstr(dRPP, killerId, reason)
      s += f' in match #{matchId}'
      parts.append(s)

  transferred = T.transferredplayers()
  players = _playersseq(T, transferred)
  if players:
    parts.append("")
    parts.append("*** Transferred ***")
    for Pl, prestige in players:
      matchId, half, turn, reason, killerId = transferred[Pl]
      Ma = cibblbibbl.match.Match(matchId)
      teams = Ma.teams
      Te = dRPP[Pl]["team"]
      s = ""
      if show_Ids:
        s += f'[{Pl.Id}] '
      s += f'{Pl.name} ({_teamstr(Pl, Te)})'
      if prestige:
        s += f' ({prestige} Achiev.)'
      s += _diedstr(dRPP, killerId, reason)
      nextsparts = []
      for Pl1 in Pl.nexts:
          if isinstance(Pl1, cls_RaisedDeadPlayer):
              Pl1 = Pl1.next
          nextTe = dRPP[Pl1]["team"]
          nextsparts.append(f'to {nextTe} as {Pl1}')
      s += f', joined {" and ".join(nextsparts)}'
      parts.append(s)

  players = _playersseq(T, T.retiredplayers())
  if players:
    parts.append("")
    parts.append("*** Famous Retired ***")
    for Pl, prestige in players:
      d = dPP[Pl]
      Te = d["team"]
      s = ""
      if show_Ids:
        s += f'[{Pl.Id}] '
      s += f'{Pl.name} ({Te.name}) (-{prestige} Achiev.)'
      parts.append(s)

  return "\n".join(parts)
