# -*- coding: utf-8 -*-
import odoo, json
from odoo import http, api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request, Response
from werkzeug.exceptions import BadRequest, NotFound
from ..pi8 import zlog, logger, sx, sy, hlog


class in_stock_pi8_codegc_moves(models.AbstractModel):
    _name = 'in.stock.pi8.codegc.moves'
  
class in_stock_pi8_codegc_moves_controller(http.Controller):
    @http.route('/api/codegc/moves', type='http', methods=['POST'], auth='public', csrf=False)
    @hlog.hlog_api()
    def superapi_codegc_moves__from_text_codes(self, **kw):
        fields = kw.get('fields')
        data = json.loads(request.httprequest.data)
        textcodes = sx.xobject.tryget(data, 'text_codes')
        if textcodes: textcodes = sx.XList.ensure(textcodes)
        else: textcodes = sx.XList.ensure(data)        

        isvalid, entries, entries_invalid = sy.OdooCodeGC.EnsureCodeLot(env=request.env, textcodes=textcodes)
        
        # "product_id,lot_id,product_uom_qty,product_uom,name,lot_name")
        
    #                    'product_uom': product.uom_id.id,
    # # #                 'name': product.display_name,
        if isvalid:
            stock_moves = sx.XListDict.Select(listdict=entries, fields=["product_id","lot_id","lot_name","product_uom_qty"], mapping={"product_uom_qty": "qty", "lot_name":"lot"})
            stock_moves = sy.OdooCodeGC.joinCode_ModeID(env=request.env, target_list=stock_moves)
            logger.debug(f"entries: {entries}")
            

            # {'product_id': 421, 'lot_id': 5707, 'entry': '0A214584$1cQxKP404T', 'code': '0A214584', 'qty': 1.0, 'lot': '$1cQxKP404T', 'tracking': 'serial'},
            return { 'message': 'The products and corresponding lots have been created.', 'entries': entries } 
        else:
            return BadRequest({ 'error':  'Bad Request', 'message': 'Invalid entries found', 'entries': entries_invalid })
        
    
# # # # # # # #  @api.model
# # # # # # # #     def process_text_codes_with_picking(self, text_codes, picking_id):
# # # # # # # #         """
# # # # # # # #         Procesa text_codes y crea movimientos de stock asociados con el picking_id dado.
# # # # # # # #         :param text_codes: Lista de códigos de texto a procesar.
# # # # # # # #         :param picking_id: ID del picking con el que se asocian los movimientos de stock.
# # # # # # # #         :return: Estadísticas del procesamiento.
# # # # # # # #         """
# # # # # # # #         # Convertir los códigos de texto y procesarlos
# # # # # # # #         codegc_moves, invalid_codes, stats = self.env['in.stock.pi8.codegc.moves'].superfunc_codegc_moves__from_text_codes(text_codes, "product_id,lot_id,product_uom_qty,product_uom,name,lot_name")
# # # # # # # #         if invalid_codes:
# # # # # # # #             raise UserError(f"Códigos inválidos encontrados: {', '.join(invalid_codes)}")

# # # # # # # #         # Agrupar los elementos por product_id y sumar product_uom_qty
# # # # # # # #         product_groups = defaultdict(lambda: {'product_uom_qty': 0, 'items': []})
# # # # # # # #         for item in codegc_moves:
# # # # # # # #             product_groups[item['product_id']]['product_uom_qty'] += item['product_uom_qty']
# # # # # # # #             product_groups[item['product_id']]['items'].append(item)
        
# # # # # # # #         # Sort items within each product group by 'lot_name' in ascending order
# # # # # # # #         for group_data in product_groups.values():
# # # # # # # #             group_data['items'] = sorted(group_data['items'], key=lambda x: x.get('lot_name', ''))

# # # # # # # #         # Crear movimientos de stock para cada grupo de productos
# # # # # # # #         picking = self.env['stock.picking'].browse(picking_id)
# # # # # # # #         for product_id, group_data in product_groups.items():
# # # # # # # #             stock_move_data = {
# # # # # # # #                 'picking_id': picking_id,
# # # # # # # #                 'product_id': product_id,
# # # # # # # #                 'product_uom_qty': group_data['product_uom_qty'],
# # # # # # # #                 'name': 'Stock Move for product {}'.format(product_id),
# # # # # # # #                 'location_id': picking.location_id.id,
# # # # # # # #                 'location_dest_id': picking.location_dest_id.id
# # # # # # # #             }
# # # # # # # #             stock_move = self.env['stock.move'].create(stock_move_data)

