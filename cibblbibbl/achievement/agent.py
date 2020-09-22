import copy
import math

import cibblbibbl

from .. import field


def iterexisting(cls, group):
  directory = (
    cibblbibbl.data.path
    / group.key
    / "achievement"
    / f'{cls.__name__.lower()}'
  )
  for p in directory.glob("**/*.json"):
    tournamentId = p.parent.name
    if tournamentId.isdecimal():
      tournamentId = tournamentId.lstrip("0")
    tournament = group.tournaments[tournamentId]
    args = p.stem.split("~")
    args = [
        (a.lstrip("0") if (a != "0" and a.isdecimal()) else a)
        for a in args
    ]
    args = cls.argsnorm(args)
    A = cls(tournament, *args)
    yield A


def iterpostponed(cls, group):
  C = cls.defaultconfig_of_group(group)._data
  value = C["value"]
  As = {
      A for A in group.achievements
      if type(A) is cls
      and A.get("status", "proposed") in {
          "postpone proposed",
          "postponed",
      }
  }
  for A0 in As:
    T0 = A0.tournament
    T1 = A0.nexttournament()
    if T1:
      A1 = cls(T1, *A0.args)
      if "proposed" in A1.get("status", "proposed"):
        A1["status"] = "proposed"  # explicit
        A1["prestige"] = value
        A1["prev_tournamentId"] = T0.Id
      A1._prev = A0
      A0._nexts = A0._nexts | {A1,}
    yield A1


def iterprevs(cls, group):
  players = sorted(Pl for Pl in group.players if Pl.prev)
  for Pl in players:
    prevPl = Pl.prev
    Ma = cibblbibbl.match.Match(int(Pl.prevdeadmatchId))
    Mu = Ma.matchup
    if not Mu:
      continue
    T1 = Mu.tournament
    prevachievmul = Pl.prevachievmul
    for A0 in prevPl.achievements:
      if A0.group != group:
        continue
      if A0.clskey() != cls.clskey():
        continue
      if A0["status"] in {"postpone proposed", "postponed"}:
        continue
      T0 = A0.tournament
      prevsubject = A0.subject
      subject = Pl
      args = A0.key[3:]
      A = cls(T1, subject, *args)
      if not A.config:
        A.config = copy.deepcopy(A0.config._data)
        v = A0.baseprestige * prevachievmul
        A.baseprestige = math.floor(v)
        A.config["prev_tournamentId"] = T0.Id
        A.config["prev_subjectId"] = prevsubject.Id
        status = A.get("status", "proposed")
        A.config["status"] = f'transferred {status}'
      A._prev = A0
      A0._nexts = A0._nexts | {A,}
      yield A
