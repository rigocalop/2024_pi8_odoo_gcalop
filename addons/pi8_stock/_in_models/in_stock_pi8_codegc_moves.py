# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request, Response
from werkzeug.exceptions import BadRequest, NotFound
import logging
import re
import odoo
import json
from .._in_common.zlogger import ZLogger, logger_api_handler, logger_function_handler, logger_superfunc_handler
import json

logging.setLoggerClass(ZLogger)
_logger = logging.getLogger("testLogger")


class in_stock_pi8_codegc_moves(models.AbstractModel):
    _name = 'in.stock.pi8.codegc.moves'
    _description = 'Modelo Base GCALOP'

#region "procedimientos atomicos"
    @staticmethod
    @logger_function_handler    
    def _parse_to_moves_codegc__from_text_codes__clean_text_codes(text_codes):
        # Reemplaza diferentes separadores por un único separador (por ejemplo, una coma)
        text_codes = re.sub(r'[\r\n]+', ',', text_codes)
        text_codes = re.sub(r',+', ',', text_codes).strip()
        return text_codes
    
    @staticmethod
    @logger_function_handler
    def _parse_to_moves_codegc__from_text_codes__single_text_code(single_text_code):
        # Initialize default values
        default_code = None
        qty = 1.0  # Default quantity
        serial = None
        lot_id = None  # Initialize as None as it's not part of text_code
        product_id = None  # Initialize as None as it's not part of text_code

        
        # Splitting the string based on the presence of '$' and '*'
        if '$' in single_text_code:
            parts = single_text_code.split('$')
            default_code = parts[0].strip()
            rest = parts[1]

            if '*' in rest:
                serial, quantity_str = rest.split('*')
                qty = float(quantity_str.strip()) if quantity_str else 1.0
            else:
                serial = rest.strip()
        else:
            if '*' in single_text_code:
                default_code, quantity_str = single_text_code.split('*')
                default_code = default_code.strip()
                qty = float(quantity_str.strip()) if quantity_str else 1.0
                
                
            else:
                default_code = single_text_code.strip()

        # Stripping any whitespace from the serial
        serial = serial.strip() if serial else None
        
        # Return as a dictionary
        to_return = {	
            'default_code': default_code,
            'qty': qty,
            'serial': serial,
            'lot_id': None,
            'product_id': None,
            'codegc': None,
            'isvalid': True,
            'isvalid_code': True,
            'isvalid_serial': True,
            "iscreated_product": False,
            "iscreated_lot": False,
            "text_code": single_text_code
        }
        return to_return

    @staticmethod
    @logger_function_handler
    def _parse_to_codegc_moves__from_text_codes(text_codes, **kwargs):
        # Limpiar y preparar los códigos de texto
        text_codes = in_stock_pi8_codegc_moves._parse_to_moves_codegc__from_text_codes__clean_text_codes(text_codes)
        codegc_moves = []
        invalid_entries = []
        for entry in text_codes.split(','):
            entry = entry.strip()

            # Parse each code to extract details
            code_details = None
            try:
                code_details =  in_stock_pi8_codegc_moves._parse_to_moves_codegc__from_text_codes__single_text_code(entry)
                if not code_details['default_code'] and not code_details['serial']:
                    invalid_entries.append({'entry': entry, 'description': 'Invalid entry'})
                
                codegc_moves.append(code_details)                    
            except Exception as e:
                invalid_entries.append({'entry': entry, 'description': 'Invalid entry'})
            
        return codegc_moves, invalid_entries
#endregion

