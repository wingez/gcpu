
import sys


class CompileError(Exception):
    pass


lineNumber = None
file = ''
warningStream = sys.stdout
logStream = sys.stdout


def setlinenumber(n: int):
    global lineNumber
    lineNumber = n


def setfile(n: str):
    global file
    file = n


def throw(description: str, **location):
    if file:
        location['file'] = file
    if lineNumber is not None:
        location['linenumber'] = lineNumber

    raise CompileError(generateerrormessage(description, **location))


def warn(message):
    warningStream.write(message)
    warningStream.write('\n')


def generateerrormessage(errortype, desc, **location):
    loc = ', '.join(['{}:{}'.format(key, value) for key, value in location.items()])

    return '{}| {}: {}'.format(errortype, loc, desc)


def log(message):
    # TODO
    if logStream:
        logStream.write(message + '\n')
