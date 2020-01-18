import collections

import cibblbibbl


kreasontrans = {
    "ballAndChain": " has been hit by a ball and chain of ",
    "bitten": " was bitten by ",
    "blocked": " was blocked by ",
    "bomb": " has been hit by a bomb throwned by ",
    "chainsaw": " has been hit by a chainsaw of ",
    "crowdPushed": " got pushed into the crowd by ",
    "dodgeFail": " tackled by ",
    "eaten": " has been eaten by ",
    "fireball": " has been hit by a fireball of ",
    "fouled": " was fouled by ",
    "hitByThrownPlayer": " has been hit by a thrown player: ",
    "lightning": " has been hit by a lightning bolt of ",
    "piledOn": " was piled upon by ",
    "stabbed": " has been stabbed by ",
}

nreasontrans = {
    "ballAndChain": " has been hit by a ball and chain",
    "bitten": " was bitten by a team-mate",
    "blocked": " was blocked",
    "bomb": " has been hit by a bomb",
    "chainsaw": " has been hit by a chainsaw",
    "crowdPushed": " got pushed into the crowd",
    "dodgeFail": " failed a dodge",
    "eaten": " has been eaten",
    "fireball": " has been hit by a fireball",
    "fouled": " was fouled",
    "gfiFail": " failed to go for it",
    "hitByRock": " has been hit by a rock",
    "hitByThrownPlayer": " has been hit by a thrown player",
    "landingFail": " failed to land after being thrown",
    "leapFail": " failed a leap",
    "lightning": " has been hit by a lightning bolt",
    "piledOn": " was piled upon",
    "stabbed": " has been stabbed",
}


def _diedstr(dRPP, killerId, reason):
  if killerId:
    killer = cibblbibbl.player.player(killerId)
    oppoTe = dRPP[killer]["team"]
    return (
        f'{kreasontrans.get(reason, reason)}'
        f'{killer.name} ({_teamstr(killer, oppoTe)})'
    )
  else:
    return f'{nreasontrans.get(reason, reason)}'


def _playersseq(T, source_playersseq):
  StarPlayer = cibblbibbl.player.StarPlayer
  players = []
  for Pl in sorted(source_playersseq, key=lambda Pl: Pl.name):
    if Pl.achievements:
      prestige = sum(
          A.prestige(T.season, maxtournament=T)
          for A in Pl.achievements
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
    return team.name


def export(T, *,
    show_Ids = False,
):
  cls_StarPlayer = cibblbibbl.player.StarPlayer
  cls_RaisedDeadPlayer = cibblbibbl.player.RaisedDeadPlayer
  dTAv1 = T.teamachievementvalues(False, False, False, False)
  dPAv1 = T.playerachievementvalues()
  dRPP = T.rawplayerperformances()
  dPP = T.playerperformances()
  achievements = sorted(T.achievements)
  d_achievements = collections.defaultdict(dict)
  for A in achievements:
    d_achievements[A.clskey()][A.subject] = A
  prev_tournament = {}
  for Te in T.teams():
    prev_tournament[Te] = Te.prev_tournament(T)

  parts = []

  nrsuffix = {1: "st", 2: "nd", 3: "rd"}
  for d in reversed(T.standings()):
    nr = d["nr"]
    if nr is None:
      continue
    Te = d["team"]
    nrstr = f'{nr}{nrsuffix.get(nr, "th")} place: '
    idstr = (f'[{Te.Id}] ' if show_Ids else "")
    parts.append(nrstr + idstr + Te.name)
    tp_keys = ("tp_admin", "tp_match", "tp_standings")
    dtp = {k: 0 for k in tp_keys}
    for k in dtp:
      A = d_achievements.get(k, {}).get(Te)
      if A:
        dtp[k] = A.prestige(T.season, maxtournament=T)
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
      and A.get("status", "proposed") in {"awarded", "proposed"}
      and not isinstance(A.subject, cls_RaisedDeadPlayer)
  )):
    part = A.export_plaintext(show_Ids=show_Ids)
    if part is None:
      continue
    clskey = A.clskey()
    if clskey != prev_clskey:
      if i:
        parts.append("")
      parts.append(f'=== {A["name"]} ({A.baseprestige}) ===')
      prev_clskey = clskey
    parts.append(f'{part}')


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
      parts.append(f'{s}')

  transferred = T.transferredplayers()
  players = _playersseq(T, transferred)
  if players:
    parts.append("")
    parts.append("*** Famous and Transferred ***")
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
        name = str(Pl1)
        if isinstance(Pl1, cls_RaisedDeadPlayer):
          if Pl1.next is not None:
            Pl1 = Pl1.next
            name = str(Pl1)
          else:
            plparts = str(Pl1).split()
            plparts.insert(1, Pl1.prevreason)
            name = " ".join(plparts)
        try:
          nextTe = dRPP[Pl1]["team"]
        except KeyError:
          nextTe = Pl1.team
        nextsparts.append(f'to {nextTe.name} as {name}')
      s += f', joined {" and ".join(nextsparts)}'
      parts.append(f'{s}')

  retiredplayers = T.retiredplayers(dPP=dPP)
  players = _playersseq(T, retiredplayers)
  if players:
    parts.append("")
    parts.append("*** Famous and Retired ***")
    for Pl, prestige in players:
      d = retiredplayers[Pl]
      Te = d["team"]
      s = ""
      if show_Ids:
        s += f'[{Pl.Id}] '
      s += f'{Pl.name} ({Te.name}) ({prestige} Achiev.)'
      parts.append(f'{s}')

  return "\n".join(parts)
