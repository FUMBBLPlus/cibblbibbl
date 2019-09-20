import bisect
import datetime


def combined(*schedules):
  fmt = "%Y-%m-%d %H:%M:%S"
  L = []
  for S in schedules:
    for P in S:
      DT = datetime.datetime.strptime(P["modified"], fmt)
      bisect.insort(L, (DT, P))
  return [t[1] for t in L]


