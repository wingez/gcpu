from . import generator
from gcpu.microcode import core

from operator import attrgetter, itemgetter
from itertools import groupby


def generate() -> str:
    template = generator.gettemplate('instructions.html')

    cfg = core.cfg

    def process_group(group):
        def process_instr(instr):
            return {
                'name': instr.name,
                'index': instr.id,
                'syntaxes': instr.getsyntaxes(),
                'flags': map(attrgetter('name'), instr.getusedflags()),
                'description': instr.description,
            }

        return sorted([process_instr(i) for i in group], key=itemgetter('index'))

    instructions = core.instructions.copy()
    instructions.sort(key=attrgetter('group'))
    instrgroups = [(name, process_group(g)) for name, g in groupby(instructions, key=attrgetter('group'))]

    return template.render(config=cfg, instructiongroups=instrgroups)
