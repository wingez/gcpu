from gcpu.compiler import throwhelper
# from gcpu.compiler import maincontext
from gcpu.compiler.contexts.maincontext import MainContext
from gcpu.compiler.memory import MemoryAllocator, MemorySegment
import os

dependencyimportsymbols = '#import '
commentsymbols = '//'
entryfunctionname = 'main'
codefileextension = '.g'
outputfileextension = '.gb'

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

maxfilesize = 2 ** 15

def compile(filename: str, outputdir: str):
    global phase
    filesIncluded.clear()
    filesCurrentlyIncluding.clear()
    compileOrder.clear()

    throwhelper.log('starting compilation of file ' + filename + '\n')

    throwhelper.log('starting initialization and imports')
    phase = 0
    # load the file and recursively, all its dependencies
    # filesIncluded and compileOrder is now populated
    basefile = initializefile(filename)
    throwhelper.log('ending initialization and imports\n')

    throwhelper.log('compileorder is: ' + ', '.join('{}: {}'.format(i + 1, x.name) for i, x in enumerate(compileOrder)))
    throwhelper.log('')

    # perform compilation phase 1
    throwhelper.log('starting compilation phase 1')
    phase = 1
    for file in compileOrder:
        file.compilephase1()
    throwhelper.log('ending compilation phase 1\n')

    throwhelper.log('starting memory asignments')
    # calculate what memorysegments to include and asign address
    if entryfunctionname not in basefile.functions:
        raise throwhelper.CompileError(
            'no entrypoint found. Add a function named {} in file {}'.format(
                entryfunctionname, basefile.name
            ))
    entryfunction = basefile.functions[entryfunctionname]
    allocator = MemoryAllocator(maxfilesize)
    allocator.allocatealldependents(entryfunction)
    allocator.asignaddresses(entryfunction)
    throwhelper.log('total memory usage: ' + str(allocator.getusedmemory()))
    throwhelper.log('ending memory asignments\n')

    throwhelper.log('starting compilation phase 2')
    # perform phase2 compilation
    phase = 2
    for file in compileOrder:
        file.compilephase2()
    throwhelper.log('ending compilation phase 2\n')

    throwhelper.log('compile successful!\n')

    throwhelper.log('generating output file')
    filecontent = allocator.generatefilecontent()
    throwhelper.log('writing output')
    outputfilename = os.path.join(outputdir, filename) + outputfileextension
    writetofile(outputfilename, filecontent)


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
    name, ext = os.path.splitext(file)
    ext = ext or codefileextension

    with open(name + ext, 'r') as f:
        return f.readlines()


def writetofile(filename, content):
    with open(filename, 'w') as f:
        for index, value in enumerate(content):
            line = '{} {}'.format(index, value)
            if True:
                print(line)
            f.write(line)
            f.write('\n')


def trimcomments(line):
    if commentsymbols in line:
        line = line.partition(commentsymbols)[0]
    return line.strip()


def getglobals():
    return {}


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

        for name, value in self.defines.items():
            result[self.name + '_' + name] = value

        return result

    def getidentifiers(self):
        result = getglobals()
        for dependency in self.dependencies:
            result.update(dependency.exportidentifiers())

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
        self.setstate(0)

        # recursevly compile the file
        context = MainContext(self)
        context.compile()

    def addobject(self, name, obj):
        self.defines[name] = obj
        self.locals[name] = obj

    def nextline(self) -> str:

        if self.linenumber >= len(self.lines):
            raise EOFError
        else:
            result = self.lines[self.linenumber]
            throwhelper.setlinenumber(self.linenumber)
            self.linenumber += 1
            if not result:
                return self.nextline()
            else:
                return result

    def setstate(self, state):
        self.linenumber = state
        throwhelper.setlinenumber(self.linenumber)

    def getstate(self):
        return self.linenumber
