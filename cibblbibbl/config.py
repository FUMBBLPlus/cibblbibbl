import collections
import json
import pathlib

import cibblbibbl

def getter(key, default=None):
  def fget(self):
    return self.config.get(key, default)
  return fget

def deleter(key):
  def fdel(self):
    del self.config[key]
  return fdel

def setter(key):
  def fset(self, value):
    self.config[key] = value
  return fset


def field(key, default=None, doc=None):
  return property(
      getter(key, default=default),
      setter(key),
      deleter(key),
      doc
  )

