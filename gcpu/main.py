import click
import gcpu._version
from gcpu.microcode import core
from gcpu.compiler import compiler
from gcpu.documentation import generator
from gcpu.utils import *

import os
from functools import wraps


def verboseoption(func):
    @click.option('--verbose', is_flag=True, default=False,
                  help='Display verbose messages.')
    @wraps(func)
    def decorate(*args, **kwargs):
        printverbose.verbose = kwargs.pop('verbose')
        printverbose('command {}', func.__name__)
        result = func(*args, **kwargs)
        printverbose('end of command {}', func.__name__)

    return decorate


def loadconfig(func):
    @verboseoption
    @click.option('--config', type=click.Path(), default='test.py',
                  help='Optional configuration file')
    @wraps(func)
    def decorate(*args, **kwargs):
        core.loadconfig(kwargs.pop('config'))
        return func(*args, **kwargs)

    return decorate


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(gcpu._version.__version__)
def cli(ctx):  # verbose):
    if ctx.invoked_subcommand is None:
        print('****This is the Awesome GCPU SDK program!****')
        print()
        print('You should probably provide some arguments. Read the documentation or type "gcpu --help" for help')


@cli.command(name='create', short_help='Create a new project.')
@click.argument('name')
@click.option('--launch', is_flag=True, help='Open the project folder when finished.')
def createproject(name, launch):
    """Creates a new project. Project will be located in projects/"""
    dir = 'projects/{}/'.format(name)
    file = '{}{}.g'.format(dir, name)

    if os.path.exists(dir):
        print('Project {} already exists'.format(name))
        return
    os.makedirs(dir)

    with open(file, 'w+') as f:
        f.write('\n\n//This is the entry point of the program\n%main\n\nend\n')

    if launch:
        openproject(name)


@cli.command(name='open', short_help='Open an existing project.')
@click.argument('name')
def openproject(name):
    """Opens a project from the defautlt directory projects/"""
    dir = 'projects/{}/'.format(name)
    file = '{}{}.g'.format(dir, name)
    click.launch(file)


@cli.command(name='compile', short_help='Compile a project.')
@click.argument('program')
@loadconfig
def compile(program):
    """Compile a program"""
    if os.path.exists(program):
        name = os.path.splitext(os.path.split(program)[1])[0]
        directory = ''
    else:
        name = program
        program = 'projects/{0}/{0}.g'.format(program)
        directory = 'projects/{}/'.format(name)

    if not os.path.exists(program):
        print('File {} not found'.format(name))
        return

    outputdir = 'output/{}.txt'.format(name)

    compiler.compile(program, outputdir, directory)
    print('done')


@cli.command(name='microcode', short_help='Generate microcode.')
@loadconfig
def microcode():
    """Generates microcode to be used in GCPU-instruction-ROM from provided configfile."""
    core.writeinstructiondatatofile('output/microcode.txt')
    print('done')


@cli.command(name='doc', short_help='Render documentation.')
@click.option('--launch', is_flag=True, help='Open the generated file when ready.')
@loadconfig
def documentation(launch):
    """Renders docuemntation from provided configfile"""
    generator.instructions()
    if launch:
        click.launch('output/doc.html')


if not os.path.exists('output/'):
    os.makedirs('output/')

if __name__ == '__main__':
    cli()
printverbose('Done :)')
