# the mnemonics used when programming
# i know its one syntax, many syntax but to differ form class Syntax
syntaxes = []
syntaxesByMnemonic = {}


def create(mnemonic, args, instruction, priority=0):
    result = Syntax(mnemonic, instruction, args, priority)
    syntaxes.append(result)

    if mnemonic not in syntaxesByMnemonic:
        syntaxesByMnemonic[mnemonic] = []
    syntaxesByMnemonic[mnemonic].append(result)

    return result


def query(mnemonic, args):
    if mnemonic not in syntaxesByMnemonic:
        return False
    for s in syntaxesByMnemonic[mnemonic]:
        if s.matchesargs(args):
            return s
    return False


def printall():
    print('printing syntaxes')
    for s in syntaxes:
        print(s.__str__())
    print()


class Syntax(object):

    def __init__(self, mnemonic, instruction, args=(), priority=0):
        self.mnemonic = mnemonic
        self.args = args
        self.priority = priority
        self.instruction = instruction
        self.size = instruction.size

    def compile(self, args):
        argstocompilewith = [arg for arg, s in zip(args, self.args) if s.include]
        return self.instruction.compile(argstocompilewith)

    def matchesargs(self, args):
        if len(self.args) != len(args):
            return False

        return all([a == b for a, b in zip(args, self.args)])

    def __str__(self):
        result = ['{}, {}'.format(self.instruction.id, self.mnemonic)]
        result += [str(arg) for arg in self.args]
        return ' '.join(result)


class Argument:

    def __init__(self, arg, name='', include=True):
        self.name = name
        self.isgeneric = type(arg) is type
        self.arg = arg
        self.include = include

    def __eq__(self, other):
        if self.isgeneric:
            return type(other) is self.arg
        else:
            return other == self.arg

    def __str__(self):
        if not self.isgeneric:
            return str(self.arg)
        if self.name:
            return '<{}:{}>'.format(self.name, self.arg.__name__)
        return '<{}>'.format(self.arg.__name__)
