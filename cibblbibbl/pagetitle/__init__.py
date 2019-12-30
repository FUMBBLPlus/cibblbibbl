import pathlib
import subprocess

rootpath = pathlib.Path(__file__).parent

def generate(scriptname, text, path):
  scriptfilename = f'{scriptname}.sh'
  scriptfilepath = rootpath / scriptfilename
  o = subprocess.run(
      [str(scriptfilepath), str(text), str(path)]
  )
  return o
