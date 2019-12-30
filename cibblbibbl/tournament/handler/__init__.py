import os
import pkgutil

import cibblbibbl

__all__ = list(
    module for _, module, _
    in pkgutil.iter_modules([os.path.dirname(__file__)])
)

def get_handler(group_key, Id):
  handler = globals()[get_handlername(group_key, Id)]
  return handler


def get_handlername(group_key, Id):
  if str(Id).isdecimal():
    filename = f'{Id:0>8}'
  else:
    filename = str(Id)
  handlerfile = f'{group_key}/tournament/handler/{filename}'
  p = cibblbibbl.data.path / handlerfile
  p_exists = (p.is_file() and p.stat().st_size)
  if p_exists:
    handlername = cibblbibbl.data.jsonfile(p).data
  else:
    handlername = "default"
  return handlername


from . import *

del pkgutil
del os
