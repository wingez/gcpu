import gcpu.compiler.throwhelper as throwhelper


def nextline(compiler, context):
    line = compiler.nextline()
    if not line:
        throwhelper.throw('end of file reached', context=context.__name__)
    return line


