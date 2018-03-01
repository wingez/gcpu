from .context import Context
from .defcontext import DefContext
from .codecontext import CodeContext
from .logcontext import LogContext
from .memcontext import MemContext
from .structcontext import StructContext
from gcpu.compiler import compiler, throwhelper, pointer


class MainContext(Context):
    availablecontexts = [DefContext, MemContext, CodeContext, LogContext, StructContext]
    acceptsEOF = True

    def __init__(self, compiler, globals):
        super().__init__()
        self.compiler = compiler
        self.scope = globals.copy()

    def onending(self):
        return self.scope
