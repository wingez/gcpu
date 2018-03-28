from gcpu.microcode import *

# addresbuilder = bitbuilder(8, 5, 2)
# 
# 
# def encodeaddress(**kwargs):
#     return addresbuilder(kwargs['instruction'], kwargs['stage'], kwargs['flags'])


config(
    use_microcode=True,
    microcode_default=Signal(1, 'undefined microcode error'),
    microcode_branching=True,
    microcode_encode=bitbuilder(('instruction', 8), ('stage', 5), ('flags', 2)),
    microcode_size=2 ** 15,
    instruction_ids=256,
    recursion=True,
    program_size=2 ** 15,
    memsegments=True,
)

PTR = CreateConstant()
CST = CreateConstant()

halt = Signal(0, 'halt')

pccount = Signal(2, 'increment program counter')
immwrite = Signal(3, 'loads value into imm-register')

reset = Signal(5, 'reset stage counter')

loadinstr = Signal(7, 'move imm to instr')

wmux8 = Signal(24, 'wmux8')
wmux4 = Signal(26, 'wmux4')
wmux2 = Signal(28, 'wmux2')
wmux1 = Signal(30, 'wmux1')
rmux8 = Signal(28, 'rmux8')
rmux4 = Signal(27, 'rmux4')
rmux2 = Signal(29, 'rmux2')
rmux1 = Signal(31, 'rmux1')

w = SignalMultiplexer(wmux1 + wmux2 + wmux4 + wmux8)
r = SignalMultiplexer(rmux1 + rmux2 + rmux4 + rmux8)

PCh = CreateRegister(15, 'PCh', r(15), w(15))
PCl = CreateRegister(14, 'PCh', r(14), w(14))
STh = CreateRegister(13, 'STh', r(13), w(13))
STl = CreateRegister(12, 'STh', r(12), w(12))
FPh = CreateRegister(11, 'FPh', r(11), w(11))
FPl = CreateRegister(10, 'FPh', r(10), w(10))

MARl = Signal(0, 'mar-l')
MARh = Signal(0, 'mar-h')
RAMr = Signal(0, 'ram-read')

fetchstandard = immwrite + loadinstr + reset + pccount

# MARh 9
# MARl 8

ovf = CreateFlag('overflow', 0)
zero = CreateFlag('zero', 1)
fill = flag_empty

del w, r
CreateInstruction('noop', index=0, group='timing',
                  desc='fetches next instruction, this instruction gets executed before main program starts',
                  stages=[
                      fetchstandard
                  ])

CreateInstruction('test', index=1, desc='the official instruction made for testing new instruction',
                  stages=[
                      [8, 10, 12, 14],
                      {ovf + zero: [9, 15], ovf + -zero: [9, 13], fill: [9]},
                      fetchstandard
                  ]).addsyntax('test2')

CreateInstruction('halt', index=255,
                  stages=[halt])

CreateInstruction('loada val', mnemonic='loada', index=2, group='registers', desc='',
                  stages=[
                      fetchstandard
                  ],
                  args=[Argument(int, 'value')],
                  compilefunc=lambda value: [value]
                  )
CreateInstruction('loada ptr', mnemonic='loada', group='registers',
                  stages=[
                      fetchstandard
                  ],
                  args=[Argument(Pointer, 'address')],
                  compilefunc=lambda p: (nbyte(p.address, 1), nbyte(p.address, 2))
                  )

CreateInstruction('call', index=3, desc='',
                  stages=[
                      fetchstandard
                  ],
                  args=[Argument(Pointer, 'function')],
                  compilefunc=lambda p: (nbyte(p.address, 1), nbyte(p.address, 2))
                  )

# for index, register in enumerate((A,B,C)):
#    CreateInstruction('int',
#        group='initialization',
#        desc='writes <value> to register ' + register.name,
#        stages=[
#            PC.read+MAR.write,
#            RAM.read+register.write+pccount,
#            PC.read+MAR.write,
#            RAM.read+IMM.write+loadinstruction+resetstage+pccount,
#            {'ovf':RAM.read,'fill':[]}
#            #TODO this iw likely wrong
#            ],
#        args=[{'type':Register,'fixvalue':register},{'type':int,'name':'value'}],
#        compilefunc=lambda value:[value])

# CreateInstruction('disp',group='display',
#                  stages=[
#                      PC.read+MAR.write,
#                      RAM.read+IMM.write+pccount
#                      #TODO: do actual shit

#                        ],
#                  args=[{'type':Register}],
#                  compilefunc= lambda register:[register.compileread]
#                  )
# CreateInstruction('disp',group='display',
#                  stages=[
#                        PC.read+MAR.write
#                        #TODO: do actual shit
#                        ],
#                  args=[{'type':int}],
#                  compilefunc=lambda value:[value])
