from gcpu import betterexec
from gcpu.microcode.register import Register
from gcpu.microcode.constant import Constant
from gcpu.microcode import syntax, flags
from gcpu.compiler.pointer import Pointer

from operator import attrgetter
from itertools import product, count, chain, filterfalse, starmap
import os

outputfileextensions = '.gb'

log = lambda s: s

cfg = {
    'use_microcode': False,
    'microcode_default': [],
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
        if c not in cfg:
            raise ValueError('{} not valid setting'.format(c))
        cfg[c] = v


# the registers avialiable as parameters
registers = []


def CreateRegister(index, name, read, write, description=''):
    result = Register(index, name, read, write, description)
    registers.append(result)
    return result


signals = []


def Signal(index, name='', description=''):
    signals.append({'index': index, 'name': name, 'desciption': description})
    return [index]


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

    def addsyntax(self, mnemonic, args=(), priority=0):
        syntax.create(mnemonic, args, self, priority)
        return self

    def __str__(self):
        return self.name

    def getsyntaxes(self):
        return [s for s in syntax.syntaxes if s.instruction is self]

    def getusedflags(self):
        return set(chain.from_iterable((s.getusedflags() for s in self.stages)))


def compileinstruction(instruction, args):
    if cfg['microcode_pass_index']:
        args.insert(0, instruction.id)
    return instruction.compile(args)


flagslist = []


def CreateFlag(name, index):
    f = flags.createflag(name, index)
    flagslist.append(f)
    return f


instructions = []


def CreateInstruction(name, mnemonic='', group='uncategorized', desc='', id=None,
                      stages=None, args=(), compilefunc=None):
    i = Instruction(name)
    i.group, i.description, i.id, i.compilefunction = group, desc, id, compilefunc

    if cfg['use_microcode']:
        if not stages:
            raise ValueError('No stages found')
        i.stages = parsestages(stages)

    if compilefunc:
        i.size = getinstructionsize(args, compilefunc)

    priority = 1 if not all([arg.isgeneric for arg in args]) else 0
    syntax.create(mnemonic or name, args, i, priority)

    instructions.append(i)

    return i


def getinstructionsize(args, compilefunction):
    params = [defaultparamvalues[arg.arg] if arg.isgeneric else arg.arg for arg in args if arg.include]
    return len(compilefunction(*params))


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
                   key=attrgetter('priority'), default=None)
        return part.signals if part else None

    def getusedflags(self):
        return set((f for p in self.parts
                    for f in chain(p.flag.musthave, p.flag.mustnothave)))


class StagePart:
    def __init__(self, flag, signals):
        self.flag, self.signals = flag, signals
        self.priority = 0 if not flag else flag.priority

    def matchesflags(self, flag):
        return self.flag.compatible(flag)


def parsestages(stages):
    result = []

    for stageraw in stages:
        parts = []

        if type(stageraw) is list:
            parts.append(StagePart(flags.flag_empty, stageraw))
        elif type(stageraw) is dict:
            if not cfg['microcode_branching']:
                raise ValueError('Not configured to accept branching')
            for flag, signals in stageraw.items():
                parts.append(StagePart(flag, signals))
        else:
            raise ValueError('')

        result.append(Stage(parts))

    return result


def loadconfig(configfilename, verbose=True):
    if verbose:
        global log
        log = lambda s: print(s)

    # Parse file
    log('loading configfile: {}'.format(configfilename))

    betterexec.exec(open(configfilename).read(), description=configfilename)

    # instructions and registers assume has valid data
    assignidtoinstructions()

    if cfg['use_microcode']:
        instructiondata = compileinstructionstages()

    print('Compile successful!')


def writeinstructiondatatofile(filename: str, outputdir: str, instructiondata):
    filename = os.path.join(outputdir, filename) + outputfileextensions
    with open(filename, 'w') as f:
        for index, value in enumerate(instructiondata):
            line = '{} {}'.format(index, value)
            f.write(line)
            f.write('\n')


def assignidtoinstructions():
    maxsize = cfg['instruction_ids']
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


def compileinstructionstages():
    instructiondata = [signalstoint(cfg['microcode_default'])] * cfg['microcode_size']
    flagcombinations = [a + b for a, b in product(*[(flag, -flag) for flag in flagslist])]

    addressfunc = cfg['microcode_encode']

    for (instr, (index, stage)), flag in product(((i, s) for i in instructions
                                                  for s in enumerate(i.stages)),
                                                 flagcombinations):
        signals = stage.getsignalsfromflag(flag)
        if not signals:
            raise ValueError('Instruction: {}, Stage: {}, No matching signals for flags:{}'.format(
                instr, index, flag))

        addr = addressfunc(instruction=instr.id,
                           stage=index,
                           flags=flag.encode())
        data = signalstoint(signals)
        instructiondata[addr] = data
        print(bin(addr), bin(data))
    return instructiondata


def signalstoint(signals):
    result = 0
    for signal in signals:
        result |= (1 << signal)
    return result
