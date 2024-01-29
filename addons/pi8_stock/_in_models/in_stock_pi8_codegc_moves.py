# -*- coding: utf-8 -*-
import odoo, json
from odoo import http, api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request
from werkzeug.exceptions import BadRequest, NotFound
from ..pi8 import zlog, logger, sx, sy, hlog


class in_stock_pi8_codegc_moves(models.AbstractModel):
    _name = 'in.stock.pi8.codegc.moves'
        
    @hlog.hlog_superfunc()
    def superfunc_codegc_moves__from_list_text_codes(self, textcodes, fields = None):
        # Procesar los códigos de texto
        default_values = { 'product_id': None, 'lot_id': None, 'product_uom': None, 'name': None, 'codegc': None, 'isvalid': True, 'isvalid_code': True, 'isvalid_serial': True, "iscreated_product": False,"iscreated_lot": False }
        result =  sy.OdooCodeGC.EnsureCodeLot(env=self.env, textcodes=textcodes, is_return_list=True)
        
        
        return result
    
    
    @hlog.hlog_superfunc()
    def superfunc_codegc_moves__from_text_codes(self, text_codes, fields = None):
        list_text_codes = sx.XList.convert(text_codes)
        return self.superfunc_codegc_moves__from_list_text_codes(list_text_codes, fields)

class in_stock_pi8_codegc_moves_controller(http.Controller):
    @http.route('/api/codegc/moves', type='http', methods=['POST'], auth='public', csrf=False)
    @hlog.hlog_api()
    def superapi_codegc_moves__from_text_codes(self, **kw):
        fields = kw.get('fields')
        data = json.loads(request.httprequest.data)
        textcodes = sx.xobject.tryget(data, 'text_codes')
        if textcodes: textcodes = sx.XList.ensure(textcodes)
        else: textcodes = sx.XList.ensure(data)        

        isvalid, entries = sy.OdooCodeGC.EnsureCodeLot(env=request.env, textcodes=textcodes)
        
        
        
        


        codegc_moves, invalid_entries, stats = request.env['in.stock.pi8.codegc.moves'].superfunc_codegc_moves__from_list_text_codes(textcodes=list_text_codes, fields=fields)
        if stats['entries_invalids'] > 0:
            return BadRequest({ 'error':  'Bad Request', 'message': 'Invalid entries found', 'stats': stats, 'invalid_entries': invalid_entries })
        else:
            return { 'message': 'The products and corresponding lots have been created.', 'stats': stats, 'codegc_moves': codegc_moves }

