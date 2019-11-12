import inspect

from ..jsonfile import jsonfile

from . import base

import cibblbibbl


dump_kwargs = (
    ("ensure_ascii", False),
    ("indent", "\t"),
    ("sort_keys", True),
)


yesnomap = {
  "y": "yes",
  "Y": "yes",
  "yes": "yes",
  "Yes": "yes",
  "YES": "yes",
  True: "yes",
  "n": "no",
  "N": "no",
  "no": "no",
  "No": "no",
  "NO": "no",
  False: "no",
}

class CachedConfig(base.CustomKeyDescriptorBase):

  def __init__(self, *, force_update_func=None, key=None):
    super().__init__(key=key)
    self.force_update_func = force_update_func
    self.jsonfile_cache = {}

  def __get__(self, instance, owner):
    if instance is None:
      return self
    attrname = f'_{self.key}'
    jf = self.jsonfile(instance)
    calcattrname = f'calculate_{self.key}'
    if not hasattr(instance, attrname):
      if not jf.data and hasattr(instance, calcattrname):
        d = getattr(instance, calcattrname)()
        jf.data.update(d)
      setattr(instance, attrname, jf.data)
    elif (
        self.force_update_func
        and self.force_update_func(instance, jf.data)
    ):
      d = getattr(instance, calcattrname)()
      jf.data = d
      setattr(instance, attrname, jf.data)
    return getattr(instance, attrname)

  def __set__(self, instance, value):
    attrname = f'_{self.key}'
    jf = self.jsonfile(instance)
    jf.data = value
    setattr(instance, attrname, jf.data)

  def __delete__(self, instance):
    attrname = f'_{self.key}'
    self.jsonfile(instance).delete()
    del instance.__dict__[attrname]

  def jsonfile(self, instance):
    if instance in self.jsonfile_cache:
      jf = self.jsonfile_cache[instance]
    else:
      filepath = getattr(instance, f'{self.key}filepath')
      jf = jsonfile(
          filepath,
          default_data = {},
          autosave = True,
          dump_kwargs = dict(dump_kwargs),
      )
      self.jsonfile_cache[instance] = jf
    return jf


class NDField(base.CustomKeyDescriptorBase):

  def __init__(self, *args,
      default = None,
      defaulterrorfstr = 'unreadable attribute',
      f_typecast = None,
      **kwargs
  ):
    super().__init__(*args, **kwargs)
    self._default = default
    self.defaulterrorfstr = defaulterrorfstr
    self.f_typecast = f_typecast
    try:
      self.f_typecast_a = len(
          inspect.getargspec(f_typecast).args
      )
    except TypeError:
      self.f_typecast_a = 1

  def default(self, instance):
    value = self._default
    if inspect.isclass(value) and issubclass(value, Exception):
      s = self.defaulterrorfstr.format(
          descriptor=self, instance=instance
      )
      raise value(s)
    elif inspect.isfunction(value):
      value = value(instance, self)
    return value

  def __get__(self, instance, owner):
    if instance is None:
      return self
    try:
      value = instance.config[self.key]
    except KeyError:
      value = self.default(instance)
    if self.f_typecast:
      if self.f_typecast_a == 2:
        value = self.f_typecast(value, instance)
      elif self.f_typecast_a == 3:
        value = self.f_typecast(value, instance, self)
      else:
        value = self.f_typecast(value)
    return value


class DDField(NDField):

  def __init__(self, *args,
      default = None,
      defaulterrorfstr = 'unreadable attribute',
      default_set_delete = True,
      delete_set_default = False,
      get_f_typecast = None,
      set_f_typecast = None,
      **kwargs
  ):
    super().__init__(*args,
      default = default,
      defaulterrorfstr = defaulterrorfstr,
      f_typecast = get_f_typecast,
      **kwargs)
    self.default_set_delete = default_set_delete
    self.delete_set_default = delete_set_default
    self.set_f_typecast = set_f_typecast
    try:
      self.set_f_typecast_a = len(
          inspect.getargspec(set_f_typecast).args
      )
    except TypeError:
      self.set_f_typecast_a = 1

  def __set__(self, instance, value):
    if self.set_f_typecast:
      if self.set_f_typecast_a == 2:
        value = self.set_f_typecast(value, instance)
      elif self.set_f_typecast_a == 3:
        value = self.set_f_typecast(value, instance, self)
      else:
        value = self.set_f_typecast(value)
    if self.default_set_delete and not self.delete_set_default:
      default = self.default(instance)
      if value == default:
        return self.__delete__(instance)
    instance.config[self.key] = value

  def __delete__(self, instance):
    if self.delete_set_default:
      default = self.default(instance)
      instance.config[self.key] = default
    else:
      del instance.config[self.key]


