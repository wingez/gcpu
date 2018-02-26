from .context import Context


class DefContext(Context):
    starttext = '#def '

    def __init__(self, parent, statement: str):
        super().__init__(parent)

        tmp = statement.partition('=')
        id = tmp[0].strip()
        result = eval(tmp[2].strip(), None, parent.scope)

        self.end(id, result)
