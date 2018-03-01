from . import context
import copy


class Struct:
    def __init__(self, size=0, offset=0):
        self.nodes = {}
        self.size = size
        self.offset = offset

    def appendstruct(self, name, structtype):
        copystruct = copy.deepcopy(structtype)
        copystruct.addoffsetrecursively(self.size)
        self.size += copystruct.size
        self.nodes[name] = copystruct

    def addoffsetrecursively(self, offset):
        self.offset += offset
        for n in self.nodes.values():
            n.addoffsetrecursively(offset)


defaultstructs = {
    'byte': Struct(1),
    'dbyte': Struct(2),
    'ptr': Struct(2),
}


class StructContext(context.Context):
    starttext = '#struct '
    endtext = 'end'

    availablecontexts = []

    def __init__(self, parent, name):
        super().__init__(parent)
        self.scope.update(defaultstructs)
        self.struct = Struct()
        self.name = name

    def parseline(self, line):
        tmp = line.split()
        name = tmp[0]
        typeraw = tmp[1]
        structtype = self.scope.get(typeraw, None)
        if not structtype:
            raise ValueError('struct {} not found'.format(typeraw))
        if not isinstance(structtype, Struct):
            raise ValueError('not struct type'.format(typeraw))

        self.addtostruct(name, structtype)

    def addtostruct(self, name, structtype):
        self.struct.appendstruct(name, structtype)

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
