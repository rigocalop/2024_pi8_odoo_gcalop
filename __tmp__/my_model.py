from odoo import models, api
import logging

# Crea un logger para tu clase o módulo
_logger = logging.getLogger(__name__)

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'Modelo de Ejemplo'

    def hello_world(self):
        # Agrega un mensaje de log
        _logger.info('\033[92mTestHelloWorld: setUp\033[0m')
        _logger.info('Por aquí pasó: método hello_world')
        return "Hola Mundo"