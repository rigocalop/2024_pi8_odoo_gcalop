# -*- coding: utf-8 -*-
from odoo import api, fields, models

class pi8_codegc_precio(models.Model):
    _name = "pi8.codegc.precio"
    _description = 'Proporciona una conversión de clave a precio.'
    key = fields.Char(string='Clave', index=True, size=4, required=True)
    name = fields.Char(string='Nombre', index=True, size=18, required=True)
    value = fields.Float(string='Precio', index=True, required=True)
    # group = fields.Char(string='Grupo', index=True, size=1)
    _sql_constraints = [('key_unique', 'UNIQUE(key)', 'La clave debe ser única')]
    
    @api.model
    def ckfield(self, key, field_name=None):
        return self.env['bs.model'].ckfield(self, key, field_name)    
    
    @api.model
    def find_key_by_group_and_value(self, group, value):
        # Buscar un registro que coincida con el grupo y el valor dados
        # record = self.search([('group', '=', group), ('value', '=', value)], limit=1)
        return '0P11'
        return record.key if record else None