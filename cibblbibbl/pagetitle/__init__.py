import os
import pathlib
import subprocess

rootpath = pathlib.Path(__file__).parent

def generate(scriptname, text, path):
  if os.name == "nt":
    scriptsuffix = ".bat"
  else:
    scriptsuffix = ".sh"
  scriptfilename = f'{scriptname}{scriptsuffix}'
  scriptfilepath = rootpath / scriptfilename
  o = subprocess.run(
      [str(scriptfilepath), str(text), str(path)]
  )
  return o
