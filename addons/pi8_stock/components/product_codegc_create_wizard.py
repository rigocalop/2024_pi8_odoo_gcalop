# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError
import logging
import re
import json
from ..pi8 import zlog, sx, sy, hlog

_logger = logging.getLogger(__name__)
class codegc_product_create_wizard(models.TransientModel):
    _name = "pi8.stock.codegc.product.create.wizard"
    _description = 'Create_CodeGC_Wizard'
    codes = fields.Text(string='Codes')
    
    # pesque errores y los precese por default,
    # evalue el tiempo de ejeciciòn.
    def call_superfunc_codegc_moves__from_list_text_codes(self):
        # Verificar si self.codes es un string con formato de array JSON
        try:
            list_text_codes = sx.list.convert(self.codes)
        except Exception:
            raise UserError('El formato de los códigos no es válido.')
            
        entries_valid, entries_invalid, stats = self.env['in.stock.pi8.codegc.moves'].superfunc_codegc_moves__from_list_text_codes(list_text_codes)
        if len(entries_invalid) > 0:
            cadena_de_entradas_invalidas = ', '.join(str(item) for item in entries_invalid)
            raise UserError(cadena_de_entradas_invalidas)
        elif len(entries_valid) > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Productos Creados'),
                    'message': _('Se crearon los productos exitosamente.'),
                    'type': 'success',  # tipos: 'success', 'warning', 'danger'...
                }
            }
            
        # decorador de funciones
        # def ensure_pssroducts_exist_from_text_codes(self):
        #     # Verificar si self.codes es un string con formato de array JSON
        #     entries_valid, entries_invalid, stats = self.env['in.stock.pi8.codegc.moves'].superfunc_codegc_moves__from_list_text_codes(sx.list.convert(self.codes))
        #     if len(entries_invalid) > 0: 
        #         raise UserError("Los siguientes códigos no son válidos: " + ', '.join(str(item) for item in entries_invalid))
        #     elif len(entries_valid) > 0: 
        #         message = "Se crearon los siguientes productos: " + ', '.join(str(item) for item in entries_valid)  
                
