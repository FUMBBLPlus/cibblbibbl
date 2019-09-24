import texttable


def default(standings_obj, *,
    show_team_id = False,
):
  S = standings_obj
  cto_trans = {-1: "", -112: "???"}  # -112: missing
  hth_trans = {-1: "", 0: "--"}
  nr_cto_trans = {-112: "?"}  # -112: missing
  params = [
      (" #", "a", "r", 2,),
      ("Team Id", "i", "r", 7,),
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
  multiline = any(("\n" in r["team"].name) for r in S)
  table.set_deco(
      texttable.Texttable.HEADER
      | texttable.Texttable.VLINES
      | (texttable.Texttable.HLINES if multiline else 0)
  )
  table.set_cols_dtype([t[1] for t in params])
  table.set_cols_align([t[2] for t in params])
  table.set_cols_width([t[3] for t in params])
  rows = []
  for nr, r in enumerate(S, 1):
    Te = r["team"]
    pts = r["pts"]
    if 1000000 <= pts:
      pts = f'W{pts-1000000}'
    row = [
        nr_cto_trans.get(r["cto"], f'{nr}'),
        str(Te.Id),
        Te.name,
        Te.roster_name,
        Te.coach_name,
        r["perf"],
        pts,
        hth_trans.get(r["hth"], r["hth"]),
        r["scorediff"],
        r["casdiff"],
        cto_trans.get(r["cto"], r["cto"]),
    ]
    if not show_team_id:
      del row[1]
    rows.append(row)
  table.add_rows([[t[0] for t in params]] + rows)
  return table.draw()
