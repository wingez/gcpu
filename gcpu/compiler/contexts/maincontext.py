from .context import Context
from .defcontext import DefContext
from .codecontext import CodeContext
from .logcontext import LogContext
from .memcontext import MemContext
from gcpu.compiler import compiler, throwhelper, pointer


class MainContext(Context):
    availablecontexts = [DefContext, MemContext, CodeContext, LogContext]
    acceptsEOF = True

    def __init__(self, compiler, globals):
        super().__init__()
        self.compiler = compiler
        self.scope = globals

    def oncontextend(self, context, result):

        if context in (DefContext, CodeContext):
            name, item = result
            self.compiler.addobject(name, item)
        if context is MemContext:
            name, item = result
            if compiler.phase == 1:
                self.compiler.memsegments[name] = item
                self.compiler.addobject(name, pointer.ptr(item))
            elif compiler.phase == 2:
                self.compiler.memsegments[name].content = item.content
                self.compiler.addobject(name, pointer.ptr(self.compiler.memsegments[name]))
