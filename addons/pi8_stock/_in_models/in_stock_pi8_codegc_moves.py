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
from inspect import currentframe
from .._in_common.zlogger import ZLogger, api_response_handler
from odoo.http import SessionExpiredException, serialize_exception
import collections
from functools import wraps
import json

logging.setLoggerClass(ZLogger)
_logger = logging.getLogger("testLogger")




class in_stock_pi8_codegc_moves(models.AbstractModel):
    _name = 'in.stock.pi8.codegc.moves'
    _description = 'Modelo Base GCALOP'
#region "procedimientos atomicos"
    @staticmethod
    def _parse_to_moves_codegc__from_text_codes__clean_text_codes(text_codes):
        _logger.fini(currentframe().f_code.co_qualname, text_codes=text_codes)
        """
        Procesa el texto de códigos para separarlos adecuadamente.
        :param texto: string con los códigos.
        :return: list de códigos.
        """
        # Reemplaza diferentes separadores por un único separador (por ejemplo, una coma)
        text_codes = re.sub(r'[\r\n]+', ',', text_codes)
        text_codes = re.sub(r',+', ',', text_codes).strip()
        _logger.fend(currentframe().f_code.co_qualname, text_codes=text_codes)
        return text_codes
    
    @staticmethod
    def _parse_to_moves_codegc__from_text_codes__single_text_code(single_text_code):
        """
        Extracts product default_code, quantity, serial number, lot_id, and product_id from a single text code.
        :param text_code: String with the format 'default_code$serial*quantity' or variations thereof.
        :return: Dictionary with keys 'default_code', 'qty', 'serial', 'lot_id', 'product_id'.
        """
        _logger.fini(currentframe().f_code.co_qualname, single_text_code=single_text_code)
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
            "iscreated_product": False
        }
        _logger.fend(currentframe().f_code.co_qualname, to_return=to_return)
        return to_return

    @staticmethod
    def _parse_to_codegc_moves__from_text_codes(text_codes, **kwargs):
        _logger.fini(currentframe().f_code.co_qualname, text_codes=text_codes)
        """
        Processes a text string containing product codes, quantities, and serial numbers,
        extracting detailed information for each code. If an entry is found with both
        serial and default_code empty, the process is stopped with an error.
        :param text_codes: String with product codes and quantities (format 'default_code$serial*quantity').
        :return: Tuple of two lists: (list of dictionaries with code details, list of invalid codes).
        """
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
            
        _logger.fend(currentframe().f_code.co_qualname, codegc_moves=codegc_moves)
        return codegc_moves, invalid_entries
#endregion

#region "Actualización de codegc_moves"
    @api.model
    def _update_codegc_moves__product_ids_from_default_code(self, codegc_moves):
        _logger.fini(currentframe().f_code.co_qualname, codegc_moves=codegc_moves)
        """
        Update product_id in each dictionary based on the default_code found, using a mass search.
        :param codegc_moves: List of dictionaries, each containing default_code, qty, serial, lot_id, and product_id.
        :return: The updated list of dictionaries with product_id set where default_code is found.
        """
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
        _logger.fend(currentframe().f_code.co_qualname, codegc_moves=codegc_moves)
        return codegc_moves


    @api.model
    def _update_codegc_moves__lot_ids_from_serial(self, codegc_moves):
        _logger.fini(currentframe().f_code.co_qualname, codegc_moves=codegc_moves)
        """
        Update lot_id and product_id in each dictionary based on the serial found in the lot, using a mass search.
        :param codes_details: List of dictionaries, each containing default_code, qty, serial, lot_id, and product_id.
        :return: The updated list of dictionaries with lot_id and product_id set where serial is found.
        """
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
        _logger.fend(currentframe().f_code.co_qualname, codegc_moves=codegc_moves)
        return codegc_moves

    @api.model
    def _update_codegc_moves__from_product_id(self, codegc_moves):
        _logger.fini(currentframe().f_code.co_qualname, codegc_moves=codegc_moves)
        """
        Actualiza el default_code en codes_details basándose en el product_id, si es necesario.
        :param codes_details: Lista de diccionarios, cada uno conteniendo default_code, qty, serial, lot_id y product_id.
        :return: La lista actualizada de diccionarios con default_code actualizado donde sea necesario.
        """
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
        _logger.fend(currentframe().f_code.co_qualname, codegc_moves=codegc_moves)
        return codegc_moves
    
    @api.model
    def _update_codegc_moves__codegc_info(self, codegc_moves):
        _logger.fini(currentframe().f_code.co_qualname, codegc_moves=codegc_moves)
        """
        Update each dictionary in the list with detailed codegc information using get_complete_codegc_info method.
        :param codes_list: List of dictionaries with keys 'default_code', 'qty', 'serial', 'lot_id', 'product_id', 'codegc'.
        :return: The updated list of dictionaries with detailed codegc information.
        """
        for code_detail in codegc_moves:
            default_code = code_detail['default_code']

            # Obtener la información detallada del código GC
            codegc_info = self.env["in.stock.pi8.codegc"].get_codegc(default_code)
            if codegc_info:
                # Actualizar el diccionario con la información obtenida
                code_detail['codegc'] = codegc_info
            else:
                code_detail['isvalid'] = False
                _logger.warning(f"No se encontró información para el código GC: {default_code}")
        _logger.fend(__name__, codegc_moves=codegc_moves)
        return codegc_moves
