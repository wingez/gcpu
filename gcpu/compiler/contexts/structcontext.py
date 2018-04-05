from . import context
from gcpu.compiler import pointer, compiler, memory
from collections import OrderedDict, namedtuple


def assertstructroot(struct):
    if not isinstance(struct, StructRoot):
        raise ValueError('basestruct must be of type {}'.format(StructRoot.__name__))


class StructBase:
    def __init__(self, offset):
        self._size = 0
        self._offset = offset


class StructNode(StructBase):
    def __init__(self, basestruct, offset):
        super().__init__(offset)
        assertstructroot(basestruct)

        self._basestruct = basestruct

    def __getattr__(self, item):
        return self._basestruct.createnodeoffset(item, self._offset)


class StructArray(StructBase):
    def __init__(self, basestruct, length, offset):
        super().__init__(offset)
        assertstructroot(basestruct)

        self._basestruct = basestruct
        self._length = length
        self._size = basestruct._size * length

    def __getitem__(self, item):
        if type(item) is not int:
            raise ValueError('Index must be int')
        if item not in range(self._length):
            raise ValueError('Index out of range')
        offset = self._offset + self._length * self._basestruct._size
        return StructNode(self._basestruct, offset)


class StructRoot(StructNode):
    NodeInfo = namedtuple('NodeInfo', ['struct', 'offset', 'count'])

    def __init__(self, name):
        super().__init__(self, 0)

        self._name = name
        self._nodes = OrderedDict()
        self._locked = False
        self._defaultdata = None

    def lock(self):
        self._locked = True
        self._defaultdata = [0] * self._size

    def addnode(self, name: str, basestruct, count=1):

        assertstructroot(basestruct)

        if self._locked:
            raise ValueError('Struct is locked')
        if not basestruct._locked:
            raise ValueError('Added basestruct must be locked')

        if name in self._nodes:
            raise ValueError('Node {} is already assigned'.format(name))
        if name.startswith('_'):
            raise ValueError('Name must not start with underscore _')
        if count < 1:
            raise ValueError('Arraylength cannot be less than 1')

        self._nodes[name] = self.NodeInfo(basestruct, self._size, count)
        self._size += basestruct._size * count

    def createnodeoffset(self, name, offset):
        nodeinfo = self._nodes.get(name, None)
        if not nodeinfo:
            raise ValueError('No substruct named {}'.format(name))

        if nodeinfo.length == 1:
            return StructNode(nodeinfo.basestruct, nodeinfo.offset + offset)
        else:
            return StructArray(nodeinfo.struct, nodeinfo.length, nodeinfo.offset + offset)

    def createpointeroffset(self, name, memsegment, offset):
        nodeinfo = self._nodes.get(name, None)
        if not nodeinfo:
            raise ValueError('No substruct named {}'.format(name))

        if nodeinfo.count == 1:
            return NodePointer(memsegment, offset + nodeinfo.offset, nodeinfo.struct)
        else:
            return ArrayPointer(memsegment, offset + nodeinfo.offset, nodeinfo.struct, nodeinfo.count)

    def createpointer(self, memsegment):
        return NodePointer(memsegment, 0, self)

    def __str__(self):
        return '{}, size = {}'.format(self._name, self._size)


class NodePointer(pointer.Pointer):
    def __init__(self, memsegment, offset, basestruct):
        super().__init__(memsegment, offset)
        assertstructroot(basestruct)

        self.basestruct = basestruct

    def __getattr__(self, item):
        return self.basestruct.createpointeroffset(item, self.pointsto, self.offset)


class ArrayPointer(pointer.Pointer):
    def __init__(self, memsegment, offset, basestruct, count):
        super().__init__(memsegment, offset)
        assertstructroot(basestruct)

        self.basestruct, self.count = basestruct, count

    def __getitem__(self, item):
        if type(item) is not int:
            raise ValueError('Index must be int')
        if item not in range(self.count):
            raise ValueError('Index out of range')
        offset = self.offset + item * self.basestruct._size
        return NodePointer(self.pointsto, offset, self.basestruct)


class Byte(StructRoot):
    def __init__(self):
        super().__init__('Byte')
        self._size = 1
        self.lock()


