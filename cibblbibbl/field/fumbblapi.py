import cibblbibbl


class CachedFUMBBLAPIGetField:

  dump_kwargs = (
      ("ensure_ascii", False),
      ("indent", "\t"),
      ("sort_keys", True),
  )

  def __init__(self, api_func,
      dir_path=None,
      api_args_func=None,
      id_func=None,
  ):
    self.dir_path = dir_path
    self.api_func = api_func
    self.api_args_func = (
        api_args_func or (lambda inst: (inst.Id,))
    )
    self.id_func = id_func or (lambda inst: inst.Id)
    if dir_path:
      self.cache = {}

  def __get__(self, instance, owner):
    if instance is None:
      return self
    elif self.dir_path:
      o = self.cache.get(instance, ...)
      if o is ...:
        filename = f'{self.id_func(instance):0>8}.json'
        p = cibblbibbl.data.path / self.dir_path / filename
        jf = cibblbibbl.data.jsonfile(p)
        if not p.is_file() or not p.stat().st_size:
          jf.dump_kwargs = self.dump_kwargs
          o = self.api_func(*self.api_args_func(instance))
          jf.data = o
          jf.save()
        else:
          o = jf._data
        self.cache[instance] = o
    else:
      o = self.api_func(*self.api_args_func(instance))
    return o

  def __delete__(self, instance):
    if self.dir_path:
      filename = f'{self.id_func(instance):0>8}.json'
      p = cibblbibbl.data.path / self.dir_path / filename
      p.unlink()  # delete file
