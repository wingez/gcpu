import click
import gcpu._version
from gcpu.microcode import core
from gcpu.compiler import compiler

pass_verbose = click.make_pass_decorator(bool)


@click.group(invoke_without_command=True)
@click.option('--verbose', is_flag=True, help='Print verbose messages')
@click.option('--version', is_flag=True)
@click.pass_context
def cli(ctx, verbose, version):
    ctx.obj = verbose

    if version:
        print(gcpu._version.__version__)


@cli.command()
@click.option('--suppress-warnings', is_flag=True, help=' Do not print warnings during compilation')
@click.argument('configfile', type=click.Path(exists=True))
@click.argument('file', type=click.Path(exists=True))
@pass_verbose
def compile(verbose, suppress_warnings, configfile, file):
    core.loadconfig(configfile)
    compiler.compile(file, 'output')
    print('done')


@cli.command()
@click.argument('configfile', type=click.Path(exists=True))
@pass_verbose
def microcode(verbose, configfile):
    core.loadconfig(configfile)
    print('done')


@cli.command()
@click.argument('configfile', type=click.Path(exists=True))
@click.option('--syntaxes', '-s', is_flag=True, help='Print all availiable syntaxes')
@pass_verbose
def check(verbose, syntaxes, configfile):
    core.loadconfig(configfile)
    print('done')
