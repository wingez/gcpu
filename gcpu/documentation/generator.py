from jinja2 import Environment, PackageLoader, select_autoescape
import itertools
import markdown
import os

env = Environment(
    loader=PackageLoader('gcpu', 'documentation/templates'),
    autoescape=select_autoescape(['html'])
)


def getmarkdown(filename):
    path = os.path.join('gcpu', 'documentation', 'texts', filename)
    with open(path, 'r') as file:
        return markdown.markdown(file.read(), extensions=['markdown.extensions.tables'])


def render_instructions():
    template = env.get_template('instructions.html')
    from gcpu.microcode import core, syntax

    instructions = sorted(core.instructions.copy(), key=lambda i: i.group)

    groups = []
    for k, g in itertools.groupby(instructions, lambda i: i.group):
        b = list(g)
        result = {'name': k, 'count': len(b), 'instructions': []}

        for i in b:
            s = next((x for x in syntax.syntaxes if x.instruction is i), None)
            result['instructions'].append({'name': s.mnemonic, 'index': i.id, 'syntax': s, 'desc': i.description})
        groups.append(result)
    print(template.render(groups=groups))

    print(getmarkdown('include.md'))
    print(getmarkdown('operations.md'))
