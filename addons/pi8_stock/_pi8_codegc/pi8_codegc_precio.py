# -*- coding: utf-8 -*-
from odoo import api, fields, models
from .._in_models.bs_model import cache_model_search

class pi8_codegc_precio(models.Model):
    _name = "pi8.codegc.precio"
    _description = 'Proporciona una conversión de clave a precio.'
    key = fields.Char(string='Clave', index=True, size=4, required=True)
    name = fields.Char(string='Nombre', index=True, size=18, required=True)
    value = fields.Float(string='Precio', index=True, required=True)
    # group = fields.Char(string='Grupo', index=True, size=1)
    _sql_constraints = [('key_unique', 'UNIQUE(key)', 'La clave debe ser única')]
    
    @cache_model_search
    def ckfield(self, key):
        pass
