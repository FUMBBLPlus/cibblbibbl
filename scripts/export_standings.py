
import cibblbibbl

def tournament_name(T, show_Ids=True):
  m_exp = cibblbibbl.tournament.export.standings.plaintext
  f_exp = m_exp.export
  G = T.group
  s0 = f_exp(T, show_Ids=show_Ids)
      # TODO: handler matching standings func
  s1 = ""
  if not T.abstract:
    s1 = f'{T.Id} • {T.style}'
    t = T
    while t.prev:
      s1 = f'{t.prev.Id} • {t.prev.style}, {s1}'
      t = t.prev
    s1 = f' ({s1})'
  return f'{T.longname}{s1}\n\n{s0}'


if __name__ == "__main__":
  G = cibblbibbl.CIBBL
  G.init()
  show_Ids = True
  Ts = sorted(G.tournaments.values())
  texts = []
  for T in Ts:
    if not T.ismain:
      continue
    s2 = f'Standings of {tournament_name(T, show_Ids)}'
    texts.append(s2)
  p = cibblbibbl.data.path
  p /= f'{G.key}/tournament/standings.txt'
  text = "\n\n\n\n".join(texts)
  with p.open("w", encoding="utf8") as f:
      f.write(text)
  print(text)
