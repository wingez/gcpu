import sys
import traceback


class InterpreterError(Exception): pass


_myexec = exec


def exec(cmd, description='source string'):
    try:
        d = dict(locals(), **globals())
        c = compile(cmd, '<string>', 'exec')
        _myexec(c, d, d)
    except SyntaxError as err:
        error_class = err.__class__.__name__
        detail = err.args[0]
        line_number = err.lineno
    except Exception as err:
        error_class = err.__class__.__name__
        detail = err.args[0] if len(err.args) else ''
        cl, exc, tb = sys.exc_info()
        line_number = traceback.extract_tb(tb)[-1][1]
    else:
        return
    raise InterpreterError("%s at line %d of %s: %s" % (error_class, line_number, description, detail))
