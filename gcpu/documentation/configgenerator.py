from . import generator
from gcpu.microcode import core, syntax

from operator import attrgetter, itemgetter
from itertools import groupby


def generate() -> str:
    template = generator.gettemplate('instructions.html')

    cfg = core.cfg

    instructions = [InstructionView(i) for i in core.instructions]
    registers = core.registers
    flags = core.flags

    return template.render(
        config=cfg,
        instructions=instructions,
        registers=registers,
        flags=flags,
    )


class InstructionView:
    def __init__(self, instr):
        self.name, self.index, self.group, self.description = instr.name, instr.id, instr.group, instr.description
        self.syntaxes = [s for s in syntax.syntaxes if s.instruction is instr]
        self.flags = [f.name for f in instr.getusedflags()]
