
import cibblbibbl

if __name__ == "__main__":
  show_team_id = True
  Ts = cibblbibbl.tournament.byGroup["cibbl"].values()
  standings_texts = []
  exp_m = cibblbibbl.tournament.export.standings.plaintext
  ss = ""
  for T in Ts:
    s = exp_m.default(T, show_team_id=show_team_id)
        # TODO: handler matching standings func
    if s:
      ss += f'[{T.style}] {s}\n\n\n'
  p = cibblbibbl.data.path
  p /= f'{T.group_key}/tournament/standings.txt'
  with p.open("w") as f:
      f.write(ss)
  print(ss)
