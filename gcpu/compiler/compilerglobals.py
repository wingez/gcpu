from gcpu.utils import printverbose

globaldict = {}


def dump():
    printverbose('dumping global values:')
    for i in globaldict.items():
        printverbose('{}: {}', *i)
    printverbose()

def getglobals():
    return globaldict


def globals(defaultname=''):
    def decorator(obj):
        name = defaultname
        if not name:
            if hasattr(obj, '__name__'):
                name = getattr(obj, '__name__')
        if not name:
            raise ValueError('no valid name provided')

        if name in globaldict:
            raise ValueError('a global with name {} is already provided'.format(name))
        globaldict[name] = obj
        return obj

    return decorator
