from gcpu.compiler.memory import MemorySegment


class Pointer:
    def __init__(self, pointsto: MemorySegment, offset=0):
        self.pointsto = pointsto
        self.offset = offset

    def __add__(self, other):
        if type(other) is int:
            return Pointer(self.pointsto, self.offset + other)

        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if type(other) is int:
            return Pointer(self.pointsto, self.offset - other)

        return NotImplemented

    @property
    def address(self):
        return self.pointsto.address + self.offset

    def __str__(self):
        return str(self.address)

    def __int__(self):
        return self.address
