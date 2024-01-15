# -*- coding: utf-8 -*-
from odoo import api, fields, models
from .._in_models.bs_model import cache_model_search

class pi8_codegc_temporada(models.Model):
    _name = "pi8.codegc.temporada"
    _description = 'Expresa la temporada de mes en 2 digitos.'
    key = fields.Char(string='Clave', index=True, size=4, required=True)
    name = fields.Char(string='Nombre', index=True, required=True)
    year = fields.Integer(string='Año', index=True, required=True)
    month = fields.Integer(string='Mes', index=True, required=True)
    _sql_constraints = [('key_unique', 'UNIQUE(key)', 'La clave debe ser única')]
    
    @cache_model_search
    def ckfield(self, key):
        pass
        
