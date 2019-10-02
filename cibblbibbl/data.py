import pathlib

try:
  from .jsonfile import jsonfile
except ImportError:
  from jsonfile import jsonfile



file = jsonfile(
    pathlib.Path.home()
    / ".fumbblplus/cibblbibbl/datapath.json",
    autosave=True
)



def getpath():
  value = file.data
  if value is ...:
    raise ValueError("data path is unset; run data.py directly")
  return pathlib.Path(value)



def setpath(value):
  p = pathlib.Path(value)
  if not p.is_dir():
    raise ValueError("not a directory")
  else:
    file.data = str(p)




if __name__ != "__main__":

  path = getpath()
  if not path.is_dir():
    raise ImportError(
        "data path is unset; run data.py directly"
  )

else:

  import sys
  if len(sys.argv) < 2:
    print("To set the path of cibblbibbl-data, command:")
    print("data.py <directory>")
  else:
    path = sys.argv[1]
    try:
      setpath(sys.argv[1])
    except ValueError:
      print("ERROR! not a directory")
