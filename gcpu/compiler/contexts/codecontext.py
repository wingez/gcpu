from gcpu.compiler.memory import CodeFunction, MemorySegment
from gcpu.compiler import compiler, throwhelper
from gcpu.microcode import syntax

from gcpu.compiler.pointer import Pointer, ptr
from .context import Context
from .defcontext import DefContext


class CodeContext(Context):
    starttext = '%'
    endtext = 'endf'
    indextext = '.'

    availablecontexts = [DefContext]

    def __init__(self, parent, name: str):
        super().__init__(parent)
        self.variables = parent.variables.copy()

        self.function = None

        if compiler.phase == 1:
            self.function = CodeFunction(name)
            self.function.indices = self.readindices()
        elif compiler.phase == 2:
            self.function = self.compiler.functions[name]
            if not self.function.isallocated:
                self.onexiting()

        p = ptr(self.function)
        self.variables[name] = p
        for name, i in self.function.indices.items():
            self.variables[name] = p + i

        self.offset = 0


    def parseline(self, line: str):
        if line.startswith(self.indextext):
            i = line.lstrip(self.indextext)
            if compiler.phase == 1:
                self.function.indices[i] = self.offset
            elif compiler.phase == 2 and self.offset is not self.function.indices[i]:
                throwhelper.throw('offset doesnt match second pass',
                                  function=self.function,
                                  offset=self.offset)
        else:
            mnemonic, args = self.parsestatement(line)
            args = self.evaluateargs(args)
            s = self.getsyntax(mnemonic, args)
            if compiler.phase == 1:
                self.function.size += s.size
            elif compiler.phase == 2:
                self.function.content.extend(s.compile(args))
            self.offset += s.size

    def oncontextend(self, context, result):
        if context is DefContext:
            id, result = result
            self.variables[id] = result

    def readindices(self):
        indices = {}
        state = self.compiler.getstate()
        line = ''
        while line != self.endtext:
            line = self.compiler.nextline()
            if line.startswith(self.indextext):
                indices[line.lstrip(self.indextext)] = 0
        self.compiler.setstate(state)
        return indices

    def onexiting(self):
        if compiler.phase == 1:
            self.compiler.functions[self.function.name] = self.function
        return self.function.name, ptr(self.function)

    def parsestatement(self, statement: str):
        tmp = statement.split(' ')
        mnemonic = tmp[0].lower()
        args = tmp[1:]
        return mnemonic, args

    def evaluateargs(self, args):
        result = [eval(arg, None, self.variables) for arg in args]
        for arg in result:
            if type(arg) is Pointer:
                self.function.dependencies.extend(arg.dependencies)
        return result

    def getsyntax(self, mnemonic: str, args: list) -> syntax.Syntax:
        s = syntax.query(mnemonic, args)
        if not s:
            throwhelper.throw('syntax {} not found'.format(mnemonic))
        return s
