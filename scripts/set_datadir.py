#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib
import sys

import cibblbibbl

if __name__ == "__main__":
  usage = "usage: set_datadir.py <directory>"
  if len(sys.argv) > 1:
    datadir = pathlib.Path(sys.argv[1])
    if datadir.is_dir():
      abspath = datadir.resolve(strict=True)
      key = "cibblbibbl-data.path"
      cibblbibbl.settings[key] = abspath.as_posix()
      sys.exit()
  print(usage)

