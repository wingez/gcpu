from . import generator
from gcpu.microcode import core

from operator import attrgetter, itemgetter
from itertools import groupby


def generate() -> str:
    template = generator.gettemplate('instructions.html')

    cfg = core.cfg

    def process_instruction(instr):
        return {
            'name': instr.name,
            'index': instr.id,
            'group': instr.group,
            'syntaxes': instr.getsyntaxes(),
            'flags': map(attrgetter('name'), instr.getusedflags()),
            'description': instr.description,
        }

    instructions = [process_instruction(i) for i in core.instructions]
    registers = core.registers
    flags = core.flags

    return template.render(
        config=cfg,
        instructions=instructions,
        registers=registers,
        flags=core.getflags(),
    )
