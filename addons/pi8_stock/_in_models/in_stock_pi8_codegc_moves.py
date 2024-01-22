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
    @hlog.hlog_function(enable=True,resalt=True)
    def sy_OdooCodeGC_EnsureCodeLot(self, _textcodes):
        default_values = { 'product_id': None, 'lot_id': None }
        codes, invalid_entries = sy.EntryCodeLot.processEntryTextCodes(_textcodes, default_values, None, validation_function = self.env["in.stock.pi8.codegc"].valid)
        list_CodeLot = sy.OdooModel.JoinLeft(self.env, codes,  'lot',  {'lot': '#not_empty'}, model_name='stock.lot', model_field_on='name', model_retreive_fields=['id', 'name', 'product_id'], mapping_fields= {'lot_id': 'id', 'product_id': 'product_id[0]'})
        list_CodeLot = sy.OdooModel.JoinLeft(self.env, codes,  'code',  {'code': '#not_empty'}, model_name='product.product', model_field_on='default_code', model_retreive_fields=['id', 'default_code'], mapping_fields= {'product_id': 'id' })

        
        
        products_to_create = []
        products = sx.XListDict.distinct_values(list_CodeLot, 'code', filtering_params={'code': '#not_empty', 'product_id': '#empty' })  
        for item in products:
            codegc_info = self.env["in.stock.pi8.codegc"].get_codegc(item)
            new_product = {
                'name': codegc_info['linea']['name'],
                'description': codegc_info['temporada']['name'],
                'list_price': float(codegc_info['precio']['value']),
                'default_code': item['code'],
                'tracking': codegc_info['linea']['tracking'],
                'sale_ok': True,
                'purchase_ok': True,
                'available_in_pos': True,
                'type': 'product'
            }
            logger.warning(f"Productos Agregado: {item['default_code']}")
            products_to_create.append(new_product)
        self.env['product.product'].create(products_to_create)
            
        lots_to_create = []
        lots = sx.XListDict.distinct_values(list_CodeLot, 'lot', filtering_params={'lot': '#not_empty', 'lot_id': '#empty'})  
        for item in lots:
            new_lot = {
                'name': item['lot'],
                'product_id': item['product_id']
            }
            lots_to_create.append(new_lot)
            logger.warning(f"LOTs Agregados: {item['lot']}")
        self.env['stock.lot'].create(lots_to_create)
            
    
    @hlog.hlog_superfunc()
    def superfunc_codegc_moves__from_list_text_codes(self, list_text_codes, fields = None):
        # Procesar los códigos de texto
        default_values = { 'product_id': None, 'lot_id': None, 'product_uom': None, 'name': None, 'codegc': None, 'isvalid': True, 'isvalid_code': True, 'isvalid_serial': True, "iscreated_product": False,"iscreated_lot": False }
        codegc_moves, invalid_entries = sy.EntryCodeLot.processEntryTextCodes(list_text_codes, default_values, mapping_dict = { 'product_uom_qty': 'qty', 'default_code': 'code', 'lot_name': 'lot','entry': 'entry'}, validation_function=self.env["in.stock.pi8.codegc"].valid)
        self.sy_OdooCodeGC_EnsureCodeLot(list_text_codes)
        
        # ACTUALIZAR_PRODUCT_ID, LOT_ID

        # Actualizar información desde 'stock.lot' para los casos en que no se encuentre el lot_name
        codegc_moves = sy.OdooModel.JoinLeft(self.env, codegc_moves,  'lot_name',  { 'lot_name': not None },
            model_name='stock.lot', model_field_on='name', model_retreive_fields=['id', 'name', 'product_id'], 
            mapping_fields= {'lot_id': 'id', 'product_id': 'product_id[0]'})     
        
        # Actualizar información desde 'product.product' para los casos en que no se encuentre el 'product.product'
        codegc_moves = sy.OdooModel.JoinLeft(self.env, codegc_moves,  'default_code',  { 'default_code': not None }, 
            model_name='product.product', model_field_on='default_code', model_retreive_fields=['id', 'default_code', 'uom_id'], 
            mapping_fields= {'id': 'product_id', 'product_uom': 'uom_id'})
        

        
        # # Actualizar información desde 'product.product' para los casos en que no se encuentre el default_code
        # codegc_moves = sy.OdooModel.JoinLeft(self.env, codegc_moves, 'default_code',  {'product_id': not None, 'default_code': None},
        #     model_name='product.product', model_field_on='default_code', model_retreive_fields=['id', 'default_code', 'uom_id'],
        #     mapping_fields={'product_id': 'id', 'default_code': 'default_code','product_uom': 'uom_id[0]'})
        
        stats = {}
        stats['entries_valids'] = len(codegc_moves)
        stats['entries_invalids'] = len(invalid_entries)
        
        if not invalid_entries:
            # codegc_moves = self._update_codegc_moves__create_new_products(codegc_moves)
            # self._update_codegc_moves__create_new_stock_lots(codegc_moves)
            # codegc_moves = self._update_codegc_moves__from_product_id__set_uom(codegc_moves)
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

