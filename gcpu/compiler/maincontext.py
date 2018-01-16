
from gcpu.compiler.defstatement import defstatement, isdefstatement


import gcpu.compiler.codecontext as codecontext


def compile(compiler):
    while True:

        try:
            line = compiler.nextline()

        except EOFError:
            return

        if codecontext.check(line):
            codecontext.compile(compiler, line)
        elif isdefstatement(line):
            id, result = defstatement(line, compiler.locals)
            compiler.locals[id] = result
