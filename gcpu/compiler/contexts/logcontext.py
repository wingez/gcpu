from .context import Context
from gcpu.compiler import throwhelper


class LogContext(Context):
    starttext = 'log '

    def __init__(self, parent, statement: str):
        super().__init__(parent)

        result = str(eval(statement, None, parent.scope))
        throwhelper.log('log file:{} line:{}  {}'.format(self.compiler.name,
                                                         self.compiler.linenumber,
                                                         result))
        self.end()
