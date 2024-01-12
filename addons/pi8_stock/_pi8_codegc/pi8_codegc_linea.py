# -*- coding: utf-8 -*-
from odoo import api, fields, models
import json
class pi8_codegc_linea(models.Model):
    _name = "pi8.codegc.linea"
    _description = 'Es un catálogo de lineas de 2 digitos.'
    key = fields.Char(string='Clave', index=True, size=4, required=True,)
    name = fields.Char(string='Nombre', index=True, size=100, required=True)
    depto = fields.Integer(string='Depto', index=True, size=1, required=True)
    tracking = fields.Selection([('none', 'Sin seguimiento'), ('lot', 'Por lotes'), ('serial', 'Por número de serie')], string='Seguimiento', required=True, default='none')
    _sql_constraints = [('key_unique', 'UNIQUE(key)', 'La clave debe ser única')]
    
    @api.model
    def ckfield(self, key, field_name=None):
        return self.env['bs.model'].ckfield(self, key, field_name)       


    @api.model
    def get_json_by_id(self, record_id):
        record = self.browse(record_id)
        if record.exists():
            record_data = {
                'id': record.id,
                'key': record.key,
                'name': record.name,
                'depto': record.depto
            }
            return json.dumps(record_data)
        else:
            return json.dumps({'error': 'Registro no encontrado'})