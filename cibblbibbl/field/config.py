from ..jsonfile import jsonfile

from . import base


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


@property
def cachedconfig(self):
  if not hasattr(self, "_config"):
    jf = jsonfile(
        self.configfilepath,
        default_data = {},
        autosave = True,
        dump_kwargs = dict(dump_kwargs),
    )
    if not jf.data and hasattr(self, "calculate_config"):
      jf.data.update(self.calculate_config())
    self._config = jf.data
  return self._config


def field(key, default=None, doc=None):
  return property(
      getter(key, default=default),
      setter(key),
      deleter(key),
      doc
  )
def getter(key, default=None):
  def fget(self):
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


class TimeField(base.TimeFieldProxyDDescriptorBase):
  attrname = "config"


def yesnofield(key, default=None, doc=None):
  return property(
      yesnogetter(key, default=default),
      yesnosetter(key),
      yesnodeleter(key),
      doc
  )
def yesnogetter(key, default=None):
  def fget(self):
    return self.config.get(key, yesnomap[default])
  return fget
def yesnosetter(key):
  def fset(self, value):
    try:
      self.config[key] = yesnomap[value]
    except KeyError:
      raise ValueError(f'invalid yes/no value: {value}')
  return fset
yesnodeleter = deleter



