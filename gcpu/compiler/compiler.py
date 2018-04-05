from gcpu.compiler import throwhelper
# from gcpu.compiler import maincontext
from gcpu.compiler.contexts.maincontext import MainContext
from gcpu.compiler.memory import MemoryAllocator, MemorySegment, CodeFunction
from gcpu.config import cfg
import gcpu._version
import os
from gcpu.utils import printverbose

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

cwd = ''


def compile(filename: str, outputfile: str, directory: str):
    global phase, cwd
    cwd = directory

    filesIncluded.clear()
    filesCurrentlyIncluding.clear()
    compileOrder.clear()

    totalmemory = cfg['program_size']
    printverbose('starting compilation of file {}', filename)

    printverbose('\nstarting initialization and imports')
    phase = 0
    # load the file and recursively, all its dependencies
    # filesIncluded and compileOrder is now populated
    basefile = initializefile(filename)
    printverbose('ending initialization and imports')

    printverbose('\ncompileorder is: {}', ', '.join('{}: {}'.format(*v) for v in enumerate(compileOrder, 1)))

    # perform compilation phase 1
    printverbose('\nstarting compilation phase 1')
    phase = 1
    for file in compileOrder:
        file.compilephase1()
    printverbose('ending compilation phase 1')

    printverbose('\nstarting memory asignments')

    # calculate what memorysegments to include and asign address
    entryfunction = basefile.components[CodeFunction].get(entryfunctionname, None)
    if not entryfunction:
        raise throwhelper.CompileError(
            'no entrypoint found. Add a function named {} in file {}'.format(
                entryfunctionname, basefile.name
            ))
    allocator = MemoryAllocator(totalmemory)
    allocator.allocatealldependents(entryfunction)
    allocator.asignaddresses(entryfunction)
    usedmemory = allocator.getusedmemory()
    printverbose('total memory usage: {}', usedmemory)
    printverbose('ending memory asignments')
    Globals.mem_total = totalmemory
    Globals.mem_used = usedmemory
    Globals.mem_free = totalmemory - usedmemory
    Globals.mem_free_first = allocator.currentaddress
    Globals.mem_free_last = totalmemory - 1

    printverbose('\nstarting compilation phase 2')
    phase = 2
    for file in compileOrder:
        file.compilephase2()
    printverbose('ending compilation phase 2')

    printverbose('\ncompile successful!')

    printverbose('\ngenerating output file')
    filecontent = allocator.generatefilecontent()
    printverbose('writing output')

    writetofile(outputfile, filecontent)


def findfile(filename):
    dir, ext = os.path.splitext(filename)

    filename = dir + (ext or codefileextension)
    # 1:seach within local directory
    file = cwd + filename
    if os.path.exists(file):
        return file

    # 2:search within absolute directory
    file = filename
    if os.path.exists(file):
        return file

    # 3:search within stdlib
    file = 'stdlib/' + filename
    if os.path.exists(file):
        return file

    raise FileNotFoundError(filename)


def initializefile(name):
    filename = findfile(name)

    # strip eventual extension
    name = os.path.splitext(name)[0]
    name = name.replace('/', '_')

    if name in filesIncluded:
        return filesIncluded[name]

    if name in filesCurrentlyIncluding:
        throwhelper.throw('including: {} would cause a dependency loop'.format(name))

    printverbose('begins importing of {}', name)

    filesCurrentlyIncluding.append(name)

    c = FileCompiler(name, filename)

    compileOrder.append(c)
    filesIncluded[name] = c
    filesCurrentlyIncluding.remove(name)

    printverbose('end importing of {}', name)

    return c


def readlines(file):
    name, ext = os.path.splitext(file)
    ext = ext or codefileextension

    with open(name + ext, 'r') as f:
        return f.readlines()


def writetofile(filename, content):
    with open(filename, 'w+') as f:
        for index, value in enumerate(content):
            line = '{} {}'.format(index, value)
            #TODO fix dis shit
            if True:
                print(line)
            f.write(line)
            f.write('\n')


def trimcomments(line):
    if commentsymbols in line:
        line = line.partition(commentsymbols)[0]
    return line.strip()


class Globals:
    version = gcpu._version.__version__
    # Total memory
    mem_total = 0
    # Total size of allocated memory
    mem_used = 0
    # Amount of memory avaliable for dynamic usage
    mem_free = 0
    # First address of unallocated memory region
    mem_free_first = 0
    # Last address of unallocated memory region
    mem_free_last = 0
    # Size of ram pages
    pagesize = 2 ** 8


def getglobals():
    return {'globals': Globals}


class FileCompiler:

    def __init__(self, name, path):
        """
        Creates a new filecompiler,load the raw textfile and read  dependencies
        """
        self.name = name
        self.dependencies = []

        self.components = CompilerComponents()

        self.toexport = {}

        self.linenumber = 0
        self.lines = [trimcomments(x) for x in readlines(path)]
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
        return {'{}_{}'.format(self.name, key): value for key, value in self.toexport.items()}

    def getidentifiers(self):
        result = getglobals()
        for dependency in self.dependencies:
            result.update(dependency.exportidentifiers())

        return result

    def compilephase1(self):
        self.compile()

    def compilephase2(self):
        self.compile()

    def compile(self):
        throwhelper.file = self.name
        globalsdefintions = self.getidentifiers()

        self.setstate(0)

        # recursevly compile the file
        context = MainContext(self, globalsdefintions)
        definitions = context.compile()

        self.toexport = {k: v for k, v in definitions.items() if not (k, v) in globalsdefintions.items()}

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

    def __str__(self):
        return self.name


class CompilerComponents:
    def __init__(self):
        self.dicts = {}

    def assertdictype(self, dicttype):
        if dicttype not in self.dicts:
            self.dicts[dicttype] = {}

    def __setitem__(self, key, value):
        t, k = key

        self.assertdictype(t)
        self.dicts[t][k] = value

    def __getitem__(self, item):
        if type(item) is tuple:
            t, k = item
            self.assertdictype(t)
            return self.dicts[t][k]
        else:
            t = item
            self.assertdictype(t)
            return self.dicts[t]
