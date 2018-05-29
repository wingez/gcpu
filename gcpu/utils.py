def static_variables(**kwargs):
    def decorate(func):
        for k, v in kwargs.items():
            setattr(func, k, v)
        return func

    return decorate


@static_variables(verbose=False)
def printverbose(message: str = '', *args, **kwargs):
    if printverbose.verbose:
        print(str(message).format(*args, **kwargs))


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()
