
import cibblbibbl

def tournament_name(T, show_Ids=True):
  s = ""
  if not T.abstract:
    s = f'{T.Id} • {T.style}'
    t = T
    while t.prev:
      s = f'{t.prev.Id} • {t.prev.style}, {s}'
      t = t.prev
    s = f' ({s})'
  s = f'{T.longname}{s}'
  if T.status != "Completed":
    s += f' /{T.status.upper()}/'
  return s


if __name__ == "__main__":
  G = cibblbibbl.CIBBL
  G.init()
  show_Ids = True
  Ts = sorted(G.tournaments.values())
  m_exp = cibblbibbl.tournament.export.standings.plaintext
  f_exp = m_exp.export
  texts = []
  for T in Ts:
    if not T.ismain:
      continue
    s0 = f_exp(T, show_Ids=show_Ids)
    tournament_title = tournament_name(T, show_Ids)
    s1 = f'Standings of {tournament_title}'
    texts.append(f'{s1}\n\n{s0}')
  p = cibblbibbl.data.path
  p /= f'{G.key}/tournament/standings.txt'
  text = "\n\n\n\n".join(texts)
  with p.open("w", encoding="utf8") as f:
      f.write(text)
  print(text)
