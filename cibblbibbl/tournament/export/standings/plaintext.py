import texttable

import cibblbibbl


def export(T, *,
    show_team_id = False,
):
  cto_trans = {-1: "", -112: "???"}  # -112: missing
  hth_trans = {-1: "", 0: "--"}
  nr_cto_trans = {-112: "?"}  # -112: missing
  multiline = False
  params = [
      (" #", "a", "r", 2,),
      ("Team ID", "i", "r", 7,),
      ("Name", "t", "l", 30,),
      ("Roster", "t", "l", 19,),
      ("Coach", "t", "l", 19,),
      ("Perf.", "t", "l", 7,),
      ("PTS", "i" , "r", 3,),
      ("HTH", "t", "r", 3,),
      ("TDD", "i", "r", 3,),
      ("CAD", "i", "r", 3,),
      ("CTO", "i", "r", 3,),
  ]
  if not show_team_id:
    del params[1]
  table = texttable.Texttable()
  table.set_cols_dtype([t[1] for t in params])
  table.set_cols_align([t[2] for t in params])
  table.set_cols_width([t[3] for t in params])
  rows = []
  standings = T.standings()
  for nr, r in enumerate(standings, 1):
    Te = r["team"]
    if isinstance(Te, cibblbibbl.team.GroupOfTeams):
      multiline = True
      perf = "\n".join(
          "".join(rsym for rsym, matchId in seq)
          for seq in r["perfs"]
      )
    else:
      perf = "".join(rsym for rsym, matchId in r["perf"])
    pts = r["pts"]
    if 100 <= pts:
      pts = f'W{pts-100}'
    row = [
        nr_cto_trans.get(r["cto"], f'{nr}'),
        str(Te.Id),
        Te.name,
        Te.roster_name,
        Te.coach_name,
        perf,
        pts,
        hth_trans.get(r["hth"], r["hth"]),
        r["tdsdiff"],
        r["casdiff"],
        cto_trans.get(r["cto"], r["cto"]),
    ]
    if not show_team_id:
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