class MatchupsDirectory:

  def __init__(self, tournamentId_attrname="tournamentId"):
    self.attrname = tournamentId_attrname

  def __get__(self, instance, owner):
    if instance is None:
      return self
    tournamentId = getattr(instance, self.attrname)
    if tournamentId.isdecimal():
      dirname = f'{tournamentId:0>8}'
    else:
      dirname = tournamentId
    directory = (
        cibblbibbl.data.path
        / instance.group_key
        / "matchup"
        / dirname
    )
    return directory



class TimeField(base.TimeFieldProxyDDescriptorBase):
  attrname = "config"


class TournamentField(base.CustomKeyDescriptorBase):

  def __get__(self, instance, owner):
    if instance is None:
      return self
    Id = instance.config.get(self.key)
    if Id is not None:
      return instance.group.tournaments[str(Id)]

  def __set__(self, instance, value):
    if hasattr(value, "Id"):
      value = str(value.Id)
    T = instance.group.tournaments[value]  # test
    instance.config[self.key] = value

  def __delete__(self, instance):
    del instance.config[self.key]


class YearField(base.CustomKeyDescriptorBase):

  def __get__(self, instance, owner):
    if instance is None:
      return self
    group_key = instance.group_key
    year_nr = getattr(instance, "year_nr", ...)
    if year_nr is ...:
      year_nr = int(instance.config[self.key])
    return cibblbibbl.year.Year(group_key, year_nr)

  def __set__(self, instance, value):
    if hasattr(value, "nr"):
      assert value.group is instance.group
      value = value.nr
    else:
      value = int(value)
    instance.config[self.key] = value

  def __delete__(self, instance):
    del instance.config[self.key]

YearNrField = lambda: (DDField(
    key = "year",
    get_f_typecast = int, set_f_typecast = int,
))


def defcfgfp(categorystr):
  def defaultconfigfilepath_of_group(cls, group):
    return (
      cibblbibbl.data.path
      / group.key
      / categorystr
      / f'{cls.clskey()}.json'
    )
  return classmethod(defaultconfigfilepath_of_group)

@classmethod
def defcfg(cls, group):
  jf = jsonfile(
      cls.defaultconfigfilepath_of_group(group),
      default_data = {},
      autosave = True,
      dump_kwargs = dict(dump_kwargs),
  )
  return jf.data


@property
def promptconfig(self):
  jf = jsonfile(
      self.configfilepath,
      default_data = {},
      autosave = True,
      dump_kwargs = dict(dump_kwargs),
  )
  if not jf.data and hasattr(self, "calculate_config"):
    jf.data.update(self.calculate_config())
  return jf.data


def field(key, default=None, doc=None):
  return property(
      getter(key, default=default),
      setter(key),
      deleter(key),
      doc
  )
def getter(key, default=None):
  def fget(self):
    if hasattr(default, "__call__"):
      default = default()
    return self.config.get(key, default)
  return fget
def setter(key):
  def fset(self, value):
    self.config[key] = value
  return fset
def deleter(key):
  def fdel(self):
    del self.config[key]
  return fdel


def yesnofield(key, default=None, doc=None):
  return property(
      yesnogetter(key, default=default),
      yesnosetter(key),
      yesnodeleter(key),
      doc
  )
def yesnogetter(key, default=None):
  def fget(self):
    default_ = default
    if inspect.isfunction(default):
      default_ = default(self)
    return self.config.get(key, yesnomap[default_])
  return fget
def yesnosetter(key):
  def fset(self, value):
    try:
      self.config[key] = yesnomap[value]
    except KeyError:
      raise ValueError(f'invalid yes/no value: {value}')
  return fset
yesnodeleter = deleter
