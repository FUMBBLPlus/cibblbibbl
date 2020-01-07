import collections
import os
import pkgutil

import cibblbibbl

__all__ = list(
    module for _, module, _
    in pkgutil.iter_modules([os.path.dirname(__file__)])
)

from . import *


Achievement = mastercls.Achievement


def cleanup(group):
  cleanup_proposed(group)
  cleanup_empty_directories(group)


def cleanup_empty_directories(group):
  root_directory = (
    cibblbibbl.data.path
    / group.key
    / "achievement"
  )
  # list all directory recursively and sort them by path,
  # longest first
  L = sorted(
      root_directory.glob("**"),
      key=lambda p: len(str(p)),
      reverse=True,
  )
  for pdir in L:
    try:
      pdir.rmdir()  # remove directory if empty
    except OSError:
      continue  # catch and continue if non-empty


def cleanup_proposed(group):
  for jf in iter_all_jsonfiles(group):
    status = jf.data.get("status")
    if status == "proposed":
      jf.delete()




def collect(group, rank=None):
  return {
      a
      for cls in sorted(
          Achievement.registry.values(),
          key = lambda c: c.rank
      )
      for a in cls.collect(group)
      if (True if rank is None else (a.rank == rank))
  }


def collectall(rank=None):
  return {
      a
      for group in cibblbibbl.group.Group.__members__.values()
      for a in collect(group, rank=rank)
  }


def iter_all_jsonfiles(group):
  root_directory = (
    cibblbibbl.data.path
    / group.key
    / "achievement"
  )
  dump_kwargs = dict(cibblbibbl.field.config.dump_kwargs)
  for filepath in root_directory.glob("**/*.json"):
    jf = cibblbibbl.data.jsonfile(
        filepath,
        autosave = True,
        dump_kwargs = dump_kwargs,
    )
    yield jf


del pkgutil
del os
