from .context import Context


class DefContext(Context):
    starttext = '#def '

    def __init__(self, parent, statement: str):
        super().__init__(parent)

        tmp = statement.partition('=')
        key = tmp[0].strip()
        s = tmp[2].strip()
        result = self.scope.evaluate(s)

        self.end(key, result)