#region "Actualización de codegc_moves"
    @api.model
    @logger_function_handler
    def _update_codegc_moves__product_ids_from_default_code(self, codegc_moves):
        Product = self.env['product.product']

        # Obtener los valores únicos de default_code de elementos con product_id=None y isvalid=True
        default_codes_to_search = list(set(detail['default_code'] for detail in codegc_moves if detail['product_id'] is None and detail['isvalid']))

        # Buscar productos correspondientes a los default_codes a partir de la nueva lista
        products = Product.search([('default_code', 'in', default_codes_to_search)])
        products = self.env['product.product'].search([])

        # Crear un diccionario para mapear default_code a product_id
        product_map = {product.default_code: product.id for product in products}

        # Actualizar product_id en codegc_moves
        for code_detail in codegc_moves:
            if code_detail['default_code'] in product_map:
                code_detail['product_id'] = product_map[code_detail['default_code']]
            else:
                _logger.warning(f"Producto no encontrado con default_code: {code_detail['default_code']}")
        return codegc_moves

    @api.model
    @logger_function_handler
    def _update_codegc_moves__lot_ids_from_serial(self, codegc_moves):
        StockProductionLot = self.env['stock.lot']

        # Extraer todos los seriales
        serials = [detail['serial'] for detail in codegc_moves if detail['serial']]

        # Buscar todos los lotes correspondientes a los seriales
        lots = StockProductionLot.search([('name', 'in', serials)])

        # Crear un diccionario para mapear serial a lot_id y product_id
        lot_map = {lot.name: (lot.id, lot.product_id.id) for lot in lots}

        # Actualizar lot_id y product_id en codes_details basado en la información del lote
        for code_detail in codegc_moves:
            if code_detail['serial'] in lot_map:
                lot_id, product_id = lot_map[code_detail['serial']]
                code_detail['lot_id'] = lot_id
                code_detail['product_id'] = product_id
            else:
                _logger.warning(f"Lote no encontrado con serial: {code_detail['serial']}")
        return codegc_moves

    @api.model
    @logger_function_handler
    def _update_codegc_moves__from_product_id(self, codegc_moves):
        Product = self.env['product.product']

        # Identificar los product_id para los que se necesita buscar default_code (asegurando que sean únicos)
        product_ids_set = {detail['product_id'] for detail in codegc_moves if detail['product_id'] and not detail.get('default_code')}

        if product_ids_set:
            # Buscar en product.product para obtener los default_code
            products = Product.browse(product_ids_set)

            # Crear un diccionario para mapear product_id a default_code
            product_map = {product.id: product.default_code for product in products}

            # Actualizar codes_details con default_code
            for detail in codegc_moves:
                if detail['product_id'] in product_map:
                    detail['default_code'] = product_map[detail['product_id']]
        return codegc_moves
    
    @api.model
    @logger_function_handler
    def _update_codegc_moves__codegc_info_and_validate(self, codegc_moves):
        for code_detail in codegc_moves:
            default_code = code_detail['default_code']
            # Obtener la información detallada del código GC
            Pi8_CodeGC = self.env["in.stock.pi8.codegc"]
            codegc_info = Pi8_CodeGC.get_codegc(default_code)
            if codegc_info:
                # Actualizar el diccionario con la información obtenida
                code_detail['codegc'] = codegc_info
                serial = code_detail['serial']
                if serial:
                    isvalid_serial = Pi8_CodeGC.validate_serial_codigo(serial, default_code)
                    code_detail['isvalid_serial'] = isvalid_serial
                    code_detail['isvalid'] = isvalid_serial
                    if not isvalid_serial:
                        _logger.warning(f"El serial no es valido: {serial}")    
            else:
                code_detail['isvalid'] = False
                code_detail['isvalid_code'] = False
                _logger.warning(f"No se encontró información para el código GC: {default_code}")
        return codegc_moves
