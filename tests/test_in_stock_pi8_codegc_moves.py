from odoo.tests.common import TransactionCase
from odoo.tests import HttpCase, tagged

from .._in_common.zlogger import ZLogger
_logger = ZLogger.get_logger()


@tagged('-at_install', 'post_install')
class test_in_stock_pi8_codegc_moves(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(test_in_stock_pi8_codegc_moves, cls).setUpClass()

    def test_generate_codegc_moves__from_text_codes(self):
        # Prueba con códigos de texto válidos
        text_codes = 'NA2244$32*2,A02244$32DE*2'  # reemplaza con códigos válidos
        _logger.tini(__name__)
        _logger.warning('test_generate_codes_list_from_text')
        self.env['in.stock.pi8.codegc.moves'].generate_codegc_moves__from_text_codes(text_codes)
        _logger.tend(__name__)