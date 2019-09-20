
import cibblbibbl

if __name__ == "__main__":
  show_team_id = True
  Ts = cibblbibbl.tournament.byGroup["cibbl"].values()
  standings_texts = []
  exp_m = cibblbibbl.tournament.export.standings.plaintext
  ss = []
  for T in Ts:
    S = T.standings
    if not S:
      continue
    s0 = exp_m.default(S, show_team_id=show_team_id)
        # TODO: handler matching standings func
    s1 = f'Standings of {T.name} ({T.ID} • {T.style})' \
      f'\n\n{s0}'
    ss.append(s1)
  p = cibblbibbl.data.path
  p /= f'{T.group_key}/tournament/standings.txt'
  text = "\n\n\n\n".join(ss)
  with p.open("w") as f:
      f.write(text)
  print(text)
