import cibblbibbl


from . import base


class MatchLink:

  def __init__(self):
    self.registry = {}

  def __get__(self, instance, owner):
    if instance is None:
      return self
    if instance not in self.registry:
      d = instance.schedulerecord
      matchId = d.get("result", {}).get("id")
      if matchId:
        Ma = cibblbibbl.match.Match(matchId)
        Ma.matchup = instance  # backlink
        self.registry[instance] = Ma
      else:
        self.registry[instance] = None
    return self.registry[instance]

  def __set__(self, instance, value):
    if value is not None and not hasattr(value, "Id"):
      value = cibblbibbl.match.Match(int(value))
    self.registry[instance] = value

  def __delete__(self, instance):
    Ma = self.registry[instance]
    del self.registry[instance]
    if Ma:
      del Ma.matchup


class ScheduleRecordTimeFieldGetter(
    base.TimeFieldProxyNDescriptorBase
):
  attrname = "schedulerecord"


@property
def sr_highlightedteam_getter(self):
  teamId = self.schedulerecord.get("result", {}).get("winner")
  if teamId:
    return cibblbibbl.team.Team(teamId)


@property
def sr_position_getter(self):
  return self.schedulerecord.get("position", 0)
