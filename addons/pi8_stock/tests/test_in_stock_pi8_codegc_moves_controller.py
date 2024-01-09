from odoo.tests.common import TransactionCase
from odoo.tests import HttpCase, tagged
import json
from .._in_common.zlogger import ZLogger
_logger = ZLogger.get_logger()

@tagged('-at_install', 'post_install')
class test_in_stock_pi8_codegc_moves_controller(HttpCase):

    def test_api_codegc_moves(self):
        # Preparar datos de prueba
        text_codes = 'NA2244$32*2,A02244$32DE*2'  # reemplaza con códigos válidos
        _logger.tini(__name__,text_codes=text_codes)

        self.authenticate('admin', 'admin')
        data = json.dumps({'text_codes': text_codes})

        # Configurar los encabezados para indicar que estás enviando datos JSON
        headers = {
            'Content-Type': 'application/json',
        }

        # Realizar una solicitud POST al endpoint de la API
        
        response = self.url_open('/api/codegc/moves', data=data, headers=headers, timeout=60)
        _logger.tend(__name__,response=response)
        # Comprobar si la respuesta es correcta
        # self.assertTrue(response.status_code, 200)
        # Convertir la respuesta a JSON y verificar el contenido
        # response_json = response.json()
        # if 'error' in response_json:
        #     self.fail(f"Error recibido del servidor: {response_json['error']}")
        # else:
        #     self.assertIn('resultado_esperado', response_json)
        # self.assertIn('resultado_esperado', response.text)