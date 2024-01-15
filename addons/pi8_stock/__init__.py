# -*- coding: utf-8 -*-
from . import _in_common    # importamos el paquete _in_common
from . import _in_models    # importamos el paquete _in_models
from . import _pi8_codegc    # importamos el paquete _pi8_codegc
from . import components    # importamos el paquete components

from .components.product_codegc_create_wizard import codegc_product_create_wizard
from .components.product_barcode_quickadd_wizard import product_barcode_quickadd_wizard
from .components.product_barcode_quickadd_wizard import product_barcode_quickadd_wizard__extend_stock__picking

import logging
from ._in_common.zlogger import ZLogger
# ZLogger.configure_logger()
# logging.setLoggerClass(ZLogger)

# import logging
# from .._in_common.zlogger import ZLogger, logger_api_handler, logger_function_handler, logger_superfunc_handler, logger_prms
# _logger = logging.getLogger("testLogger")