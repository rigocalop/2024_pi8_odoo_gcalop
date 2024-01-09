# -*- coding: utf-8 -*-
from odoo import api, fields, models

class pi8_codegc_precio(models.Model):
    _name = "pi8.codegc.precio"
    _description = 'Proporciona una conversión de clave a precio.'
    key = fields.Char(string='Clave', index=True, size=3, required=True)
    name = fields.Char(string='Nombre', index=True, size=18, required=True)
    value = fields.Integer(string='Precio', index=True, required=True)
    _sql_constraints = [('key_unique', 'UNIQUE(key)', 'La clave debe ser única')]
    
    @api.model
    def ckfield(self, key, field_name=None):
        return self.env['bs.model'].ckfield(self, key, field_name)    
