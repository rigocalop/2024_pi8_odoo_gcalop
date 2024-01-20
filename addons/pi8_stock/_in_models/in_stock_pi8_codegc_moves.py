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
    def expandEntryTextCode(cls, entry_textcode):
        """
        Extrae el código del producto, la cantidad y el número de lote de un código de texto único.
        :param entry_textcode: Cadena de texto con formatos como 'codigo$lote*cantidad' o 'codigo&lote*cantidad'.
            Los separadores utilizados para dividir el texto son '&' y '$'.
        :return: Diccionario con los siguientes campos:
            - 'entry': Texto original.
            - 'isvalid': Booleano que indica si el formato es válido.
            - 'code': Código del producto extraído del texto.
            - 'qty': Cantidad del producto como un valor flotante.
            - 'lot': Nombre o número de lote del producto.
                Esta función trata de identificar y separar los componentes del código del producto,
                la cantidad y el número de lote, basándose en los separadores específicos.
                Si el formato del texto de entrada no cumple con los patrones esperados,
                se marcará como no válido y se manejarán las excepciones adecuadamente.
        """
        # Mapeo de separadores a tipos de seguimiento
        tracking_map = {'$': 'serial', '&': 'lot'}
        separator = tracking_map.keys()

        # Inicializar valores predeterminados
        code = None
        qty = 1.0  # Cantidad por defecto
        lot = None
        tracking = 'none'
        entry_invalid = None

        try:
            # Encontrar el primer separador que está presente en entry_textcode
            separator_used = next((sep for sep in separator if sep in entry_textcode), None)

            if separator_used:
                parts = entry_textcode.split(separator_used)
                code = parts[0].strip()
                rest = parts[1] if len(parts) > 1 else ''

                if '*' in rest:
                    lot, qty_str = rest.split('*')
                    qty = float(qty_str.strip()) if qty_str else 1.0
                else:
                    lot = rest.strip()

                lot = separator_used + lot if lot else None
                tracking = tracking_map.get(separator_used, 'none')
            else:
                if '*' in entry_textcode:
                    code, qty_str = entry_textcode.split('*')
                    code = code.strip()
                    qty = float(qty_str.strip()) if qty_str else 1.0
                else:
                    code = entry_textcode.strip()

            # Eliminar espacios en blanco del nombre del lote
            lot = lot.strip() if lot else None

            if not lot and not code:
                entry_invalid = {'entry': entry_textcode, 'msg': 'No existen código y lote'}

        except Exception as e:
            entry_invalid = {'entry': entry_textcode, 'msg': 'Formato de cantidad inválido. No se puede convertir a flotante.'}

        if not entry_invalid and tracking == 'none' and lot is not None:
            entry_invalid = {'entry': entry_textcode, 'msg': 'Seguimiento ninguno y lote no es None'}

        entry = {'entry': entry_textcode, 'code': code, 'qty': qty, 'lot': lot, 'tracking': tracking}

        return entry, entry_invalid


#region "procedimientos atomicos"
    @classmethod
    @hlog.hlog_function()
    def _parse_to_moves_codegc__from_text_codes__single_text_code(cls, single_text_code):
        # Initialize default values
        entry, entry_invalid = cls.expandEntryTextCode(single_text_code)
        if entry == None:
            return None
        #default_code, qty, lot_name, isvalid =  sy.codegc.parse_product_details(single_text_code, str_separators=['&', '$']) 
        
        # Return as a dictionary
        to_return = {
            'product_id': None,
            'lot_id': None,
            'product_uom': None,
            'name': None,
            'product_uom_qty': entry.get('qty'),
            'default_code': entry.get('code'),
            'lot_name': entry.get('lot'),
            'codegc': None,
            'isvalid': True,
            'isvalid_code': True,
            'isvalid_serial': True,
            "iscreated_product": False,
            "iscreated_lot": False,
            "text_code": entry.get('entry'),
        }
        return to_return
    
    @classmethod
    @hlog.hlog_function()
    def _parse_to_codegc_moves__from_text_codes(cls, list_text_codes, **kwargs):
        # Limpiar y preparar los códigos de texto
        codegc_moves = []
        invalid_entries = []
        for entry in list_text_codes:
            entry = entry.strip()

            # Parse each code to extract details
            code_details = None
            try:
                code_details =  cls._parse_to_moves_codegc__from_text_codes__single_text_code(entry)
                if not code_details['isvalid']:
                    invalid_entries.append({'entry': entry, 'description': 'Invalid entry'})
                elif not code_details['default_code'] and not code_details['lot_name']:
                    invalid_entries.append({'entry': entry, 'description': 'Invalid entry'})
                else:
                    codegc_moves.append(code_details)                    
            except Exception as e:
                invalid_entries.append({'entry': entry, 'description': 'Invalid entry'})
            
        return codegc_moves, invalid_entries
#endregion

    
    
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
                logger.warning(f"Productos Agregado: {move['text_code']}")
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
                logger.warning(f"Product Lot Agregado: {move['text_code']}")

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
                logger.warning(f"Invalid Entry: {move['text_code']} - {description}")
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



