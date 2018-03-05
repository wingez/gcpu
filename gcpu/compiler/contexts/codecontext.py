from gcpu.compiler.memory import CodeFunction, MemorySegment
from gcpu.compiler import compiler, throwhelper
from gcpu.microcode import syntax

from gcpu.compiler.pointer import Pointer
from .context import Context
from . import defcontext, structcontext, instancecontext


class CodeContext(Context):
    starttext = '%'
    endtext = 'end'
    indextext = '.'

    availablecontexts = [defcontext.DefContext, structcontext.StructContext, instancecontext.InstanceContext]

    def __init__(self, parent, name: str):
        super().__init__(parent)

        self.function = None

        if compiler.phase == 1:
            self.function = CodeFunction(name)
            self.function.indices = self.readindices()

            self.compiler.components[CodeFunction, name] = self.function
        elif compiler.phase == 2:
            self.function = self.compiler.components[CodeFunction, name]
            if not self.function.isallocated:
                self.onending()

        p = Pointer(self.function)
        self.scope[name] = p
        for name, i in self.function.indices.items():
            self.scope[name] = p + i

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

    def onending(self):
        return self.function.name, Pointer(self.function)

    def parsestatement(self, statement: str):
        tmp = statement.split()
        mnemonic = tmp[0].lower()
        args = tmp[1:]
        return mnemonic, args

    def evaluateargs(self, args):
        result = [self.scope.evalalutate(arg) for arg in args]
        for arg in result:
            if isinstance(arg, Pointer):
                self.function.dependencies.append(arg.pointsto)
        return result

    def getsyntax(self, mnemonic: str, args: list) -> syntax.Syntax:
        s = syntax.query(mnemonic, args)
        if not s:
            throwhelper.throw('syntax {} not found'.format(mnemonic))
        return s
