import gcpu.compiler.throwhelper as throwhelper
from typing import List, Dict


class Context:
    starttext = None
    endtext = None
    acceptsEOF = False
    availablecontexts = []

    def __init__(self, parent=None):
        self.compiler = parent.compiler if parent else None
        self.active = True
        self.result = None
        self.parent = parent
        self.scope = parent.scope.copy() if parent else {}

    def compile(self):

        while True:
            if not self.active:
                break
            line = ''
            try:
                line = self.compiler.nextline()
            except EOFError:
                if self.acceptsEOF:
                    self.exit()
                    break
                throwhelper.throw('end of file reached', context=self.__name__)

            if self.endtext and line == self.endtext:
                self.exit()
                break

            for context in self.availablecontexts:
                if context.checkstart(line):
                    startstament = line.lstrip(context.starttext)
                    c = context(self, startstament)
                    result = c.compile()
                    self.oncontextend(context, result)
                    break
            else:
                if self.parseline(line) is False:
                    throwhelper.throw('line could not be parsed',
                                      file=self.compiler.name,
                                      linenumber=self.compiler.linenumber,
                                      context=type(self).__name__)

        if self.parent:
            self.parent.oncontextend(self.__class__, self.result)
        return self.result

    def exit(self):
        result = self.onending()
        if type(result) is tuple:
            self.end(*result)
        else:
            self.end(result)

    def docontext(self, context, statement):
        return context(self, statement).compile()

    def parseline(self, line):
        return False

    def end(self, *result):
        self.result = result
        self.active = False

    def oncontextend(self, context, result):
        return ()

    def onending(self):
        pass

    @classmethod
    def checkstart(cls, statement: str) -> bool:
        if not cls.starttext:
            raise NotImplementedError(str(cls))
        return statement.startswith(cls.starttext)
