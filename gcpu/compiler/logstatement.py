from gcpu.compiler.throwhelper import log

logsymbols = 'log '


def islogstatement(statement: str) -> bool:
    return statement.startswith(logsymbols)


def logstatement(statement: str, vars, comp):
    if not islogstatement(statement):
        return False
    statement = statement.partition(logsymbols)[2]
    result = str(eval(statement, None, vars))
    log('log file:{} line:{}  {}'.format(comp.name, comp.linenumber, result))

    return True
