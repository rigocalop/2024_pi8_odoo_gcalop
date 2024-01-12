from odoo.tests.common import TransactionCase
from odoo.tests import HttpCase, tagged
import json
from .._in_common.zlogger import ZLogger, logger_test_handler
_logger = ZLogger.get_logger()


@tagged('-at_install', 'post_install')
class test_in_stock_pi8_codegc_moves(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(test_in_stock_pi8_codegc_moves, cls).setUpClass()
    
    @logger_test_handler
    def test_indev(self):
        # 0A12233$a23456789z
        InStockPi8Codegc = self.env['in.stock.pi8.codegc']
        codigo = "A10101"
        serial = InStockPi8Codegc.generate_serial(codigo,5)
        validar = InStockPi8Codegc.validar_serial(codigo, serial)
    
    @logger_test_handler
    def test_superfunc_codegc_moves__from_text_codes(self):
        # Prueba con códigos de texto válidos
        text_codes = 'NA2244$32*2,A02244$32DE*2'  # reemplaza con códigos válidos
        
        _logger.warning('test_generate_codes_list_from_text')
        self.env['in.stock.pi8.codegc.moves'].superfunc_codegc_moves__from_text_codes(text_codes)
        
@tagged('-at_install', 'post_install')
class test_in_stock_pi8_codegc_moves_controller(HttpCase):
    
    @logger_test_handler
    def test_superapi_codegc_moves__from_text_codes(self):
        # Preparar datos de prueba
        InStockPi8Codegc = self.env['in.stock.pi8.codegc']
        codigo = 'A11233'
        codigo2 = 'A11234'
        serial = InStockPi8Codegc.generate_serial(codigo,10)
        text_codes = f'{codigo}${serial},{codigo2}${serial}'
        
        self.authenticate('admin', 'admin')
        data = json.dumps({'text_codes': text_codes})

        # Configurar los encabezados para indicar que estás enviando datos JSON
        headers = {
            'Content-Type': 'application/json',
        }

        # Realizar una solicitud POST al endpoint de la API
        
        response = self.url_open('/api/codegc/moves?hola=hola', data=data, headers=headers, timeout=60)        