#endregion


    @api.model
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
    def _update_codegc_moves__create_new_products(self, codegc_moves):
        _logger.fini(currentframe().f_code.co_qualname, codegc_moves=codegc_moves)
        """
        Crea nuevos productos basados en los elementos de 'codegc_moves' que cumplan con las condiciones.
        Actualiza los elementos de 'codegc_moves' con información de 'product_vals'.
        Realiza una inserción masiva de productos en la base de datos.
        :param codegc_moves: Lista de elementos de movimiento de código GCALOP.
        :return: Lista de objetos 'product.product' de los productos creados.
        """
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

        _logger.fend(currentframe().f_code.co_qualname, codegc_moves=codegc_moves, created_products=created_products)
        return codegc_moves

    
    
    @api.model
    def generate_codegc_moves__from_text_codes(self, text_codes, **kwargs):
        _logger.fini(currentframe().f_code.co_qualname, text_codes=text_codes)
        """
        Generate a codes list from text codes, filling in additional details using existing methods.
        :param text_codes: String containing multiple codes in the format 'default_code$serial*quantity'.
        :return: List of dictionaries with complete information for each code.
        """
        # Extraer detalles básicos de cada código
        
        codegc_moves, invalid_entries = in_stock_pi8_codegc_moves._parse_to_codegc_moves__from_text_codes(text_codes)

        # Actualizar información de product_id y lot_id
        codegc_moves = self._update_codegc_moves__product_ids_from_default_code(codegc_moves)
        codegc_moves = self._update_codegc_moves__lot_ids_from_serial(codegc_moves)
        codegc_moves = self._update_codegc_moves__from_product_id(codegc_moves)
        codegc_moves = self._update_codegc_moves__codegc_info(codegc_moves)
        codegc_moves = self._update_codegc_moves__create_new_products(codegc_moves)
        
        _logger.fend(currentframe().f_code.co_qualname,codegc_moves=codegc_moves)
        return codegc_moves, invalid_entries

# def api_response_handler(func):
#     def wrapper(*args, **kwargs):
#         run_level = ZLogger.RUN_LEVEL
#         to_return = None
#         try:
#             api_params = {key: request.httprequest.args.getlist(key) for key in request.httprequest.args}
#             _logger.tini(f'API ejecutada: {request.httprequest.path} => {func.__module__}{func.__name__}', **api_params, api_data = request.httprequest.data)
#             result = func(*args, **kwargs)
#             response_content = None
#             status = 200
#             if isinstance(result, BadRequest):
#                 response_content = result.description
#                 status = 400
#             else: 
#                 response_content = json.dumps(result)
            
#             to_return = request.make_response(response_content, headers=[('Content-Type', 'application/json')], status=status)                
#             _logger.returns(f'API ejecutada: {request.httprequest.path} => {func.__module__}{func.__name__}', response_content=response_content, response=to_return)
#             _logger.tend(f'API ejecutada: {request.httprequest.path} => {func.__module__}{func.__name__}')
#             ZLogger.RUN_LEVEL = run_level    
#             return to_return
#         except Exception as e:
#             _logger.error(f'Error durante la ejecución de la API: {str(e)}')
#             response_content = json.dumps({'error': str(e)})
#             ZLogger.RUN_LEVEL = run_level    
#             return request.make_response(response_content, headers=[('Content-Type', 'application/json')], status=500)
#     return wrapper

class in_stock_pi8_codegc_moves_controller(http.Controller):
    @http.route('/api/codegc/moves', type='http', methods=['POST'], auth='public', csrf=False)
    @api_response_handler
    def generate_codegc_moves(self, **post):
        text_codes = json.loads(request.httprequest.data).get('text_codes')
        codegc_moves, invalid_entries = request.env['in.stock.pi8.codegc.moves'].generate_codegc_moves__from_text_codes(text_codes)
        if invalid_entries:
            return BadRequest(f'{invalid_entries}')
        response_content = json.dumps({'result': codegc_moves})
        return response_content


