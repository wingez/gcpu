
defsymbols = '#def '


def isdefstatement(statement: str):
    return statement.startswith(defsymbols)


def defstatement(statement: str, vars: dict, trim=True):
    if trim:
        statement = statement.partition(defsymbols)[2]

    tmp = statement.partition(' = ')
    id = tmp[0].strip()
    raw = tmp[2].strip()
    result = eval(raw, locals=vars)

    return id, result
