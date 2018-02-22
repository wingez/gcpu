from .signal import Signal
from .signalmultiplexer import SignalMultiplexer
from .core import config, CreateFlag, CreateInstruction, CreateRegister, config
from .constant import Constant, CreateConstant
from .syntax import Argument
from .flags import flag_empty

from ..bithelper import *

from gcpu.compiler.pointer import Pointer