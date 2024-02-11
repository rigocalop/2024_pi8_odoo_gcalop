import odoo, json

from ..zlogger_handlers import *
from odoo import models
from ..zlogger import ZLogger
from ..zlogger_handlers import hlog_api

from odoo import http, api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request, Response
from werkzeug.exceptions import BadRequest, NotFound

from .._sy import lib_sy as sy
from .._sx import lib_sx as sx
from .._sz import lib_sz as sz

class OdooCodeGC_Controller(http.Controller):
    @http.route('/api/codegc/ensure', type='http', methods=['POST'], auth='public', csrf=False)
    @hlog_api()
    def api_ensurecodelot(self, **kw):
        # Asegurar la extracción de los datos
        data = json.loads(request.httprequest.data)
        textcodes = sx.xobject.tryget(data, 'text_codes')
        if textcodes: textcodes = sx.XList.ensure(textcodes)
        else: textcodes = sx.XList.ensure(data)        

        # Asegurar la creación de los productos y lotes
        isvalid, entries, entries_invalid = sz.OdooCodeGC.EnsureCodeLot(env=request.env, textcodes=textcodes)

        if isvalid:
            stock_moves = sz.OdooCodeGC.joinCode_ModeID(env=request.env, target_list=entries)
            return stock_moves
        else:
            return BadRequest({ 'error':  'Bad Request', 'message': 'Invalid entries found', 'entries': entries_invalid })
        
        
# crer codigos de productos 
# enviar a rabbit una ubicacion.