# # # # # # # #             # Crear líneas de stock move para cada item en el grupo
# # # # # # # #             for item in group_data['items']:
# # # # # # # #                 stock_move_line_data = sx.model.object_clone(item, ['product_id', 'lot_id', 'lot_name','product_uom_qty:quantity_product_uom','product_uom_qty:quantity','product_uom:product_uom_id'], 
# # # # # # # #                     {
# # # # # # # #                         'move_id': stock_move.id, 
# # # # # # # #                         'picking_id': picking_id,
# # # # # # # #                         'location_id': picking.location_id.id,
# # # # # # # #                         'location_dest_id': picking.location_dest_id.id
# # # # # # # #                     })
# # # # # # # #                 self.env['stock.move.line'].create(stock_move_line_data)

# # # # # # # #         return stats
        


        # # codegc_moves, invalid_entries, stats = request.env['in.stock.pi8.codegc.moves'].superfunc_codegc_moves__from_list_text_codes(textcodes=list_text_codes, fields=fields)
        # if stats['entries_invalids'] > 0:
        #     return BadRequest({ 'error':  'Bad Request', 'message': 'Invalid entries found', 'stats': stats, 'invalid_entries': invalid_entries })
        # else:
        #     return { 'message': 'The products and corresponding lots have been created.', 'stats': stats, 'codegc_moves': codegc_moves }




 

    # def group_and_sort_stock_moves(self, stock_moves):
    #     """
    #     Agrupa y ordena los movimientos de stock por product_id.
    #     :param stock_moves: Lista de diccionarios que representan los movimientos de stock.
    #     :return: Lista de diccionarios representando los movimientos de stock agrupados y ordenados.
    #     """
    #     from collections import defaultdict

    #     # Crear un diccionario para acumular las cantidades por product_id
    #     grouped_moves = defaultdict(lambda: {'product_id': 0, 'product_uom_qty': 0, 'product_uom': None, 'name': ''})
        
    #     for move in stock_moves:
    #         product_id = move['product_id']
    #         grouped_moves[product_id]['product_id'] = product_id
    #         grouped_moves[product_id]['product_uom_qty'] += move['product_uom_qty']
    #         grouped_moves[product_id]['product_uom'] = move['product_uom']
    #         grouped_moves[product_id]['name'] = move['name']  # Podría ser el nombre del último producto encontrado

    #     # Convertir el diccionario en una lista y ordenar por product_id
    #     sorted_moves = sorted(grouped_moves.values(), key=lambda x: x['product_id'])
    #     return sorted_moves

    # # def generate_basic_stock_moves(self, codes_quantities, group_and_sort=False):
    # #     # Paso 2: Obtener los productos utilizando in.product
    # #     in_product_model = self.env['in.product']
    # #     barcodes = [code for code, _ in codes_quantities]
    # #     products_by_barcode, not_found_barcodes = in_product_model.get_products_by_barcode(barcodes)

    # #     # Verificar si hay productos no encontrados
    # #     if not_found_barcodes:
    # #         raise UserError(f"Códigos de producto no encontrados: {', '.join(not_found_barcodes)}")

    # #     # Preparar los movimientos de stock solo con la información básica del producto
    # #     stock_moves = []
    # #     for barcode, qty in codes_quantities:
    # #         product = products_by_barcode.get(barcode)
    # #         if product:
    # #             stock_move_data = {
    # #                 'product_id': product.id,
    # #                 'product_uom_qty': qty,
    # #                 'product_uom': product.uom_id.id,
    # #                 'name': product.display_name,
    # #             }
    # #             stock_moves.append(stock_move_data)

    # #     # Opcionalmente agrupar y ordenar por product_id
    # #     if group_and_sort:
    # #         return self.group_and_sort_stock_moves(stock_moves)

    # #     return stock_moves

    # def create_stock_moves(self, codes_quantities, picking_id, group_and_sort=False):
    #     """
    #     Crea movimientos de stock a partir de los códigos y cantidades, agregando información de picking.
    #     """
    #     # Paso 1: Generar los movimientos básicos de stock
    #     stock_moves, invalidcodes, stats = self.env["in.stock.pi8.codegc.moves"].superfunc_codegc_moves__from_list_text_codes(textcodes=codes_quantities, fields="product_id,product_uom_qty,product_uom,name")
    #     if invalidcodes:
    #         raise UserError(f"Códigos inválidos encontrados: {', '.join(invalidcodes)}")

    #     # Paso 2: Obtener el picking y agregar información adicional a los movimientos
    #     picking = self.env['stock.picking'].browse(picking_id)
    #     if not picking.exists():
    #         raise UserError("Stock picking no encontrado.")

    #     # Agregar información específica del picking a cada movimiento de stock
    #     for move in stock_moves:
    #         move.update({
    #             'location_id': picking.location_id.id,
    #             'location_dest_id': picking.location_dest_id.id,
    #             'picking_id': picking.id,
    #         })

    #     return stock_moves