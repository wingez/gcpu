from gcpu import betterexec
from gcpu.microcode.register import Register
from gcpu.microcode.constant import Constant
from gcpu.microcode import syntax, flags
from gcpu.compiler.pointer import Pointer

from operator import attrgetter
from itertools import product, count, chain
import os

outputfileextensions = '.gb'

# the instructionsset
instructions = []

log = lambda s: s

# array representing memory content of the Microcode-ROMs
# as of 1.5 for 15bits(8instr,5stage,2flags)=32k * 4byte
# content represented by 32bit uint
instructiondata = []

conf = {
    'use_microcode': False,
    'microcode_default': 0,
    'microcode_branching': False,
    'microcode_pass_index': False,
    'microcode_encode': lambda kwargs: kwargs['instruction'],
    'microcode_size': 256,
    'instruction_ids': 256,
    'recursion': True,
    'program_size': 256,
    'memsegments': False,
}


def config(**kwargs):
    for c, v in kwargs.items():
        if c not in conf:
            raise ValueError('{} not valid setting'.format(c))
        conf[c] = v


# the registers avialiable as parameters
registers = []


def CreateRegister(index, name, read, write, description=''):
    result = Register(index, name, read, write, description)
    registers.append(result)
    return result


class Instruction(object):
    def __init__(self, name):
        self.name = name
        self.stages = None
        self.id = None

        self.group = None
        self.description = None
        self.arguments = None
        self.arguentsize = None
        self.compilefunction = None
        self.size = 1

    def compile(self, args):
        result = [self.id]
        if self.compilefunction:
            result += self.compilefunction(*args)
        return result

    def addsyntax(self, mnemonic, args, priority=0):
        syntax.create(mnemonic, args, self, priority)
        return self


flagslist = []


def CreateFlag(name, index):
    f = flags.createflag(name, index)
    flagslist.append(f)
    return f


def CreateInstruction(name, mnemonic='', group='uncategorized', desc='', id=None,
                      stages=None, args=(), compilefunc=None):
    i = Instruction(name)
    i.group, i.description, i.id, i.compilefunction = group, desc, id, compilefunc

    if conf['use_microcode']:
        if not stages:
            raise ValueError('No stages found')
        i.stages = parsestages(stages)

    if compilefunc:
        i.size = getinstructionsize(args, compilefunc)

    priority = 1 if not all([arg.isgeneric for arg in args]) else 0
    syntax.create(mnemonic or name, args, i, priority)

    instructions.append(i)

    return i


defaultparamvalues = {
    Register: Register(0, '', [], []),
    int: 0,
    Pointer: Pointer(0),
    Constant: None}


class Stage:
    def __init__(self, parts):
        self.parts = parts

    def getsignalsfromflag(self, flag):
        part = max((x for x in self.parts if x.matchesflags(flag)),
                   key=attrgetter('priority'), default=False)
        if not part:
            raise ValueError('no stage found for flags {}'.format(flag))
        return part.signals

    def getusedflags(self):
        result = []
        for part in self.parts:
            for f in chain(part.flag.musthave, part.flag.mustnothave):
                if f not in result:
                    result.append(f)
        return f


class StagePart:
    def __init__(self, flags, signals):
        self.flags, self.signals = flags, signals
        self.priority = 0 if not flags else flags.priority

    def matchesflags(self, flag):
        return self.flags.compatible(flag)


def parsestages(stages):
    result = []

    for stageraw in stages:
        parts = []

        if type(stageraw) is list:
            parts.append(StagePart(flags.empty, stageraw))
        elif type(stageraw) is dict:
            if not conf['microcode_branching']:
                raise ValueError('Not configured to accept branching')
            for flag, signals in stageraw.items():
                parts.append(StagePart(flag, signals))
        else:
            raise ValueError('')

        result.append(Stage(parts))

    return result


def getinstructionsize(args, compilefunction):
    params = [defaultparamvalues[arg.arg] if arg.isgeneric else arg.arg for arg in args if arg.include]
    return len(compilefunction(*params))


def loadconfig(configfilename, verbose=True):
    if verbose:
        global log
        log = lambda s: print(s)

    # Parse file
    log('loading configfile: {}'.format(configfilename))

    betterexec.exec(open(configfilename).read(), description=configfilename)

    # instructions and registers assume has valid data
    assignidtoinstructions()

    if conf['use_microcode']:
        global instructiondata
        instructiondata = [conf['microcode_default']] * conf['microcode_size']

        for instruction in instructions:
            try:
                compileinstructionstages(instruction)
            except Exception as e:
                print('error compiling instruction ', instruction.id, ' ', instruction.group)
                raise e
    print('Compile successful!')


def writeinstructiondatatofile(filename: str, outputdir: str):
    filename = os.path.join(outputdir, filename) + outputfileextensions
    with open(filename, 'w') as f:
        for index, value in enumerate(instructiondata):
            line = '{} {}'.format(index, value)
            f.write(line)
            f.write('\n')


def assignidtoinstructions():
    maxsize = conf['instruction_ids']
    usedids = [None] * maxsize

    if len(instructions) >= maxsize:
        raise ValueError('to many instructions')

    def assign(instruction, id):
        if id >= maxsize:
            raise ValueError('id over maxsize')
        if usedids[id]:
            raise ValueError('double assignment of id {}'.format(id))
        instruction.id = id
        usedids[id] = instruction

    for i in instructions:
        if i.id is not None:
            assign(i, i.id)

    toassign = sorted([x for x in instructions if x.id is None], key=attrgetter('group'))

    for instr, id in zip(toassign, (x for x in count(0) if not usedids[x])):
        assign(instr, id)


def compileinstructionstages(instruction):
    flagcombinations = product(*[(flag, -flag) for flag in flagslist])

    addressfunc = conf['microcode_encode']

    for stageindex, stage in enumerate(instruction.stages):
        for flag in flagcombinations:
            signals = stage.getsignalsfromflag(flag)

            addr = addressfunc(instruction=instruction.id,
                               stage=stageindex,
                               flags=flags.flagstoint(flag))
            instructiondata[addr] = signalstoint(signals)


def signalstoint(signals):
    result = 0
    for signal in signals:
        result |= (1 << signal)
    return result
