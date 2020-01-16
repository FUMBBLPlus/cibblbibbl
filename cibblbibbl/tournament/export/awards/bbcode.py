import collections

import cibblbibbl
from cibblbibbl import bbcode

from .plaintext import kreasontrans, nreasontrans

def _diedstr(dRPP, killerId, reason):
  if killerId:
    killer = cibblbibbl.player.player(killerId)
    oppoTe = dRPP[killer]["team"]
    return (
        f'{kreasontrans.get(reason, reason)}'
        f'{bbcode.player(killer)} ({_teamstr(killer, oppoTe)})'
    )
  else:
    return f', {nreasontrans.get(reason, reason)}'


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
    return bbcode.team(team)


def export(T):
  cls_StarPlayer = cibblbibbl.player.StarPlayer
  cls_RaisedDeadPlayer = cibblbibbl.player.RaisedDeadPlayer
  dTAv1 = T.teamachievementvalues(False, False, False)
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
    nrstr = bbcode.i(nrstr)
    part = nrstr + bbcode.team(Te)
    if nr == 1:
      part = bbcode.b(part)
    parts.append(part)
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
      and A.get("status", "proposed") in {"awarded", "proposed"}
      and not isinstance(A.subject, cls_RaisedDeadPlayer)
  )):
    part = A.export_bbcode()
    if part is None:
      continue
    clskey = A.clskey()
    if clskey != prev_clskey:
      if i:
        parts.append("")
      logo_url = A.get("logo_url")
      if logo_url:
        parts.append(bbcode.img(logo_url))
      parts.append(bbcode.b(bbcode.i(A["name"])))
      parts.append(bbcode.i(A["description"]))
      prev_clskey = clskey
    parts.append(f'– {part}')


  players = _playersseq(T, T.deadplayers())
  if players:
    parts.append("")
    parts.append(bbcode.b(bbcode.i("Famous and Died")))
    for Pl, prestige in players:
      d = dPP[Pl]
      matchId, half, turn, reason, killerId = d["dead"]
      Ma = cibblbibbl.match.Match(matchId)
      Te = d["team"]
      s = ""
      s += f'{Pl.name} ({_teamstr(Pl, Te)})'
      if prestige:
        s += f' ({prestige} Achiev.)'
      s += _diedstr(dRPP, killerId, reason)
      s += f' [{bbcode.match(Ma, "match")}]'
      parts.append(f'– {s}')

  transferred = T.transferredplayers()
  players = _playersseq(T, transferred)
  if players:
    parts.append("")
    parts.append(bbcode.b(bbcode.i("Famous and Transferred")))
    for Pl, prestige in players:
      matchId, half, turn, reason, killerId = transferred[Pl]
      Ma = cibblbibbl.match.Match(matchId)
      teams = Ma.teams
      Te = dRPP[Pl]["team"]
      s = ""
      s += f'{bbcode.player(Pl)} ({_teamstr(Pl, Te)})'
      if prestige:
        s += f' ({prestige} Achiev.)'
      s += _diedstr(dRPP, killerId, reason)
      nextsparts = []
      for Pl1 in Pl.nexts:
        if isinstance(Pl1, cls_RaisedDeadPlayer):
          if Pl1.next is not None:
            Pl1 = Pl1.next
            name = bbcode.player(Pl1)
          else:
            plparts = str(Pl1).split()
            plparts.insert(1, Pl1.prevreason)
            name = " ".join(plparts)
        try:
          nextTe = dRPP[Pl1]["team"]
        except KeyError:
          nextTe = Pl1.team
        nextsparts.append(
            f'to {bbcode.team(nextTe)}'
            f' as {name}'
        )
      s += f', joined {" and ".join(nextsparts)}'
      parts.append(f'– {s}')

  retiredplayers = T.retiredplayers(dPP=dPP)
  players = _playersseq(T, retiredplayers)
  if players:
    parts.append("")
    parts.append(bbcode.b(bbcode.i("Famous and Retired")))
    for Pl, prestige in players:
      d = retiredplayers[Pl]
      Te = d["team"]
      s = f'{bbcode.player(Pl)} ({bbcode.team(Te)})'
      s += f' ({prestige} Achiev.)'
      parts.append(f'– {s}')

  return "\n".join(parts)
