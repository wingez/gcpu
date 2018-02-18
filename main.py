import sys
from gcpu import bithelper
from gcpu.microcode import core
from gcpu.microcode import syntax

from gcpu.compiler import compiler


def compilefile(args):
    microcode = args[0]
    file = args[1]
    core.loadinstructions(microcode)
    syntax.printall()
    compiler.compile(file, 'output')


def microcode(args):
    name = args[0]
    core.loadinstructions(name)
    syntax.printall()
    core.writeinstructiondatatofile('mc' + name, 'output')


if __name__ == '__main__':

    action = sys.argv[1]
    args = sys.argv[2:]

    if action == 'compile':
        compilefile(args)
    elif action == 'microcode':
        microcode(args)
    elif action == 'doc':
        import gcpu.documentation.generator as docgenerator

        if args[0] == 'instructions':
            microcode(args[1:])
            docgenerator.render_instructions()
