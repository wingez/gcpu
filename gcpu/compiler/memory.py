from typing import List
import gcpu.compiler.throwhelper as throwhelper


class MemorySegment:

    def __init__(self, id=''):
        self.isallocated = False
        self.address = 0
        self.size = 0
        self.content = []
        self.dependencies = []
        self.id = id

    def getasignmessage(self) -> str:
        return self.id


class MemoryAllocator:

    def __init__(self, maxsize=2 ** 16):
        self.allocated = set()
        self.currentaddress = 0
        self.maxsize = maxsize

    def allocatealldependents(self, rootobject: MemorySegment, allocating=set()):

        if rootobject not in self.allocated:
            rootobject.isallocated = True

            self.allocated.add(rootobject)

        if rootobject in allocating:
            return

        allocating.add(rootobject)
        for dependency in rootobject.dependencies:
            self.allocatealldependents(dependency)
        allocating.remove(rootobject)

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
            name = segment.getasignmessage()
            if not name:
                name = 'unknown'
            throwhelper.log('asignning {}, size:{} at address {}'.format(name, segment.size, self.currentaddress))

            segment.address = self.currentaddress
            self.currentaddress += segment.size

    def generatefilecontent(self):
        result = [0] * self.currentaddress

        for memsegment in self.allocated:
            for index, value in enumerate(memsegment.content):
                result[memsegment.address + index] = value
        return result

    def getusedmemory(self):
        return self.currentaddress
