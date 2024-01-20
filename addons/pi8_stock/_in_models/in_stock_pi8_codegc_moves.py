# -*- coding: utf-8 -*-
import odoo, json
from odoo import http, api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request
from werkzeug.exceptions import BadRequest, NotFound
from ..pi8 import zlog, logger, sx, sy, hlog

class in_stock_pi8_codegc_moves(models.AbstractModel):
    _name = 'in.stock.pi8.codegc.moves'
    _description = 'Modelo Base GCALOP'
    
    @classmethod
    @hlog.hlog_function()
    def _parse_to_codegc_moves__from_text_codes(cls, list_text_codes, **kwargs):
        # Limpiar y preparar los códigos de texto
        mapping_dict = { 'product_uom_qty': 'qty', 'default_code': 'code', 'lot_name': 'lot','entry': 'entry'}
        default_values = { 'product_id': None, 'lot_id': None, 'product_uom': None, 'name': None, 'codegc': None, 'isvalid': True, 'isvalid_code': True, 'isvalid_serial': True, "iscreated_product": False,"iscreated_lot": False }
        codegc_moves, invalid_entries = sy.EntryCodeLot.processEntryTextCodes(list_text_codes, default_values, mapping_dict)
        return codegc_moves, invalid_entries

    @hlog.hlog_function()
    def _update_codegc_moves__codegc_info_and_validate(self, codegc_moves):
        for code_detail in codegc_moves:
            default_code = code_detail['default_code']
            # Obtener la información detallada del código GC
            codegc_info = self.env["in.stock.pi8.codegc"].get_codegc(default_code)
            if codegc_info:
                # Actualizar el diccionario con la información obtenida
                code_detail['codegc'] = codegc_info
                lot_name = code_detail['lot_name']
                name = codegc_info['linea']['name']
                is_valid = True
                is_valid_code = sx.base36.validate(default_code)
                is_valid_serial = True

                if lot_name: 
                    is_valid_lot_name = sy.codegc.validate_lot_name(default_code, lot_name)
                is_valid = is_valid_code and is_valid_lot_name
                
                if not is_valid:
                    logger.warning(f"Invalid **lot_name**: {lot_name}") 
                
                # Actualizar el diccionario con los resultados de la validación
                code_detail['name'] = codegc_info['linea']['name']
                code_detail['isvalid'] = is_valid
                code_detail['isvalid_code'] = is_valid_code
                code_detail['isvalid_serial'] = is_valid_lot_name
            else:
                code_detail['isvalid'] = False
                code_detail['isvalid_code'] = False
                logger.warning(f"No se encontró información para el código GC: {default_code}")
        return codegc_moves

    @hlog.hlog_function()
    def _create_products__get_product_vals(self, codegc):
        # Validar el código del producto
        codegc_info = self.env["in.stock.pi8.codegc"].get_codegc(codegc)
        if not codegc_info:
            logger.warning(f"Validación fallida para el código: {codegc}")
            raise UserError(_("Código del producto inválido o falta información relacionada."))

        # Crear el diccionario de valores del producto
        product_vals = {
            'name': codegc_info['linea']['name'],
            'description': codegc_info['temporada']['name'],
            'list_price': float(codegc_info['precio']['value']),
            'default_code': codegc,
            'type': 'product',
            'sale_ok': True,
            'purchase_ok': True,
            'available_in_pos': True,
            'tracking': 'none'
        }

        # Agregar el campo 'barcode' si es la versión Enterprise
        if odoo.release.version_info[4] == 'e':
            product_vals['barcode'] = codegc
        return product_vals
    
    
    @hlog.hlog_function()
    def _update_codegc_moves__create_new_products(self, codegc_moves):
        created_products = []
        # Filtrar elementos que cumplan con la condición 'isvalid=True' y 'product_id=None'
        valid_codegc_moves = [item for item in codegc_moves if item['isvalid'] and item['product_id'] is None]
        
        if valid_codegc_moves != []:
            # Obtener valores distintos de 'codegc' en la lista filtrada
            unique_codegc_list = list(set(item.get('default_code') for item in valid_codegc_moves))
            Product = self.env['product.product']

            # Crear un array de product_vals
            product_vals_to_create = []

            for move in valid_codegc_moves:
                
                product_vals = self._create_products__get_product_vals(move['default_code'])
                tracking = move['codegc']['linea']['tracking']
                product_vals['tracking'] = tracking
                logger.warning(f"Productos Agregado: {move['entry']}")
                product_vals_to_create.append(product_vals)

            # Realizar una inserción masiva de productos en la base de datos
            if product_vals_to_create:
                created_products = self.env['product.product'].create(product_vals_to_create)

            # Actualizar 'product_id' en 'codegc_moves' con los IDs de los productos creados
            for move in codegc_moves:
                matching_product = next((product for product in created_products if product.default_code == move['default_code']), None)
                if matching_product:
                    move['product_id'] = matching_product.id
                    move['iscreated_product'] = True
        return codegc_moves
    
    
    @hlog.hlog_function()
    def _update_codegc_moves__create_new_stock_lots(self, codegc_moves):
        # Filtrar elementos que cumplan con la condición 'isvalid=True' y 'product_id=None'
        valid_codegc_moves = [item for item in codegc_moves if item['isvalid'] and item['lot_id'] is None]

        if valid_codegc_moves != []:
            # Obtener valores distintos de 'codegc' en la lista filtrada
            StockLot = self.env['stock.lot']

            # Crear un array de lot_vals
            lots_to_create = []
            for move in valid_codegc_moves:
                new_lot = {
                    'name': move['lot_name'],
                    'product_id': move['product_id']
                }
                lots_to_create.append(new_lot)
                logger.warning(f"Product Lot Agregado: {move['entry']}")

            # Realizar una inserción masiva de productos en la base de datos
            if lots_to_create:
                created_lots = StockLot.create(lots_to_create)

            # Actualizar 'lot_id' en 'codegc_moves' con los IDs de los lot creados
            for move in codegc_moves:
                matching_lot = next((lot for lot in created_lots if lot.name == move['lot_name']), None)
                if matching_lot:
                    move['lot_id'] = matching_lot.id
                    move['iscreated_lot'] = True
        
                    
    @api.model
    @hlog.hlog_function()
    def _update_codegc_moves__from_product_id__set_uom(self, codegc_moves):
        Product = self.env['product.product']

        # Identificar los product_id para los que se necesita buscar default_code (asegurando que sean únicos)
        product_ids_set = {detail['product_id'] for detail in codegc_moves if detail['product_id']}
        product_map = {}

        if product_ids_set:
            # Buscar en product.product para obtener los default_code y uom_id
            products = Product.browse(product_ids_set)
            # Crear un diccionario para mapear product_id a default_code y uom_id
            product_map = {product.id: {'default_code': product.default_code, 'uom_id': product.uom_id.id} for product in products}
        
        logger.info(f"product_map: {product_map}")
        
        # Actualizar codegc_moves con uom_id solo si es None y existe product_id
        for detail in codegc_moves:
            if detail['product_id'] in product_map and detail.get('uom_id') is None:
                detail.update({
                    'product_uom': product_map[detail['product_id']]['uom_id']
                })
        return codegc_moves

    def _update_invalid_entries(self, codegc_moves, invalid_entries):
        for move in codegc_moves:
            if not move.get('isvalid', True):
                description = 'General invalid entry'
                if move.get('isvalid_code') == False:
                    description = 'Invalid code'
                elif move.get('isvalid_serial') == False:
                    description = 'Invalid Tracking'
                logger.warning(f"Invalid Entry: {move['entry']} - {description}")
                invalid_entries.append({'entry': move, 'description': description})
    
    @hlog.hlog_superfunc()
    def superfunc_codegc_moves__from_list_text_codes(self, list_text_codes, fields = None):
        codegc_moves, invalid_entries = self._parse_to_codegc_moves__from_text_codes(list_text_codes)
        # Actualizar información de product_id y lot_id
        
        # Actualizar información desde 'product.product' para los casos en que no se encuentre el 'product.product'
        codegc_moves = sy.OdooModel.joinListDict(self.env, codegc_moves,  'default_code',  { 'default_code': not None }, 
            odoo_model_name='product.product', odoo_model_field_on='default_code', model_retreive_fields=['id', 'default_code', 'uom_id'], 
            mapping_fields= {'id': 'product_id', 'product_uom': 'uom_id'})
        
        # Actualizar información desde 'stock.lot' para los casos en que no se encuentre el lot_name
        codegc_moves = sy.OdooModel.joinListDict(self.env, codegc_moves,  'lot_name',  { 'lot_name': not None },
            odoo_model_name='stock.lot', odoo_model_field_on='name', model_retreive_fields=['id', 'name', 'product_id'], 
            mapping_fields= {'lot_id': 'id', 'product_id': 'product_id[0]'})
        
        # Actualizar información desde 'product.product' para los casos en que no se encuentre el default_code
        codegc_moves = sy.OdooModel.joinListDict(self.env, codegc_moves, 'default_code',  {'product_id': not None, 'default_code': None},
            odoo_model_name='product.product', odoo_model_field_on='default_code', model_retreive_fields=['id', 'default_code', 'uom_id'],
            mapping_fields={'product_id': 'id', 'default_code': 'default_code','product_uom': 'uom_id[0]'})
        
        
        codegc_moves = self._update_codegc_moves__codegc_info_and_validate(codegc_moves)
        self._update_invalid_entries(codegc_moves, invalid_entries)
        stats = {}
        stats['entries_valids'] = sx.XList.count_matches(codegc_moves, 'isvalid', True)
        stats['entries_invalids'] = sx.XList.count_matches(codegc_moves, 'isvalid', False) + len(invalid_entries)
        
        if not invalid_entries:
            codegc_moves = self._update_codegc_moves__create_new_products(codegc_moves)
            self._update_codegc_moves__create_new_stock_lots(codegc_moves)
            codegc_moves = self._update_codegc_moves__from_product_id__set_uom(codegc_moves)
            codegc_moves = sx.XList.fields_include(codegc_moves, fields)
            stats['created_products'] = sx.XList.count_matches(codegc_moves, 'iscreated_product', True)
            stats['created_lots'] = sx.XList.count_matches(codegc_moves, 'iscreated_lot', True)
            stats['message']='The products and corresponding lots have been created.'
        else:
            stats['message']='Exist invalid entries.'
        logger.info("Tipo de codegc_moves: " + str(type(codegc_moves)))
        return codegc_moves, invalid_entries, stats
    
    @hlog.hlog_superfunc()
    def superfunc_codegc_moves__from_text_codes(self, text_codes, fields = None):
        list_text_codes = sx.XList.convert(text_codes)
        return self.superfunc_codegc_moves__from_list_text_codes(list_text_codes, fields)

class in_stock_pi8_codegc_moves_controller(http.Controller):
    @http.route('/api/codegc/moves', type='http', methods=['POST'], auth='public', csrf=False)
    @hlog.hlog_api
    def superapi_codegc_moves__from_text_codes(self, **kw):
        fields = kw.get('fields')
        data = json.loads(request.httprequest.data)
        textcodes = sx.xobject.tryget(data, 'text_codes')
        
        if textcodes: list_text_codes = sx.XList.ensure(textcodes)
        else: list_text_codes = sx.XList.ensure(data)

        codegc_moves, invalid_entries, stats = request.env['in.stock.pi8.codegc.moves'].superfunc_codegc_moves__from_list_text_codes(list_text_codes,fields)
        if stats['entries_invalids'] > 0:
            return BadRequest({ 'error':  'Bad Request', 'message': 'Invalid entries found', 'stats': stats, 'invalid_entries': invalid_entries })
        else:
            return { 'message': 'The products and corresponding lots have been created.', 'stats': stats, 'codegc_moves': codegc_moves }



