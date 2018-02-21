from .generator import gettemplate
from gcpu.microcode import core

from operator import attrgetter
from itertools import groupby


def generate() -> str:
    template = gettemplate('instructions.html')

    cfg = core.cfg

    def process_group(group):
        def process_instr(instr):
            return {
                'name': instr.name,
                'index': instr.id,
                'syntaxes': instr.getsyntaxes(),
                'flags': instr.getusedflags(),
                'description': instr.description,
            }

        return [process_instr(i) for i in group]

    instructions = core.instructions.copy()
    instructions.sort(key=attrgetter('group'))
    instrgroups = dict(((name, process_group(g) for name, g in groupby(instructions, key=attrgetter('group')))))

    return template.render(config=cfg, instructiongroups=instrgroups)
