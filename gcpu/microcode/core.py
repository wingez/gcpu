from gcpu import betterexec
from gcpu.config import cfg
from gcpu.microcode.register import Register
from gcpu.microcode.constant import Constant
from gcpu.microcode import syntax, flag
from gcpu.microcode.instruction import Instruction
from gcpu.compiler.pointer import Pointer

from operator import attrgetter
from itertools import product, count, chain, filterfalse, starmap
import os
import logging

log = logging.getLogger(__name__)

outputfileextensions = '.gb'


def config(**kwargs):
    for c, v in kwargs.items():
        if c not in cfg:
            raise ValueError('{} not valid setting'.format(c))
        cfg[c] = v


# the registers avialiable as parameters
registers = []
signals = []
flags = []
instructions = []


def CreateRegister(index, name, read, write, description=''):
    result = Register(index, name, read, write, description)
    registers.append(result)
    return result


def Signal(index, name='', description=''):
    signals.append({'index': index, 'name': name, 'desciption': description})
    return [index]


def CreateFlag(name, index):
    f = flag.Flag(name, index)
    flags.append(f)
    return f.createstate()


def CreateInstruction(name, **kwargs):
    i = Instruction(name, **kwargs)
    instructions.append(i)
    return i


def loadconfig(configfilename):
    # Parse file
    log.info('loading configfile: {}'.format(configfilename))

    betterexec.exec(open(configfilename).read(), description=configfilename)

    # instructions and registers assume has valid data
    assignindextoinstructions()

    print('Compile successful!')


def writeinstructiondatatofile(filename: str, verbose=True):
    with open(filename, 'w') as f:

        for instruction in instructions:
            f.write('#Instruction {}\n'.format(instruction.name))
            for addr, data in instruction.compilemicrocode(flags):
                f.write('{:5} {:5} # {:0>15b} {:0>32b}\t\t\n'.format(addr, data, addr, data))


def assignindextoinstructions():
    maxsize = cfg['instruction_ids']
    usedindices = [None] * maxsize

    if len(instructions) >= maxsize:
        raise ValueError('to many instructions')

    def assign(instruction, index):
        if index >= maxsize:
            raise ValueError('index over maxsize')
        if usedindices[index]:
            raise ValueError('double assignment of index {}'.format(index))
        instruction.index = index
        usedindices[index] = instruction

    for i in instructions:
        if i.index is not None:
            assign(i, i.index)

    toassign = sorted([x for x in instructions if x.index is None], key=attrgetter('group'))

    for instr, index in zip(toassign, (x for x in count(0) if not usedindices[x])):
        assign(instr, index)
