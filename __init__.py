# -*- coding: utf-8 -*-
from ._in_common.sy_codes import sy_codes
from ._in_common.zlogger import ZLogger
from ._in_common.zlogger_formatter import ZLogger_CustomFormatter


from ._pi8_codegc.pi8_codegc_linea import pi8_codegc_linea
from ._pi8_codegc.pi8_codegc_precio import pi8_codegc_precio
from ._pi8_codegc.pi8_codegc_temporada import pi8_codegc_temporada

from ._pi8_codegc.pi8_codegc import pi8_codegc
from .components.product_codegc_create_wizard import codegc_product_create_wizard
from .components.product_barcode_quickadd_wizard import product_barcode_quickadd_wizard
from .components.product_barcode_quickadd_wizard import product_barcode_quickadd_wizard__extend_stock__picking

from ._in_models.bs_model import bs_model
from ._in_models.in_product import in_product
from ._in_models.in_stock_picking import in_stock_picking
from ._in_models.in_stock_move import in_stock_move
from ._in_models.in_stock_pi8_codegc import in_stock_pi8_codegc
from ._in_models.in_stock_pi8_codegc_moves import in_stock_pi8_codegc_moves
from ._in_models.in_stock_pi8_codegc_moves import in_stock_pi8_codegc_moves_controller
from .__tmp__.my_model  import MyModel
import logging

ZLogger.configure_logger()
# logging.setLoggerClass(ZLogger)
# logger = logging.getLogger("testLogger")
# logger.setLevel(logging.DEBUG)

#     # Establecer el formatter personalizado
# ch = logging.StreamHandler()
# ch.setFormatter(ZLogger_CustomFormatter())
# logger.addHandler(ch)