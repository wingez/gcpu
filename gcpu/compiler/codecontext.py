from gcpu.compiler.memory import MemorySegment
from gcpu.compiler import compiler, throwhelper
from gcpu.compiler.dependecyconstant import DependencyConstant
from gcpu.microcode import syntax

startsymbol = '%'
endsymbol = 'endf'
indexsymbol = '.'


class CodeFunction(MemorySegment):

    def __init__(self, name: str, compiler):# newcompiler.FileCompiler):
        self.name = name
        self.compiler = compiler
        self.indices = {}
        super().__init__()


def compile(compiler, startline: str):
    locals = compiler.locals.copy()
    function = None

    name = startline.lstrip(startsymbol)
    if compiler.phase == 1:
        function = CodeFunction(name, compiler)
        function.indices = readindices(compiler)
        compiler.functions[name]=function
    elif compiler.phase == 2:
        function = compiler.functions[name]
        if not function.isallocated:
            return

    locals.update(function.indices)

    offset = 0
    while True:
        line = compiler.nextline()
        if line == endsymbol:
            break
        elif isindex(line):
            i = index(line)
            if compiler.phase == 1:
                function.indices[i] = offset
            elif compiler.phase == 2 and offset is not function.indices[i]:
                throwhelper.throw('offset doesnt match second pass', function=function, offset=offset)

        else:
            mnemonic, args = parseprogramstatement(line)
            args = evaluateargs(args, locals, function)
            s = getsyntax(mnemonic, args)
            if compiler.phase == 1:
                function.size += s.size
                offset += s.size
            elif compiler.phase == 2:
                function.content.extend(s.compile(args))

def readindices(compiler):
    indices = {}
    begstate = compiler.getstate()
    while True:
        line = compiler.nextline()

        if line == endsymbol:
            break
        if isindex(line):
            i = index(line)
            indices[i] = 0
    compiler.setstate(begstate)
    return indices


def parseprogramstatement(statement: str):
    tmp = statement.split(' ')
    mnemonic = tmp[0].lower()
    args = tmp[1:]
    return mnemonic, args


def evaluateargs(args, vars, function: CodeFunction):
    result = [eval(x, locals=vars) for x in args]
    for i, arg in enumerate(result):
        if type(arg) is DependencyConstant:
            if compiler.phase == 1:
                result[i] = 0
                function.dependencies.append(arg.dependencies)
            elif compiler.phase == 2:
                throwhelper.throw('type: dependencyconstant invalid in phase 2')
    return result


def getsyntax(mnemonic: str, args: list) -> syntax.Syntax:
    s = syntax.query(mnemonic, args)
    if not s:
        throwhelper.throw('syntax {} not found'.format(mnemonic))
    return s


def check(line: str):
    return line.startswith(startsymbol)


def isindex(line: str):
    return line.startswith(indexsymbol)


def index(line: str):
    return line.partition(indexsymbol)[2]
