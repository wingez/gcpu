from gcpu.compiler import throwhelper
from gcpu.compiler import maincontext
from gcpu.compiler.dependecyconstant import DependencyConstant
from gcpu.compiler.memory import MemoryAllocator, MemorySegment

dependencyimportsymbols = '#import '
commentsymbols = '//'
entryfunctionname = 'main'
codefileextension='.g'
outputfileextension='.gb'

"""
Phases:
0: reserved for future use
1: check for identifiers, defs, variables, check size of memorysegments
2: assign correct values into memory

"""
phase = 0

filesIncluded = {}
filesCurrentlyIncluding = []
compileOrder = []


def compile(filename: str):
    global phase
    filesIncluded.clear()
    filesCurrentlyIncluding.clear()
    compileOrder.clear()

    throwhelper.log('starting compilation of file '+filename)
    phase = 0
    # load the file and recursively, all its dependencies
    # filesIncluded and compileOrder is now populated
    basefile = initializefile(filename)

    # perform compilation phase 1
    throwhelper.log('starting compilation phase 1')
    phase = 1
    for file in compileOrder:
        file.compilephase1()
    throwhelper.log('ending compilation phase 1')

    throwhelper.log('starting memory asignments')
    # calculate what memorysegments to include and asign address
    if entryfunctionname not in basefile.functions:
        raise throwhelper.CompileError(
            'no entrypoint found. Add a function named {} in file {}'.format(
                entryfunctionname, basefile.name
            ))
    entryfunction = basefile.functions[entryfunctionname]
    allocator = MemoryAllocator()
    allocator.allocatealldependents(entryfunction)
    allocator.asignaddresses(entryfunction)
    throwhelper.log('ending memory asignments')

    throwhelper.log('starting compilation phase 2')
    # perform phase2 compilation
    phase = 2
    for file in compileOrder:
        file.compilephase2()
    throwhelper.log('ending compilation phase 2')

    throwhelper.log('generating output file')
    filecontent = allocator.generatefilecontent()
    throwhelper.log('wrting output')
    writetofile(filename,filecontent)


def initializefile(filename):
    if filename in filesIncluded:
        return filesIncluded[filename]

    if filename in filesCurrentlyIncluding:
        throwhelper.throw('including: {} would cause a dependency loop'.format(filename))

    throwhelper.log('begins importing of {}'.format(filename))

    filesCurrentlyIncluding.append(filename)

    c = FileCompiler(filename)

    compileOrder.append(c)
    filesIncluded[filename] = c
    filesCurrentlyIncluding.remove(filename)

    throwhelper.log('end importing of {}'.format(filename))

    return c


def readlines(file):
    with open(file+codefileextension, 'r') as f:
        return f.readlines()


def writetofile(filename, content):
    with open(filename+outputfileextension, 'w') as f:
        for index, value in enumerate(content):
            line='{}: {}'.format(index, value)
            if True:
                print(line)
            f.write(line)
            f.write('\n')


def trimcomments(line):
    if commentsymbols in line:
        line = line.partition(commentsymbols)[0]
    return line.strip('\n')


def getglobals():
    return {'msb': msb}



def msb(value):
    result = MemorySegment()
    result.size = 2

    if phase == 1:
        if issubclass(type(value), DependencyConstant):
            result.dependencies.append(value)
    if phase == 2:
        result.content = [value]

    return result


class FileCompiler:

    def __init__(self, name):
        """
        Creates a new filecompiler,load the raw textfile and read  dependencies
        """
        self.name = name
        self.dependencies = []

        self.locals = {}

        self.functions = {}
        self.memsegments = {}
        self.defines = {}

        self.linenumber = 0

        self.lines = [trimcomments(x) for x in readlines(self.name)]
        self.readdependencies()

    def readdependencies(self):
        """
        Read and imports dependencies
        Also removes all line used for imports for furter ease parsing
        """
        for linenumber, line in enumerate(self.lines):
            if line.startswith(dependencyimportsymbols):
                throwhelper.setfile(self.name)
                throwhelper.setlinenumber(linenumber)

                toimport = line.partition(dependencyimportsymbols)[2]
                dependency = initializefile(toimport)

                self.dependencies.append(dependency)
                # remove the content of the line
                self.lines[linenumber] = ''

    def exportidentifiers(self):
        result = {}
        for name, func in self.functions.items():
            if phase != 2 or func.isallocated:
                identifier = self.name + '_' + name
                if phase == 1:
                    result[identifier] = DependencyConstant(func)
                elif phase == 2:
                    result[identifier] = func.address

        for name, value in self.defines.items():
            result[self.name + '_' + name] = value

        return result

    def getidentifiers(self):
        result = getglobals()
        for dependency in self.dependencies:
            self.locals.update(dependency.getidentifiers())

        if phase == 1:
            pass
        elif phase == 2:
            for name, func in self.functions.items():
                result[name] = func.address
            for name, mem in self.memsegments.items():
                result[name] = mem.address
        return result

    def compilephase1(self):
        self.compile()

    def compilephase2(self):
        self.compile()

    def compile(self):
        throwhelper.file = self.name

        self.locals = self.getidentifiers()
        self.setstate(-1)

        # recursevly compile the file
        maincontext.compile(self)

    def addobject(self, name, obj):
        self.defines[name] = obj
        self.locals[name] = obj

    def nextline(self) -> str:

        if self.linenumber >= len(self.lines):
            raise EOFError
        else:
            result = self.lines[self.linenumber]
            self.linenumber += 1
            throwhelper.setlinenumber(self.linenumber)
            if not result:
                return self.nextline()
            else:
                return result

    def setstate(self, state):
        self.linenumber = state
        throwhelper.setlinenumber(self.linenumber)

    def getstate(self):
        return self.linenumber
