from gcpu.compiler import codecontext, compiler, throwhelper
from gcpu.compiler.defstatement import defstatement, isdefstatement
from gcpu.compiler.memory import MemorySegment
from gcpu.compiler.dependecyconstant import DependencyConstant


def compile(comp):
    while True:

        try:
            line = comp.nextline()

        except EOFError:
            return

        if codecontext.check(line):
            codecontext.compile(comp, line)
        elif isdefstatement(line):
            id, result = defstatement(line, comp.locals)

            if type(result) is MemorySegment:
                if compiler.phase == 1:
                    result.id = id
                    comp.memsegments[id] = result
                    comp.addobject(id, DependencyConstant(result))
                elif compiler.phase == 2:
                    comp.memsegments[id].content = result.content
                    comp.addobject(id, comp.memsegments[id].address)
            else:
                comp.addobject(id, result)

        else:
            throwhelper.throw('unable to parse. Line: ' + line)
