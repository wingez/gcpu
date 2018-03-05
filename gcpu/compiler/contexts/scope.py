class Scope:

    def __init__(self):
        self._items = {}

    def __contains__(self, item):
        return item in self._items

    def __getitem__(self, item):
        return self._items[item]

    def get(self, item, default=None):
        return self._items.get(item, default)

    def __setitem__(self, key, value):
        self._items[key] = value

    def update(self, items):
        self._items.update(items)

    def items(self):
        return self._items.items()

    def copy(self):
        result = Scope()
        result._items = self._items.copy()
        return result

    def evalalutate(self, statement):
        return eval(statement, None, self._items)


inherit = 1
extend = 2
new = 3
