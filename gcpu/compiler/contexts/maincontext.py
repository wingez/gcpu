from .context import Context
from .defcontext import DefContext
from .codecontext import CodeContext
from .logcontext import LogContext
from .memcontext import MemContext
from .structcontext import StructContext
from .instancecontext import InstanceContext
from . import scope


class MainContext(Context):
    availablecontexts = [DefContext, MemContext, CodeContext,
                         LogContext, StructContext, InstanceContext,
                         ]
    acceptsEOF = True
    scopemode = scope.new

    def __init__(self, compiler, globals):
        super().__init__()
        self.compiler = compiler
        self.scope.update(globals)

    def onending(self):
        return self.scope
