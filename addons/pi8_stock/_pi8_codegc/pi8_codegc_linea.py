# -*- coding: utf-8 -*-
from odoo import api, fields, models
import json
from .._in_models.bs_model import cache_model_search
class pi8_codegc_linea(models.Model):
    _name = "pi8.codegc.linea"
    _description = 'Es un catálogo de lineas de 2 digitos.'
    key = fields.Char(string='Clave', index=True, size=4, required=True,)
    name = fields.Char(string='Nombre', index=True, size=100, required=True)
    depto = fields.Integer(string='Depto', index=True, size=1, required=True)
    tracking = fields.Selection([('none', 'Sin seguimiento'), ('lot', 'Por lotes'), ('serial', 'Por número de serie')], string='Seguimiento', required=True, default='none')
    _sql_constraints = [('key_unique', 'UNIQUE(key)', 'La clave debe ser única')]
    

    @cache_model_search
    def ckfield(self, key):
        pass