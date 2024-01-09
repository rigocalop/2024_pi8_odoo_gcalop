from odoo import models, fields, api
from odoo.exceptions import UserError
import re
import odoo

class product_barcode_quickadd_wizard(models.TransientModel):
    _name = 'pi8.stock.product.barcode.quickadd.wizard'

    _description = 'Asistente para Agregar Productos por Código de Barras'

    text_codes = fields.Text(string="Códigos en Texto")
    stock_picking_id = fields.Many2one('stock.picking', string='Traslado Interno')

    @api.model
    def default_get(self, fields_list):
        res = super(product_barcode_quickadd_wizard, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            res['stock_picking_id'] = active_id
        return res

    def add_stock_moves_to_picking_from_text(self):
        self.env['in.stock.picking'].add_stock_moves_to_picking_from_text(self.text_codes, self.stock_picking_id.id)
        
class product_barcode_quickadd_wizard__extend_stock__picking(models.Model):
    _inherit = 'stock.picking'
    def action_open_barcode_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Barcode Quick-Add',
            'res_model': 'pi8.stock.product.barcode.quickadd.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }        