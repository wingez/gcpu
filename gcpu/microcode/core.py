from gcpu.betterexec import betterexec

from gcpu.microcode.register import Register
from gcpu.microcode.constant import Constant
from gcpu.microcode import syntax
import os
from gcpu.compiler.pointer import Pointer

outputfileextensions = '.gb'

# the instructionsset
instructions = []
# the registers avialiable as parameters
registers = []

# array representing memory content of the Microcode-ROMs
# as of 1.5 for 15bits(8instr,5stage,2flags)=32k * 4byte
# content represented by 32bit uint
instructiondata = [0] * (2 ** 15)


def CreateRegister(index, name, read, write, description=''):
    result = Register(index, name, read, write, description)
    registers.append(result)
    return result


class Instruction(object):
    def __init__(self):
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


def CreateInstruction(mnemonic='', group='uncategorized', desc='', id=None,
                      stages=[], args={}, compilefunc=None):
    instr = Instruction()
    instr.group = group
    instr.description = desc
    instr.stages = stages
    instr.id = id
    instr.compilefunction = compilefunc

    if compilefunc:
        instr.size += getinstructionsize(args, compilefunc)

    if mnemonic:
        priority = 1 if not all([arg.isgeneric for arg in args]) else 0
        syntax.create(mnemonic, args, instr, priority)

    instructions.append(instr)

    return instr


defaultparamvalues = {
    Register: Register(0, '', [], []),
    int: 0,
    Pointer: Pointer(0),
    Constant: None}


def getinstructionsize(args, compilefunction):
    params = [defaultparamvalues[arg.arg] if arg.isgeneric else arg.arg for arg in args if arg.include]
    return len(compilefunction(*params))


def loadinstructions(filename):
    # TODO preparatiosn

    # Parse file
    print('parsing file ' + filename)
    betterexec(open(filename).read(), description=filename)

    # instructions and registers assume has valid data

    for i in range(0, len(instructiondata)):
        instructiondata[i] = defaultinstructiondata

    assignidtoinstructions()

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
    usedids = [False] * (2 ** 8)

    for i in instructions:

        # Note to self: Dont do (if i.id:) since 0 is a valid id
        if i.id is not None:
            if usedids[i.id]:
                raise ValueError('double assignment of id ' + str(i.id))
            usedids[i.id] = True

    toassignid = sorted([x for x in instructions if x.id is None], key=lambda instr: instr.group)

    lowestfreeid = 0

    for instr in toassignid:
        while usedids[lowestfreeid]:
            lowestfreeid += 1
            if lowestfreeid >= 2 ** 8:
                raise ValueError('Instructioncount exceded 256')

        instr.id = lowestfreeid


defaultinstructiondata = 0


def setdefaultinstructiondata(signals):
    global defaultinstructiondata
    defaultinstructiondata = signalstoint(signals)


def setinstructiondata(instruction, stageindex, flags, signals):
    addr = encodeaddress(instruction.id, stageindex, flags)
    instructiondata[addr] = signalstoint(signals)


def compileinstructionstages(instruction):
    for stageindex, stage in enumerate(instruction.stages):
        hasflags = type(stage) is dict
        for flags in range(0, 4):
            stagesignals = getstagedatawithcorrectflags(stage, flags) if hasflags else stage
            setinstructiondata(instruction, stageindex, flags, stagesignals)


# none zero ovf zeronotovf ovfnotzero ovfzero
flagspriority = [
    ['none', 'fill'],
    ['ovfnotzero', 'ovf', 'fill'],
    ['zeronotovf', 'zero', 'fill'],
    ['ovfzero', 'ovf', 'zero', 'fill']]


def getstagedatawithcorrectflags(stage, flags):
    for p in flagspriority[flags]:
        for s in stage:
            if s == p:
                return stage[s]

    raise ValueError("Stage contained no code for flags: " + str(flags))


def signalstoint(signals):
    result = 0
    for signal in signals:
        result |= (1 << signal)
    return result


def encodeaddress(instruction, stage, flags):
    return instruction | (stage << 8) | (flags << 13)


def decodeaddress(address):
    instruction = 0x00ff & address
    stage = (0x1f00 & address) >> 8
    flags = (0x6000 & address) >> 13

    return {'instruction': instruction, 'stage': stage, 'flags': flags}