#endregion


    @api.model
    @logger_function_handler
    def _create_products__get_product_vals(self, codegc):
        # Validar el código del producto
        codegc_info = self.env["in.stock.pi8.codegc"].get_codegc(codegc)
        if not codegc_info:
            _logger.warning(f"Validación fallida para el código: {codegc}")
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
            'available_in_pos': True
        }

        # Agregar el campo 'barcode' si es la versión Enterprise
        if odoo.release.version_info[4] == 'e':
            product_vals['barcode'] = codegc
        return product_vals
    
    @api.model
    @logger_function_handler
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
                _logger.warning(f"Productos Agregado: {move['text_code']}")
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
    
    @api.model
    @logger_function_handler
    def _update_codegc_moves__create_new_stock_lots(self, codegc_moves):
        created_products = []
        # Filtrar elementos que cumplan con la condición 'isvalid=True' y 'product_id=None'
        valid_codegc_moves = [item for item in codegc_moves if item['isvalid'] and item['lot_id'] is None]
        
        if valid_codegc_moves != []:
            # Obtener valores distintos de 'codegc' en la lista filtrada
            unique_codegc_list = list(set(item.get('serial') for item in valid_codegc_moves))
            Product = self.env['product.product']
            StockLot = self.env['stock.lot']

            # Crear un array de lot_vals
            lots_to_create = []
            for move in valid_codegc_moves:
                new_lot = {
                    'name': move['serial'],
                    'product_id': move['product_id']
                }
                lots_to_create.append(new_lot)
                _logger.warning(f"Product Lot Agregado: {move['text_code']}")


            # Realizar una inserción masiva de productos en la base de datos
            if lots_to_create:
                created_lots = StockLot.create(lots_to_create)

            # Actualizar 'lot_id' en 'codegc_moves' con los IDs de los lot creados
            for move in codegc_moves:
                matching_lot = next((lot for lot in created_lots if lot.name == move['serial']), None)

                if matching_lot:
                    move['lot_id'] = matching_lot.id
                    move['iscreated_lot'] = True
    @api.model
    def _update_invalid_entries(self, codegc_moves, invalid_entries):
        for move in codegc_moves:
            if not move.get('isvalid', True):
                description = 'General invalid entry'
                if move.get('isvalid_code') == False:
                    description = 'Invalid code'
                elif move.get('isvalid_serial') == False:
                    description = 'Invalid serial'
                _logger.warning(f"Invalid Entry: {move['text_code']} - {description}")
                invalid_entries.append({'entry': move, 'description': description})
    
    
    @api.model
    @logger_superfunc_handler
    def superfunc_codegc_moves__from_text_codes(self, text_codes, **kwargs):
        # Extraer detalles básicos de cada código
        codegc_moves, invalid_entries = in_stock_pi8_codegc_moves._parse_to_codegc_moves__from_text_codes(text_codes)

        # Actualizar información de product_id y lot_id
        codegc_moves = self._update_codegc_moves__product_ids_from_default_code(codegc_moves)
        codegc_moves = self._update_codegc_moves__lot_ids_from_serial(codegc_moves)
        codegc_moves = self._update_codegc_moves__from_product_id(codegc_moves)
        codegc_moves = self._update_codegc_moves__codegc_info_and_validate(codegc_moves)
        
        self._update_invalid_entries(codegc_moves, invalid_entries)
        
        codegc_moves = self._update_codegc_moves__create_new_products(codegc_moves)
        codegc_moves = self._update_codegc_moves__create_new_stock_lots(codegc_moves)
        
        # _logger.fend(currentframe().f_code.co_qualname,codegc_moves=codegc_moves)
        return codegc_moves, invalid_entries


class in_stock_pi8_codegc_moves_controller(http.Controller):
    @http.route('/api/codegc/moves', type='http', methods=['POST'], auth='public', csrf=False)
    @logger_api_handler
    def superapi_codegc_moves__from_text_codes(self, **post):
        text_codes = json.loads(request.httprequest.data).get('text_codes')
        codegc_moves, invalid_entries = request.env['in.stock.pi8.codegc.moves'].superfunc_codegc_moves__from_text_codes(text_codes)
        if invalid_entries: return BadRequest(f'{invalid_entries}')
        return json.dumps({'result': codegc_moves})


