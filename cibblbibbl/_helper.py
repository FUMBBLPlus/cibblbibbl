import json
import pathlib
import re

import cibblbibbl

EXTRA_STRIP = " ⠀"
IGNORE = "\xad"


def norm_name(s):
  s = s.strip(EXTRA_STRIP)
  s = re.sub(f'[{IGNORE}]', "", s)
  return s


def get_api(ID, dir_path, api_func, *, reload=False):
  filename = f'{ID:0>8}.json'
  data_path = cibblbibbl.settings["cibblbibbl-data.path"]
  p = pathlib.Path(data_path) / dir_path / filename
  if not reload and p.is_file() and p.stat().st_size:
    with p.open(encoding="utf8") as f:
      o = json.load(f)
  else:
    o = api_func(ID)
    if p.parent.is_dir():
      with p.open("w", encoding="utf8") as f:
        json.dump(
          o,
          f,
          ensure_ascii = False,
          indent = "\t",
          sort_keys = True,
        )
  return o
