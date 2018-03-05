from .context import Context


class DefContext(Context):
    starttext = '#def '

    def __init__(self, parent, statement: str):
        super().__init__(parent)

        tmp = statement.partition('=')
        key = tmp[0].strip()
        result = self.scope.evalalutate(tmp[2].strip())

        self.end(key, result)
