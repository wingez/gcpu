from .context import Context
from gcpu.compiler import compiler

logall = 'logf '
logphase2 = 'log '
evaldelimeter = '$'


class LogContext(Context):
    # starttext = 'log'

    def __init__(self, parent, statement: str):
        super().__init__(parent)

        if statement.startswith(logphase2):
            if compiler.phase != 2:
                self.end()
                return
            statement = statement[len(logphase2):]
        elif statement.startswith(logall):
            statement = statement[len(logall):]

        result = self.parsestatement(statement)  # str(self.scope.evaluate(statement))
        print('log file:{} line:{}  {}'.format(self.compiler.name,
                                               self.compiler.linenumber,
                                               result))
        self.end()

    def parsestatement(self, statement: str):
        result = statement
        if evaldelimeter in statement:
            result, *junk, statement = statement.partition(evaldelimeter)
            rest = ''
            if ' ' in statement:
                statement, *junk, rest = statement.partition(' ')

            result += str(self.scope.evaluate(statement))
            if rest:
                result += self.parsestatement(rest)
        return result

    @classmethod
    def checkstart(cls, statement: str):
        return statement.startswith(logall) or statement.startswith(logphase2)
