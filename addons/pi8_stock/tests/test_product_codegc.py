from odoo.tests.common import TransactionCase
import logging
_logger = logging.getLogger(__name__)

class test_product_codegc(TransactionCase):

    def setUp(self):
        super(test_product_codegc, self).setUp()
        self.my_model = self.env['pi8.codegc'].create({})

        # Agrega un mensaje de log en la configuración
        _logger.info('\033[91mTestHelloWorld: setUp\033[0m')
        # Configuración inicial (crear registros necesarios, etc.)

    def test_create_products_from_valid_text_codes(self):
        # Prueba con códigos de texto válidos
        text_codes = 'J12244'  # reemplaza con códigos válidos
        self.env['pi8.codegc'].create_products_from_text_codes(text_codes)
        # Afirmaciones para verificar el resultado esperado

    # def test_create_products_from_invalid_text_codes(self):
    #     # Prueba con códigos de texto inválidos
    #     text_codes = '...'  # reemplaza con códigos inválidos
    #     with self.assertRaises(UserError):
    #         self.env['pi8.codegc'].create_products_from_text_codes(text_codes)
    #     # Afirmaciones adicionales si son necesarias

# Puedes agregar más métodos de prueba según sea necesario
