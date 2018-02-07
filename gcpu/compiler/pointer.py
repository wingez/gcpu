from gcpu.compiler.memory import MemorySegment


class Pointer:
    def __init__(self, address: int = 0, dependecies=()):
        self.address = address
        self.dependencies = list(dependecies)

    def __add__(self, other):
        if type(other) is int:
            return Pointer(self.address + other, self.dependencies)

        raise NotImplementedError

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if type(other) is int:
            return Pointer(self.address - other, self.dependencies)

        raise NotImplementedError

    def __int__(self):
        return self.address


def ptr(value):
    if type(value) is int:
        return Pointer(value)
    elif issubclass(type(value),MemorySegment):
        return Pointer(value.address, [value])
    else:
        raise ValueError('value is not int or memorysegment')
