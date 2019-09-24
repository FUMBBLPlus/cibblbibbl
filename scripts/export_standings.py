
import cibblbibbl

if __name__ == "__main__":
  show_team_id = True
  Ts = sorted(
      cibblbibbl.tournament.byGroup["cibbl"].values(),
      key=lambda T: T.sortId,
  )
  exp_m = cibblbibbl.tournament.export.standings.plaintext
  texts = []
  for T in Ts:
    S = T.standings
    if not S:
      continue
    s0 = exp_m.default(S, show_team_id=show_team_id)
        # TODO: handler matching standings func
    if T.Id.isdecimal():
      s1 = f'Standings of {T.name} ({T.Id} • {T.style})' \
        f'\n\n{s0}'
    else:
      s1 = f'Prestiges of {T.name}\n\n{s0}'
    texts.append(s1)
  p = cibblbibbl.data.path
  p /= f'{T.group_key}/tournament/standings.txt'
  text = "\n\n\n\n".join(texts)
  with p.open("w") as f:
      f.write(text)
  print(text)
