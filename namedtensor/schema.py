from collections import OrderedDict
from .utils import make_tuple


class _Schema:
    "Dimension names and order"

    def __init__(self, names, mask=0):
        self._names = make_tuple(names)
        s = set()
        for n in self._names:
            assert n is not None
            assert n.isalnum(), "dim name %s must be alphanumeric" % n
            assert n not in s, (
                "Tensor must have unique dims, dim '%s' is non-unique" % n
            )
            s.add(n)

        self._masked = mask
        self._axes = OrderedDict(((d, i) for i, d in enumerate(self._names)))

    def _to_einops(self):
        return " ".join(self._names)

    def ordered_dict(self, size):
        return OrderedDict(((d, size[i]) for i, d in self.enum_masked()))

    @staticmethod
    def build(names, mask):
        if isinstance(names, _Schema):
            return _Schema(names._names, mask)
        names = make_tuple(names)
        return _Schema(names, mask)

    def get(self, name):
        if name not in self._axes:
            raise RuntimeError(
                "Dimension %s does not exist. Available dimensions are %s"
                % (name, self._names)
            )
        i = self._axes[name]
        if i < self._masked:
            raise RuntimeError("Dimension %s is masked" % (name,))
        return i

    def drop(self, names):
        names = make_tuple(names)
        return _Schema(
            [n for n in self._names if n not in names], self._masked
        )

    def update(self, update):
        return _Schema([update.get(n, n) for n in self._names], self._masked)

    def enum_masked(self):
        return enumerate(self._names[self._masked :], self._masked)

    def enum_all(self):
        return enumerate(self._names)
