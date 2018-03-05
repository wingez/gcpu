import gcpu.compiler.throwhelper as throwhelper
from typing import List, Dict
from . import scope


class Context:
    starttext = None
    endtext = None
    acceptsEOF = False
    availablecontexts = []
    scopemode = 0

    def __init__(self, parent=None):
        self.compiler = parent.compiler if parent else None
        self.active = True
        self.result = None
        self.parent = parent

        self.setupscope()

    def setupscope(self):
        """
        Setup the scope. If no custom scopemode attribute is asigned the scope default to extend if context has 
        other context available as childrens or inherit if it does not.
        :return:
        """
        scopemode = self.scopemode or (scope.extend if self.availablecontexts else scope.inherit)

        if scopemode == scope.inherit:
            self.scope = self.parent.scope
        elif scopemode == scope.extend:
            self.scope = self.parent.scope.copy()
        elif scopemode == scope.new:
            self.scope = scope.Scope()
        else:
            raise ValueError('Unknown scopemode: '.format(scopemode))

    def compile(self):

        while True:
            if not self.active:
                break
            line = ''
            try:
                line = self.compiler.nextline()
            except EOFError:
                if self.acceptsEOF:
                    self._exit()
                    break
                throwhelper.throw('end of file reached', context=self.__name__)

            if self.endtext and line == self.endtext:
                self._exit()
                break

            for context in self.availablecontexts:
                if context.checkstart(line):
                    startstament = line[len(context.starttext):]
                    c = context(self, startstament)
                    c.compile()
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

    def _exit(self):
        result = self.onending()
        if type(result) is tuple:
            self.end(*result)
        else:
            self.end(result)

    def docontext(self, context, statement):
        """Scope to a new context"""
        return context(self, statement).compile()

    def parseline(self, line):
        """This method gets called for every line in the context. Return False if line could not be parsed"""
        return False

    def end(self, *result):
        """Call this method when a context has finished parsing and control should return to its parent."""
        self.result = result[0] if len(result) == 1 else result
        self.active = False

    def onending(self) -> tuple:
        """This method gets called when the end characters are reached.
        Return a tuple containg the result of the context"""
        return ()

    def oncontextend(self, context, result):
        """This method gets called when a childcontext ends. By default adds result to scope"""
        if type(result) is tuple and len(result) == 2:
            if type(result[0]) is str:
                self.scope[result[0]] = result[1]

    @classmethod
    def checkstart(cls, statement: str) -> bool:
        if not cls.starttext:
            raise NotImplementedError(str(cls))
        return statement.startswith(cls.starttext)
