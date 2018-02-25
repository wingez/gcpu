cfg = {
    'use_microcode': False,
    'microcode_default': [],
    'microcode_branching': False,
    'microcode_pass_index': False,
    'microcode_encode': lambda kwargs: kwargs.get('instruction'),
    'microcode_size': 256,
    'instruction_ids': 256,
    'recursion': True,
    'program_size': 256,
    'memsegments': False,
}
