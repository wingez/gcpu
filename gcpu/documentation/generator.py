from jinja2 import Environment, PackageLoader, select_autoescape
import itertools
import markdown
import os

from . import configgenerator

env = Environment(
    loader=PackageLoader('gcpu', 'documentation/templates'),
    autoescape=select_autoescape(['html'])
)

gettemplate = env.get_template


def getmarkdown(filename):
    path = os.path.join('gcpu', 'documentation', 'texts', filename)
    with open(path, 'r') as file:
        return markdown.markdown(file.read(), extensions=['markdown.extensions.tables'])


def instructions():
    with open('output/doc.html', 'w') as file:
        file.write(configgenerator.generate())
   