
import cibblbibbl

from export_standings import tournament_name

if __name__ == "__main__":
  G = cibblbibbl.CIBBL
  G.init()
  show_Ids = True
  Ts = sorted(G.tournaments.values())
  m_exp = cibblbibbl.tournament.export.prestiges.plaintext
  f_exp = m_exp.export
  texts = []
  for T in Ts:
    if not T.ismain:
      continue
    s0 = f_exp(T, show_Ids=show_Ids)
    tournament_title = tournament_name(T, show_Ids)
    s1 = f'Prestiges of {tournament_title}'
    texts.append(f'{s1}\n\n{s0}')
  p = cibblbibbl.data.path
  p /= f'{G.key}/tournament/prestiges.txt'
  text = "\n\n\n\n".join(texts)
  with p.open("w", encoding="utf8") as f:
      f.write(text)
  print(text)
