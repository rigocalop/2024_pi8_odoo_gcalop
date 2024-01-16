from odoo.tests.common import TransactionCase
from odoo.tests import HttpCase, tagged
import json
from ..pi8 import zlog, sy, sx, hlog





@tagged('-at_install', 'post_install')
class test_in_stock_pi8_codegc_moves(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(test_in_stock_pi8_codegc_moves, cls).setUpClass()
    
    @hlog.hlog_test
    def test_indev(self):
        # 0A12233$a23456789z
        InStockPi8Codegc = self.env['in.stock.pi8.codegc']
        codigo = "A10101"
        serial =  sy.codegc.generate_serial(codigo, 10)
        validar = sy.codegc.validate_serial(codigo, serial)
    
    @hlog.hlog_test
    def test_superfunc_codegc_moves__from_text_codes(self):
        # Prueba con códigos de texto válidos
        text_codes = 'NA2244$32*2,A02244$32DE*2'  # reemplaza con códigos válidos
        zlog.warning('test_generate_codes_list_from_text')
        self.env['in.stock.pi8.codegc.moves'].superfunc_codegc_moves__from_text_codes(text_codes)
        

@tagged('-at_install', 'post_install')
class test_in_stock_pi8_codegc_moves_controller(HttpCase):
    @hlog.hlog_test_api(resalt=False, auth_user='admin',auth_password='admin')
    def test_superapi_codegc_moves__from_text_codes(self):
        # Preparar datos de prueba
        InStockPi8Codegc = self.env['in.stock.pi8.codegc']
        codigo = '0A112333'
        codigo2 = '0A11234X'
        serial =  sy.codegc.generate_serial(codigo, 10)
        text_codes = f'{codigo}${serial},{codigo2}${serial}'
        data = json.dumps({'text_codes': text_codes})
        response = self.url_open('/api/codegc/moves?hola=hola', data=data, headers=self.headers, timeout=60)        
        
        
    @hlog.hlog_test_api(resalt=False, auth_user='admin',auth_password='admin')
    def test_superapi_stock_pi8_codegc_GET(self):
        codigo = '0A11233'
        response = self.url_open(f'/api/codegc/{codigo}', headers=self.headers, timeout=60)              