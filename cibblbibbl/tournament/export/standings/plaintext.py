from tabulate import tabulate


def default(T, *,
    show_team_id = False,
    tablefmt = None,
):
  S = T.standings
  if not S:
    return ""
  hth_trans = {-1: "", 0: "--"}
  coin_trans = {-1: "", -112: "???"}  # -112: missing
  rows = []
  headers = (["ID",] if show_team_id else [])
  headers.extend((
      "Name",
      "Roster",
      "Coach",
      "Perf.",
      "PTS",
      "HTH",
      "TDD",
      "CASD",
      "COIN",
  ))
  colalign = (["right",] if show_team_id else [])
  colalign.extend((
      "left",
      "left",
      "left",
      "left",
      "right",
      "right",
      "right",
      "right",
      "right",
  ))
  for r in S:
    Te = r["team"]
    row = ([str(Te.ID),] if show_team_id else [])
    row.extend((
        Te.name,
        Te.roster_name,
        Te.coach_name,
        r["perf"],
        r["pts"],
        hth_trans.get(r["hth"], r["hth"]),
        r["tdd"],
        r["casd"],
        coin_trans.get(r["coin"], r["coin"]),
    ))
    rows.append(row)
  tabulate_s = tabulate(
      rows,
      colalign=colalign,
      headers=headers,
      tablefmt=tablefmt,
  )
  return f'Standings of {T.name} (#{T.ID})' \
      f'\n\n{tabulate_s}'
