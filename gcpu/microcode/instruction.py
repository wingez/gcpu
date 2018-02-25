from gcpu.config import cfg
from .register import Register
from ..compiler.pointer import Pointer
from .constant import Constant
from . import syntax
from .flag import flag_empty

from itertools import chain, product
from operator import attrgetter


class Instruction(object):
    defaultparamvalues = {
        Register: Register(0, '', [], []),
        int: 0,
        Pointer: Pointer(0),
        Constant: None}

    def __init__(self, name, mnemonic='', group='uncategorized', desc='', index=None,
                 stages=None, args=(), compilefunc=None):

        self.name, self.group, self.description, self.index, self.compilefunction \
            = name, group, desc, index, compilefunc

        if cfg['use_microcode']:
            if not stages:
                raise ValueError('Missing argument stages')
            self.stages = self.parsestages(stages)

        self.size = len(self.compile(
            [self.defaultparamvalues[arg.arg] if arg.isgeneric else arg.arg
             for arg in args if arg.include]))

        self.addsyntax(mnemonic or name, args)

    def compile(self, args):
        result = []
        if cfg['microcode_pass_index']:
            args.insert(0, self.index)
        else:
            result.append(self.index)

        if self.compilefunction:
            result += self.compilefunction(*args)
        return result

    def addsyntax(self, mnemonic, args=(), priority=None):
        if priority is None:
            priority = 1 if not all([arg.isgeneric for arg in args]) else 0
        syntax.create(mnemonic, args, self, priority)
        return self

    def __str__(self):
        return self.name

    def getusedflags(self):
        return set(chain.from_iterable((s.getusedflags() for s in self.stages)))

    def compilemicrocode(self, flags):
        if not cfg['use_microcode']:
            raise ValueError('microcode not enabled')

        addressfunc = cfg['microcode_encode']

        flagstates = [f.createstate() for f in flags]
        flagcombinations = [a + b for a, b in
                            product(*[(flag, -flag) for flag in flagstates])]

        for (index, stage), flag in product(enumerate(self.stages), flagcombinations):
            content = stage.getsignalsfromflag(flag)
            if not content:
                raise ValueError('Instruction: {}, Stage: {}, No matching signals for flags:{}'.format(
                    self, index, flag))

            addr = addressfunc(instruction=self.index,
                               stage=index,
                               flags=flag.encode())
            yield addr, content

    @staticmethod
    def parsestages(stages):
        def process_stage(stage):
            parts = []
            if type(stage) is list:
                parts.append(StagePart(flag_empty, stage))
            elif type(stage) is dict:
                if not cfg['microcode_branching']:
                    raise ValueError('Not configured to accept branching')
                for flag, signals in stage.items():
                    parts.append(StagePart(flag, signals))
            else:
                raise ValueError('')

            return Stage(parts)

        return [process_stage(s) for s in stages]


class Stage:
    def __init__(self, parts):
        self.parts = parts

    def getsignalsfromflag(self, flag):
        part = max((x for x in self.parts if x.matchesflags(flag)),
                   key=attrgetter('priority'), default=None)
        return part.data if part else None

    def getusedflags(self):
        return set((f for p in self.parts
                    for f in chain(p.flag.musthave, p.flag.mustnothave)))


def signalstoint(signals):
    result = 0
    for signal in signals:
        result |= (1 << signal)
    return result


class StagePart:
    def __init__(self, flag, data):
        self.flag, self.data = flag, signalstoint(data)
        self.priority = 0 if not flag else flag.priority

    def matchesflags(self, flag):
        return self.flag.compatible(flag)
