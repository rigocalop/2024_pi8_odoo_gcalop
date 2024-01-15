# -*- coding: utf-8 -*-
import logging
from ._in_common import _sx
from ._in_common import _sy
from ._in_common.zlogger import ZLogger
from ._in_common import zlogger as zlog

# Configura ZLogger como la clase de logger
ZLogger.configure_logger()
logging.setLoggerClass(ZLogger)

# zlog = ZLogger
logger = logging.getLogger("testLogger")

class sy:
    codegc =  _sy.sy_CodeGC

class sx:
    base16 = _sx.sx_Base16Converter
    base36 = _sx.sx_Base36Converter
    base62 = _sx.sx_Base62Converter
