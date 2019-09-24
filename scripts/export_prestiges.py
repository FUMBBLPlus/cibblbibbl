
import cibblbibbl

if __name__ == "__main__":
  show_team_id = True
  Ts = sorted(
      cibblbibbl.tournament.byGroup["cibbl"].values(),
      key=lambda T: T.sortId,
  )
  texts = []
  exp_m = cibblbibbl.tournament.export.prestiges.plaintext
  for T in Ts:
    P = cibblbibbl.tournament.tools.prestiges.base(T)
    s0 = exp_m.default(P, show_team_id=show_team_id)
        # TODO: handler matching standings func
    if T.Id.isdecimal():
      s1 = f'Prestiges of {T.name} ({T.Id} • {T.style})' \
        f'\n\n{s0}'
    else:
      s1 = f'Prestiges of {T.name}\n\n{s0}'
    texts.append(s1)
  p = cibblbibbl.data.path
  p /= f'{T.group_key}/tournament/prestiges.txt'
  text = "\n\n\n\n".join(texts)
  with p.open("w") as f:
      f.write(text)
  print(text)
