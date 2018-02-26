from .context import Context
from .defcontext import DefContext
from gcpu.compiler.memory import MemorySegment
from gcpu.compiler.pointer import Pointer
from gcpu.compiler import throwhelper


class MemContext(Context):
    starttext = '#mem '

    def __init__(self, parent, statement):
        super().__init__(parent)
        self.scope = parent.scope.copy()
        self.scope.update({'msb': msb})

        name, result = self.docontext(DefContext, statement)
        if type(result) is not MemorySegment:
            throwhelper.throw('result is not memorysegment')
        result.id = name
        self.end(name, result)


def msb(value):
    result = MemorySegment()
    result.size = 1

    if type(value) is Pointer:
        result.dependencies.extend(value.dependencies)
        result.content = [value.address]
    elif type(value) is int:
        result.content = [value]
    else:
        raise NotImplementedError

    return result
