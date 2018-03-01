from . import context
from .structcontext import Struct, StructContext
from gcpu.compiler import compiler, memory, pointer


class InstanceContext(context.Context):
    starttext = '#instance '

    def __init__(self, parent, statement):
        super().__init__(parent)
        arg = statement.split()

        structtype = None
        name = ''
        structname = ''

        if len(arg) == 2:
            """
                #instance <name> <structtype>
            """

            name, structname = arg

            structtype = self.scope.get(structname, None)
            if not isinstance(structtype, Struct):
                raise ValueError('no structtype')
        else:
            """
                #instance <name>
                    structdef...
                    ...
                    ...
                end
            """
            name, structtype = self.docontext(StructContext, arg[0])

        memsegment = None
        if compiler.phase == 1:
            memsegment = memory.MemorySegment('{}, struct = {}'.format(name, structname))
            memsegment.size = structtype.size
            self.compiler.components[memory.MemorySegment, name] = memsegment
        elif compiler.phase == 2:
            memsegment = self.compiler.components[memory.MemorySegment, name]

        self.end(name, pointertreefromstruct(structtype, memsegment))


def pointertreefromstruct(struct, memsegment):
    result = PointerTree(memsegment, struct.offset)
    for k, v in struct.nodes.items():
        setattr(result, k, pointertreefromstruct(v, memsegment))
    return result


class PointerTree(pointer.Pointer):
    def __init__(self, baseobj, offset):
        super().__init__(baseobj, offset)
