# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError
import logging
from ..pi8 import zlog, sx, sy, hlog, sz

_logger = logging.getLogger(__name__)
class codegc_product_create_wizard(models.TransientModel):
    _name = "pi8.stock.codegc.product.create.wizard"
    _description = 'Create_CodeGC_Wizard'
    codes = fields.Text(string='Codes')
    
    # pesque errores y los precese por default,
    def call_superfunc_codegc_moves__from_list_text_codes(self):
        # Verificar si self.codes es un string con formato de array JSON
        try:
            list_text_codes = sx.XList._clean_textcodes(self.codes)
            list_text_codes = sx.XList.convert(list_text_codes)
        except Exception:
            raise UserError('El formato de los códigos no es válido.')
        
        isvalid, data = sz.Odoo_CodegcLot.Ensure(env=self.env,textcodes=list_text_codes, return_entries=True)
        
        if not isvalid:
            raise UserError(isvalid)
        elif isvalid:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Productos Creados'),
                    'message': _('Se crearon los productos exitosamente.'),
                    'type': 'success',  # tipos: 'success', 'warning', 'danger'...
                }
            }
            

