import click
import gcpu._version
from gcpu.microcode import core, syntax
from gcpu.compiler import compiler
from gcpu.documentation import generator

import os
import logging


@click.group(invoke_without_command=True)
@click.option('--verbose', is_flag=True, help='Print verbose messages')
@click.option('--version', is_flag=True)
def cli(verbose, version):
    if version:
        print(gcpu._version.__version__)

    logging.basicConfig(level=logging.INFO if verbose else logging.ERROR)


@cli.command()
@click.option('--suppress-warnings', is_flag=True, help=' Do not print warnings during compilation')
@click.argument('configfile', type=click.Path(exists=True))
@click.argument('file', type=click.Path(exists=True))
def compile(suppress_warnings, configfile, file):
    loadconfig(configfile)
    compiler.compile(file, 'output')
    print('done')


@cli.command()
@click.argument('configfile', type=click.Path(exists=True))
def microcode(configfile):
    loadconfig(configfile)
    name = os.path.splitext(configfile)[0]
    core.writeinstructiondatatofile('output/{}.o'.format(name))

    print('done')


@cli.command()
@click.argument('configfile', type=click.Path(exists=True))
@click.option('--syntaxes', '-s', is_flag=True, help='Print all availiable syntaxes')
def check(syntaxes, configfile):
    loadconfig(configfile)
    if syntaxes:
        syntax.printall()


@cli.command()
@click.option('--configfile', '-c', type=click.Path(exists=True))
@click.option('-d', is_flag=True, help='Opens the file when done')
def documentation(configfile, d):
    if configfile:
        loadconfig(configfile)
        generator.instructions()

        if d:
            click.launch('output\\doc.html')


def loadconfig(configfile):
    core.loadconfig(configfile)


if __name__ == '__main__':
    cli()
