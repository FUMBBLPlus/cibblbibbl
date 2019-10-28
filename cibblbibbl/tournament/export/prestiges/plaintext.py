import texttable

import cibblbibbl


def export(T, *,
    show_Ids = False,
):
  statuses = {"awarded", "proposed"}
  multiline = False
  params = [
      (" #", "a", "r", 2,),
      ("Team ID", "i", "r", 7,),
      ("Name", "t", "l", 30,),
      ("Roster", "t", "l", 19,),
      ("Coach", "t", "l", 19,),
      ("Perf.", "t", "l", 7,),
      ("GAM", "i" , "r", 3,),
      ("CV", "t", "r", 2,),
      ("POS", "t", "r", 3,),
      (" P ", "i", "r", 3,),
  ]
  if not show_Ids:
    del params[1]
  table = texttable.Texttable()
  table.set_cols_dtype([t[1] for t in params])
  table.set_cols_align([t[2] for t in params])
  table.set_cols_width([t[3] for t in params])
  rows = []
  standings = T.standings()
  for nr, r in enumerate(standings, 1):
    Te = TeofA = r["team"]
    if isinstance(Te, cibblbibbl.team.GroupOfTeams):
      multiline = True
      TeofA = Te[0] # all members has same values
      perf = "\n".join(
          "".join(r for r, matchId in seq)
          for seq in r["perfs"]
      )
    else:
      perf = "".join(r for r, matchId in r["perf"])
    As = {
        A for A in T.achievements
        if A["status"] in statuses
        and A.subject is TeofA
    }
    padmcls = cibblbibbl.achievement.tp_admin.cls
    pgamcls = cibblbibbl.achievement.tp_match.cls
    pposcls = cibblbibbl.achievement.tp_standings.cls
    pcvcls = cibblbibbl.achievement.ta_crushingvictory.cls
    padm = sum(A["prestige"] for A in As if type(A) is padmcls)
    pgam = sum(A["prestige"] for A in As if type(A) is pgamcls)
    ppos = sum(A["prestige"] for A in As if type(A) is pposcls)
    pcv = sum(A["prestige"] for A in As if type(A) is pcvcls)
    ptot = padm + pgam + pcv + ppos
    row = [
        f'{nr}',
        str(Te.Id),
        Te.name,
        Te.roster_name,
        Te.coach_name,
        perf,
        (str(pgam) if pgam else ""),
        (str(pcv) if pcv else ""),
        (str(ppos) if ppos else ""),
        (str(ptot) if ptot else ""),
    ]
    if not show_Ids:
      del row[1]
    rows.append(row)
  rows.insert(0, [t[0] for t in params])
  table.add_rows(rows)
  table.set_deco(
      texttable.Texttable.HEADER
      #| texttable.Texttable.VLINES
      | (texttable.Texttable.HLINES if multiline else 0)
  )
  return table.draw()
