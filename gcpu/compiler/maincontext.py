from gcpu.compiler import codecontext, compiler, throwhelper, pointer
from gcpu.compiler.defstatement import defstatement, isdefstatement
from gcpu.compiler.memstatement import memstatement, ismemstatement
from gcpu.compiler.logstatement import logstatement

def compile(comp):
    while True:

        try:
            line = comp.nextline()

        except EOFError:
            return

        if logstatement(line,comp.locals,comp):
            pass
        elif codecontext.check(line):
            codecontext.compile(comp, line)
        elif isdefstatement(line):
            id, result = defstatement(line, comp.locals)
            comp.addobject(id, result)

        elif ismemstatement(line):
            id, result = memstatement(line, comp.locals)
            if compiler.phase == 1:
                comp.memsegments[id] = result
                comp.addobject(id, pointer.ptr(result))
            elif compiler.phase == 2:
                comp.memsegments[id].content = result.content
                comp.addobject(id, pointer.ptr(comp.memsegments[id]))

        else:
            throwhelper.throw('unable to parse. Line: ' + line)
