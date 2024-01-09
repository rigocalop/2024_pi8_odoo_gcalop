from odoo import models, api
from odoo.tests.common import tagged, TransactionCase
import logging

# Crea un logger para tu clase o módulo
# _logger = logging.getLogger(__name__)
 
class TestHelloWorld(TransactionCase):
    def setUp(self):
        super(TestHelloWorld, self).setUp()
        self.my_model = self.env['my.model'].create({})

        # Agrega un mensaje de log en la configuración
        _logger.info('\033[91mTestHelloWorld: setUp\033[0m')

    @tagged('mi_tag')
    def test_hello_world(self):
        # Agrega un mensaje de log antes de la afirmación
        _logger.info('TestHelloWorld: test_hello_world iniciando')

        self.assertEqual(self.my_model.hello_world(), "Hola Mundo")

        # Agrega otro mensaje de log después de la afirmación
        _logger.info('TestHelloWorld: test_hello_world completado')
        
        
    @tagged('mi_tag2')
    def test_hello_world2(self):
        # Agrega un mensaje de log antes de la afirmación
        _logger.info('TestHelloWorld: test_hello_world2 iniciando')

        self.assertEqual(self.my_model.hello_world(), "Hola Mundo")

        # Agrega otro mensaje de log después de la afirmación
        _logger.info('TestHelloWorld: test_hello_world2 completado')
