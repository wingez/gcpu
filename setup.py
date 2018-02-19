from setuptools import setup, find_packages
import re


def getversion():
    VERSIONFILE = 'gcpu/_version.py'
    verstrline = open(VERSIONFILE, 'rt').read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {}'.format(VERSIONFILE))


setup(
    name='gcpu',
    version=getversion(),
    description='',
    url='',
    author_email='gustav.ledous@gmail.com',
    license='MIT',
    include_package_data=True,
    py_modules=['gcpu.main'],
    install_requires=[
        'Click',
        'Jinja2',
        'Markdown',
    ],
    entry_points='''
        [console_scripts]
        gcpu=gcpu.main:cli
    ''',
    zip_safe=False,
)
