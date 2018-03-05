from . import context
from gcpu.compiler.pointer import Pointer


class Struct:
    def __init__(self, name, size=0, offset=0, nodes=None):
        self.name, self.size, self.offset, self.nodes = name, size, offset, nodes or {}

    def appendstruct(self, name, struct, count=1):
        if count != 1:
            copy = StructArray(name, 0, self.size, struct, count)
        else:
            copy = struct.copyandoffset(self.size)
        self.size += copy.size
        self.nodes[name] = copy

    def copyandoffset(self, offset):
        return Struct(self.name, self.size, self.offset + offset,
                      {key: s.copyandoffset(offset) for key, s in self.nodes.items()})

    def createpointer(self, baseobject):
        ptr = Pointer(baseobject, self.offset)
        for name, struct in self.nodes.items():
            setattr(ptr, name, struct.createpointer(baseobject))
        return ptr


class StructArray(Struct):

    def __init__(self, name, size, offset, arraystruct, arraylength):
        size = arraystruct.size * arraylength
        super().__init__(name, size, offset)
        self.arraystruct, self.arraylenght = arraystruct, arraylength

        self.array = []
        for i in range(arraylength):
            self.array.append(arraystruct.copyandoffset(self.offset + arraystruct.size * i))

    def copyandoffset(self, offset):
        return StructArray(self.name, 0, self.offset + offset, self.arraystruct, self.arraylenght)

    def createpointer(self, baseobject):
        return ArrayPointer(baseobject, self.offset, [p.createpointer(baseobject) for p in self.array])


class ArrayPointer(Pointer):
    def __init__(self, memorysegment, offset, array):
        super(ArrayPointer, self).__init__(memorysegment, offset)
        self.array = array
        self.length = len(array)

    def __getitem__(self, item):
        if type(item) is not int:
            raise ValueError('indexer is not int')
        if item not in range(1, self.length):
            raise ValueError('indexer not in range')

        return self.array[item]


defaultstructs = {
    'byte': Struct('', 1),
    'dbyte': Struct(' ', 2),
    'ptr': Struct('', 2),
}


class StructContext(context.Context):
    starttext = '#struct '
    endtext = 'end'

    availablecontexts = []

    def __init__(self, parent, name):
        super().__init__(parent)
        self.scope.update(defaultstructs)
        self.struct = Struct(name)
        self.name = name

    def parseline(self, line: str):

        if line.endswith(']'):
            line, s = line.split('[')
            s = s.rstrip(']')
            count = self.scope.evalalutate(s)
        else:
            count = 1

        tmp = line.split()
        name = tmp[0]
        typeraw = tmp[1]
        structtype = self.scope.get(typeraw, None)
        if not structtype:
            raise ValueError('struct {} not found'.format(typeraw))
        if not isinstance(structtype, Struct):
            raise ValueError('not struct type'.format(typeraw))

        self.addtostruct(name, structtype, count)

    def addtostruct(self, name, structtype, count=1):
        self.struct.appendstruct(name, structtype, count)

    def oncontextend(self, context, result):
        if context is StructContext:
            name = result[0]
            structtype = result[1]
            self.addtostruct(name, structtype)
        else:
            super().oncontextend(context, result)

    def onending(self):
        return self.name, self.struct


StructContext.availablecontexts.append(StructContext)
