# -*- coding: utf-8 -*-
import logging

from ._in_common._sx import lib_sx as sx
from ._in_common._sy import lib_sy as sy
from ._in_common.zlogger import ZLogger
from ._in_common import zlogger as zlog
from ._in_common import zlogger_handlers as hlog

# Configura ZLogger como la clase de logger
ZLogger.configure_logger()
logging.setLoggerClass(ZLogger)
logger = logging.getLogger("testLogger")
