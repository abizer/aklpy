from collections import OrderedDict
from typing import TypeVar

T = TypeVar("T")


# borrowed from https://gist.github.com/davesteele/44793cd0348f59f8fadd49d7799bd306
class LRUDict[K, V](OrderedDict):
    def __init__(self, *args, max_size: int = 1024, **kwargs):
        assert max_size > 0
        self.max_size = max_size

        super().__init__(*args, **kwargs)

    def __setitem__(self, key: K, value: V) -> None:
        super().__setitem__(key, value)
        super().move_to_end(key)

        while len(self) > self.max_size:  # pragma: no cover
            oldkey = next(iter(self))
            super().__delitem__(oldkey)

    def __getitem__(self, key: K) -> V:
        val = super().__getitem__(key)
        super().move_to_end(key)

        return val
