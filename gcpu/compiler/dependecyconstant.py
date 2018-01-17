import gcpu.compiler.throwhelper as throwhelper
from gcpu.compiler.memory import MemorySegment
from gcpu.compiler import compiler


class DependencyConstant:
    # dependencies should be a list of MemorySegments
    def __init__(self, dependencies):
        if issubclass(type(dependencies), MemorySegment):
            self.dependencies = [dependencies]
        else:
            self.dependencies = dependencies

    def __add__(self, other):
        if compiler.phase != 1:
            throwhelper.throw('operation not allowed in phase 2')

        if type(other) is DependencyConstant:
            return DependencyConstant(self.dependencies + other.dependecies)
        elif type(other) is int:
            return self
        else:
            throwhelper.throw('operation not allowed: Memsegment and {}'.format(other.__name__))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        result = self.__add__(other)
        throwhelper.warn('Use of MemSegment - n, use with caution')
        return result

    def __rsub__(self, other):
        throwhelper.throw('operation not allowed: {} - MemSegment'.format(other.type.__name__))
