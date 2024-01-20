from odoo import models, fields, api
from odoo.exceptions import UserError
from ..pi8 import zlog, sx, sy, hlog
from collections import defaultdict

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

    def call_process_text_codes_with_picking(self):
        self.process_text_codes_with_picking(self.text_codes, self.stock_picking_id.id)
    
    @api.model
    def process_text_codes_with_picking(self, text_codes, picking_id):
        """
        Procesa text_codes y crea movimientos de stock asociados con el picking_id dado.
        :param text_codes: Lista de códigos de texto a procesar.
        :param picking_id: ID del picking con el que se asocian los movimientos de stock.
        :return: Estadísticas del procesamiento.
        """
        # Convertir los códigos de texto y procesarlos
        codegc_moves, invalid_codes, stats = self.env['in.stock.pi8.codegc.moves'].superfunc_codegc_moves__from_text_codes(text_codes, "product_id,lot_id,product_uom_qty,product_uom,name,lot_name")
        if invalid_codes:
            raise UserError(f"Códigos inválidos encontrados: {', '.join(invalid_codes)}")

        # Agrupar los elementos por product_id y sumar product_uom_qty
        product_groups = defaultdict(lambda: {'product_uom_qty': 0, 'items': []})
        for item in codegc_moves:
            product_groups[item['product_id']]['product_uom_qty'] += item['product_uom_qty']
            product_groups[item['product_id']]['items'].append(item)
        
        # Sort items within each product group by 'lot_name' in ascending order
        for group_data in product_groups.values():
            group_data['items'] = sorted(group_data['items'], key=lambda x: x.get('lot_name', ''))

        # Crear movimientos de stock para cada grupo de productos
        picking = self.env['stock.picking'].browse(picking_id)
        for product_id, group_data in product_groups.items():
            stock_move_data = {
                'picking_id': picking_id,
                'product_id': product_id,
                'product_uom_qty': group_data['product_uom_qty'],
                'name': 'Stock Move for product {}'.format(product_id),
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id
            }
            stock_move = self.env['stock.move'].create(stock_move_data)

            # Crear líneas de stock move para cada item en el grupo
            for item in group_data['items']:
                stock_move_line_data = sx.model.object_clone(item, ['product_id', 'lot_id', 'lot_name','product_uom_qty:quantity_product_uom','product_uom_qty:quantity','product_uom:product_uom_id'], 
                    {
                        'move_id': stock_move.id, 
                        'picking_id': picking_id,
                        'location_id': picking.location_id.id,
                        'location_dest_id': picking.location_dest_id.id
                    })
                self.env['stock.move.line'].create(stock_move_line_data)

        return stats

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
