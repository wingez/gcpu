from .context import Context
from gcpu.compiler import compiler

logall = 'logf '
logphase2 = 'log '


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

        result = str(self.scope.evaluate(statement))
        print('log file:{} line:{}  {}'.format(self.compiler.name,
                                               self.compiler.linenumber,
                                               result))
        self.end()

    @classmethod
    def checkstart(cls, statement: str):
        return statement.startswith(logall) or statement.startswith(logphase2)
