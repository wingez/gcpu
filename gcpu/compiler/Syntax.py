
#the mnemonics used when programming
# i know its one syntax, many syntax but to differ form class Syntax
Syntaxes = []
SyntaxesByMnemonic={}




class Syntax(object):
    def __init__(self,mnemonic,instruction, args=[],priority=0):
        self.mnemonic=mnemonic
        self.args=args
        self.priority=priority
        self.instruction=instruction
        self.size=instruction.size

    def compile(self,args):
        argstocompilewith = [args[i] for i in range(len(args)) if 'fixvalue' not in self.args[i]]
        return self.instruction.compile(argstocompilewith)

    def matchesargs(self,args):

        def argvalidator(providedarg,syntaxarg):
            if type(providedarg) is syntaxarg['type']:
                if 'fixvalue' in syntaxarg and providedarg is not syntaxarg['fixvalue']:
                    return False
                return True
            return False
         
        if len(self.args) != len(args):
            return False
        if all(argvalidator(args[i],self.args[i]) for i in range(len(args))):
            return self
        return False

    def __str__(self):
        result='{}'.format(self.mnemonic)
        for arg in self.args:
            if 'fixvalue' in arg:
                result+=' {}'.format(str(arg['fixvalue']))
            else:
                if 'name' in arg:
                    result+=' <{}:{}>'.format(arg['name'],arg['type'].__name__)
                else:
                    result+=' <{}>'.format(arg['type'].__name__)
        return result


    
def Query(mnemonic,args):
    
    if mnemonic not in SyntaxesByMnemonic:
        return False
    for s in SyntaxesByMnemonic[mnemonic]:
        if s.matchesargs(args):
            return s
    return False



def CreateSyntax(mnemonic,args,instruction,priority=0):
    result=Syntax(mnemonic,instruction,args,priority)
    Syntaxes.append(result)

    if mnemonic not in SyntaxesByMnemonic:
        SyntaxesByMnemonic[mnemonic]=[]
    SyntaxesByMnemonic[mnemonic].append(result)

    return result
    
