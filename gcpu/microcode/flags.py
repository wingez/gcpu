class FlagBase:
    def __init__(self):
        self.musthave = []
        self.mustnothave = []

    def __add__(self, other):
        if not isinstance(other,FlagBase):
            raise NotImplementedError()
        r = FlagBase()
        r.musthave = self.musthave + other.musthave
        r.mustnothave = self.mustnothave + other.mustnothave
        return r

    def __neg__(self):
        r = FlagBase()
        r.musthave = self.mustnothave
        r.mustnothave = self.musthave
        return r

    def compatible(self, other):
        return all([x not in other.mustnothave for x in self.musthave]) \
               and all([x not in other.musthave for x in self.mustnothave])

    @property
    def priority(self):
        return len(self.musthave) + len(self.mustnothave)


class Flag:
    def __init__(self, name, index):
        super().__init__()
        self.name, self.index = name, index


empty = FlagBase()


def createflag(name, index):
    f = Flag(name, index)

    result = FlagBase()
    result.musthave.append(f)
    return result


def flagstoint(flagiterable):
    result = 0
    for flag in flagiterable:
        for f in flag.musthave:
            result |= 1 << f.index
    return result
