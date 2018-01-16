from typing import List
import gcpu.compiler.throwhelper as throwhelper


class MemorySegment:

    def __init__(self):
        self.isallocated = False
        self.address = 0
        self.size = 0
        self.content = []
        self.dependencies = []

    pass


class MemoryAllocator:

    def __init__(self, maxsize=2 ** 16):
        self.allocated = set()
        self.currentaddress = 0
        self.maxsize = maxsize
        self.size = 0

    def allocate(self, *memsegments):
        for m in memsegments:
            if m not in self.allocated:
                m.isallocated = True
                self.allocated.add(m)

    def allocatealldependents(self, rootobject: MemorySegment):

        self.allocate(rootobject)
        for dependency in rootobject.dependencies:
            self.allocatealldependents(dependency)

    def asignaddresses(self, zerosegment=None):

        if zerosegment:
            self.asignsegment(zerosegment)

        for memsegment in self.allocated:
            if memsegment is not zerosegment:
                self.asignsegment(memsegment)

    def asignsegment(self, segment: MemorySegment):
        if self.currentaddress + segment.size >= self.maxsize:
            throwhelper.throw('not enough memoey avaliable')
        else:
            segment.address = self.currentaddress
            self.currentaddress += segment.size

    def generatefilecontent(self):
        result = [0] * self.currentaddress

        for memsegment in self.allocated:
            for index, value in enumerate(memsegment.content):
                result[memsegment.address + index] = value
        return result
