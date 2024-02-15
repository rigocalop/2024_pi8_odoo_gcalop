import json
from ..zlogger_handlers import hlog_api
from odoo import http, _
from odoo.http import request, Response
from .._sy import lib_sy as sy
from .._sx import lib_sx as sx
from .._sz import lib_sz as sz

class Odoo_CodegcLot_Controller(http.Controller):
    @http.route('/api/codegclot/ensure', type='http', methods=['POST'], auth='public', csrf=False)
    @hlog_api()
    def api_codegclot_ensure(self, **kw):
        # Asegurar la extracción de los datos
        data = json.loads(request.httprequest.data)
        textcodes = sx.XList.ensure(data)     

        # Extraer 'return_entries' como un parámetro de la URL, valor predeterminado a True si no se proporciona
        type_return = sy.Api.prmStr('return', '')
        return_entries = True if type_return.lower() != '' else False
        
        is_success, entries = sz.Odoo_CodegcLot.Ensure(env=request.env, textcodes=textcodes, return_entries=return_entries)
        if not return_entries: entries = { 'message' : 'Entries created successfully'}
        return sy.Api.ApiResponse(is_success=is_success, data=entries, message_error=f'Invalid entries found: {entries}')

    @http.route('/api/codegclot/generate', type='http', methods=['GET'], auth='public', csrf=False)
    @hlog_api()
    def api_codegclot_generate(self, **kw):
        # Extraer los parámetros 'codegc' y 'qty' del URL como parámetros de consulta
        codegc = sy.Api.prmStr('codegc', None, True)
        qty = sy.Api.prmInt('qty', 1)
        moreinfo = sy.Api.prmBool('moreinfo', False)

        # Llamar al método para generar el código de lote
        is_success, codegclot = sz.Odoo_CodegcLot.Generate(env=request.env, codegc=codegc, qty=qty, moreinfo=moreinfo)
        return sy.Api.ApiResponse(is_success=is_success,data=codegclot,message_error=f'{codegclot}')
        
    @http.route('/api/codegclot/ensure/data', type='http', methods=['POST'], auth='public', csrf=False)
    @hlog_api()
    def api_codegclot_ensure_data(self, **kw):
        # Asegurar la extracción de los datos
        data = json.loads(request.httprequest.data)
        
        # Extraer 'entries' del cuerpo de la solicitud JSON
        entries = data.get('entries', [])
        is_success, to_return = sz.Odoo_CodegcLot.EnsureData(env=request.env, entries=entries)
        return sy.Api.ApiResponse(is_success=is_success,data=to_return,message_error=f'{to_return}')
