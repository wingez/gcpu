from itertools import chain


class FlagState:
    def __init__(self):
        self.musthave = []
        self.mustnothave = []

    def __add__(self, other):
        if not isinstance(other, FlagState):
            raise NotImplementedError()
        r = FlagState()
        r.musthave = self.musthave + other.musthave
        r.mustnothave = self.mustnothave + other.mustnothave
        return r

    def __neg__(self):
        r = FlagState()
        r.musthave = self.mustnothave
        r.mustnothave = self.musthave
        return r

    def compatible(self, other):
        return all([x not in other.mustnothave for x in self.musthave]) \
               and all([x not in other.musthave for x in self.mustnothave])

    @property
    def priority(self):
        return len(self.musthave) + len(self.mustnothave)

    def __str__(self):
        items = [x.name for x in self.musthave]
        items += ['~{}'.format(x.name) for x in self.mustnothave]
        return ' '.join(items)

    def encode(self):
        result = 0
        for f in self.musthave:
            result |= 1 << f.index
        return result


class Flag:
    def __init__(self, name, index):
        super().__init__()
        self.name, self.index = name, index

    def createstate(self):
        result = FlagState()
        result.musthave.append(self)
        return result


flag_empty = FlagState()
