from gcpu.compiler.memory import MemorySegment
from gcpu.compiler.defstatement import defstatement
import gcpu.compiler.throwhelper as throwhelper
from gcpu.compiler.pointer import Pointer

from typing import Tuple

memsymbols = '#mem '


def ismemstatement(statement: str):
    return statement.startswith(memsymbols)


def memstatement(statement: str, vars: dict) -> Tuple[str, MemorySegment]:
    statement = statement.partition(memsymbols)[2]
    vars.update({'msb': msb})
    id, memsegment = defstatement(statement, vars, trim=False)

    if type(memsegment) is not MemorySegment:
        throwhelper.throw('result not memorysegment')

    memsegment.id = id

    return id, memsegment


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