class DByte(StructRoot):
    def __init__(self):
        super().__init__('DByte')
        self._size = 2
        self.lock()


class Ptr(StructRoot):
    def __init__(self):
        super().__init__('Ptr')
        self._size = 2
        self.lock()


defaultstructs = {
    'byte': Byte(),
    'dbyte': DByte(),
    'ptr': Ptr(),
}


class StructParser:

    def __init__(self, name, context):

        self.context = context
        if compiler.phase == 1:
            self.struct = StructRoot(name)
            self.context.compiler.components[StructRoot, name] = self.struct
        elif compiler.phase == 2:
            self.struct = self.context.compiler.components[StructRoot, name]

    def parseline(self, line: str):
        """
            The following statements are valid, Parenthesis marks optional staments

            <name> : <type>([<arraylength>])(=<initvalue>)
        """
        # line = "<name> : <type>([<arraylength>]) (=<initvalue>)"

        initvalueraw = None
        arraylength = 1
        arraylengthraw = None

        name, line = [l.strip() for l in line.split(':')]
        # name = "<name>"
        # line = "<type>([<arraylength>])(=<initvalue>)]"

        if '=' in line:
            line, initvalueraw = [l.strip() for l in line.split('=')]
        # initvalueraw= "<initvalue>"
        # line = "<type>([arraylength])"

        if line.endswith(']'):
            line, s = line.split('[')
            arraylengthraw = s.rstrip(']')
            # line= "<type>"

        typeraw = line

        if compiler.phase == 1:
            structtype = self.context.scope[typeraw]

            if arraylengthraw:
                arraylength = self.context.scope.evaluate(arraylengthraw)
            self.add(name, structtype, arraylength)

        elif compiler.phase == 2:
            if initvalueraw:
                initvalue = self.context.scope.evaluate(initvalueraw)

    def add(self, name, structtype, arraylength=1):
        self.struct.addnode(name, structtype, arraylength)

    def finish(self):
        self.struct.lock()
        return self.struct


class StructContext(context.Context):
    starttext = '#struct '
    endtext = 'end'

    availablecontexts = []

    def __init__(self, parent, name):
        super().__init__(parent)
        self.name = name
        self.scope.update(defaultstructs)
        self.parser = StructParser(name, self)

    def parseline(self, line: str):
        self.parser.parseline(line)

    def oncontextend(self, context, result):
        if context is StructContext:
            self.parser.add(*result)
        else:
            super().oncontextend(context, result)

    def onending(self):
        return self.name, self.parser.finish()


StructContext.availablecontexts.append(StructContext)


class InstanceContext(context.Context):
    starttext = '#instance '

    def __init__(self, parent, statement: str):
        super().__init__(parent)
        self.scope.update(defaultstructs)

        memsegment = None

        if ':' in statement:
            # #instance <name>:<type> etc...
            structid='autotruct_{}_{}'.format(self.compiler.name,self.compiler.linenumber)
            parser = StructParser(structid, self)
            parser.parseline(statement)
            struct = parser.finish()

            if not len(struct._nodes) == 1:
                raise NotImplementedError
            # Get first node which should be the name of the struct
            name = next(iter(struct._nodes.keys()))

            if compiler.phase == 1:
                memsegment = memory.MemorySegment('{}, struct = {}'.format(name, struct._name))
                memsegment.size = struct._size
                self.compiler.components[memory.MemorySegment, name] = memsegment
            elif compiler.phase == 2:
                memsegment = self.compiler.components[memory.MemorySegment, name]

            self.end(name, struct.createpointer(memsegment).__getattr__(name))

        else:
            """
                #instance <name>
                    structdef...
                    ...
                    ...
                end
            """
            name, struct = self.docontext(StructContext, statement)

            if compiler.phase == 1:
                memsegment = memory.MemorySegment('{}, struct = {}'.format(name, struct._name))
                memsegment.size = struct._size
                self.compiler.components[memory.MemorySegment, name] = memsegment
            elif compiler.phase == 2:
                memsegment = self.compiler.components[memory.MemorySegment, name]

            self.end(name, struct.createpointer(memsegment))
