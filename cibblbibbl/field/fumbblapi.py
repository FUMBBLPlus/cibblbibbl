import cibblbibbl

from . import base


class CachedFUMBBLAPIGetField(base.CustomKeyDescriptorBase):

  dump_kwargs = (
      ("ensure_ascii", False),
      ("indent", "\t"),
      ("sort_keys", True),
  )

  def __init__(self, api_func,
      dir_path=None,
      api_args_func=None,
      id_func=None,
      force_update_func=None,
      key=None,
      **kwargs,
  ):
    super().__init__(key=key)
    self.dir_path = dir_path
    self.api_func = api_func
    self.api_args_func = (
        api_args_func or (lambda inst: (inst.Id,))
    )
    self.id_func = id_func or (lambda inst: inst.Id)
    if dir_path:
      self.cache = {}
    self.force_update_func = force_update_func
    self.kwargs = kwargs

  def __get__(self, instance, owner):
    if instance is None:
      return self
    elif self.dir_path:
      o = self.cache.get(instance, ...)
      if o is ...:
        jf = self.jf(instance)
        p = jf.filepath
        if not p.is_file() or not p.stat().st_size:
          o = self.update(instance, jf)
        else:
          o = jf._data
          if self.force_update_func:
            if self.force_update_func(instance, o):
              o = self.update(instance, jf)
        self.cache[instance] = o
    else:
      o = self.update(instance)
    return o

  def __delete__(self, instance):
    if self.dir_path:
      filename = f'{self.id_func(instance):0>8}.json'
      p = cibblbibbl.data.path / self.dir_path / filename
      p.unlink()  # delete file
    if self.cache.get(instance, ...) != ...:
      del self.cache[instance]

  def jf(self, instance):
    if self.dir_path:
      filename = f'{self.id_func(instance):0>8}.json'
      p = cibblbibbl.data.path / self.dir_path / filename
      jf = cibblbibbl.data.jsonfile(p)
      return jf

  def update(self, instance, jf=None):
    #print(f'{type(instance)}  {instance._KEY} {self.api_func}')
    o = self.api_func(
      *self.api_args_func(instance),
      **self.kwargs,
    )
    if jf:
      jf.dump_kwargs = dict(self.dump_kwargs)
      jf.data = o
      jf.save()
    return o
