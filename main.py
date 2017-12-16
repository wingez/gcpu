
import sys
from gcpu import bithelper
from gcpu.microcode import core 

def compilefile(args):
    pass


def microcode(args):
    name = args[0]
    core.loadinstructions(name)
   











if __name__=='__main__':

    action = sys.argv[1]
    args = sys.argv[2:]

    if action=='compile':
        compilefile(args)
    elif action=='microcode':
        microcode(args)



    
















    





