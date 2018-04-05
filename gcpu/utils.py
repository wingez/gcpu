def static_variables(**kwargs):
    def decorate(func):
        for k, v in kwargs.items():
            setattr(func, k, v)
        return func

    return decorate


@static_variables(verbose=False)
def printverbose(message):
    if printverbose.verbose:
        print(message)
