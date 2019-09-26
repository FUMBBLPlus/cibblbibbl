import collections
import json
import pathlib

import cibblbibbl

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


def yesnogetter(key, default=None):
  def fget(self):
    return self.config.get(key, yesnomap[default])
  return fget

yesnodeleter = deleter

def yesnosetter(key):
  def fset(self, value):
    try:
      self.config[key] = yesnomap[value]
    except KeyError:
      raise ValueError(f'invalid yes/no value: {value}')
  return fset

def yesnofield(key, default=None, doc=None):
  return property(
      yesnogetter(key, default=default),
      yesnosetter(key),
      yesnodeleter(key),
      doc
  )
