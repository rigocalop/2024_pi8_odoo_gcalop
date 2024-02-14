import json
from ..zlogger_handlers import *
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
        type_return = request.params.get('return', '')
        return_entries = True if type_return.lower() != '' else False
        
        isvalid, entries = sz.Odoo_CodegcLot.Ensure(env=request.env, textcodes=textcodes, return_entries=return_entries)

        if not isvalid:
            to_return = { 'error':  'Bad Request', 'message': 'Invalid entries found', 'entries': entries }
            return Response(json.dumps(to_return), content_type='application/json', status=400)
        elif not return_entries:
            to_return = { 'message' : 'Entries created successfully'}
            return Response(json.dumps(to_return), content_type='application/json', status=200)
        else:
            return Response(json.dumps(entries), content_type='application/json', status=200)

    @http.route('/api/codegclot/generate', type='http', methods=['GET'], auth='public', csrf=False)
    def api_codegclot_generate(self, **kw):
        # Extraer los parámetros 'codegc' y 'qty' del URL como parámetros de consulta
        codegc = request.params.get('codegc', '')  # Proporciona un valor predeterminado si 'codegc' no se encuentra
        qty_str = request.params.get('qty', '1')  # Usa '1' como valor predeterminado si 'qty' no se proporciona
        moreinfo = request.params.get('moreinfo', 'False')  # Usa '1' como valor predeterminado si 'qty' no se proporciona
        moreinfo = moreinfo.lower() in ['true', '1', 't', 'yes', 'y']  # Convierte a booleano

        # Intentar convertir 'qty' a un entero
        try:
            qty = int(qty_str)
        except ValueError:
            # Si 'qty' no es convertible a un entero, devuelve un error
            response_content = json.dumps({"error": "El parámetro 'qty' debe ser un número entero."})
            return Response(response_content, content_type='application/json', status=400)

        # Llamar al método para generar el código de lote
        isvalid, codegclot = sz.Odoo_CodegcLot.Generate(env=request.env, codegc=codegc, qty=qty, moreinfo=moreinfo)
        
        # Devolver la respuesta basada en si la operación fue válida o no
        if isvalid:
            response_content = json.dumps(codegclot)
            return Response(response_content, content_type='application/json', status=200)
        else:
            # Si la operación no fue válida, incluir el mensaje de error en la respuesta
            response_content = json.dumps({"error": codegclot})
            return Response(response_content, content_type='application/json', status=400)

    @http.route('/api/codegclot/generate', type='http', methods=['GET'], auth='public', csrf=False)
    def api_codegclot_generate(self, **kw):
        # Extraer los parámetros 'codegc' y 'qty' del URL como parámetros de consulta
        codegc = request.params.get('codegc', '')  # Proporciona un valor predeterminado si 'codegc' no se encuentra
        qty_str = request.params.get('qty', '1')  # Usa '1' como valor predeterminado si 'qty' no se proporciona
        moreinfo = request.params.get('moreinfo', 'False')  # Usa '1' como valor predeterminado si 'qty' no se proporciona
        moreinfo = moreinfo.lower() in ['true', '1', 't', 'yes', 'y']  # Convierte a booleano

        # Intentar convertir 'qty' a un entero
        try:
            qty = int(qty_str)
        except ValueError:
            # Si 'qty' no es convertible a un entero, devuelve un error
            response_content = json.dumps({"error": "El parámetro 'qty' debe ser un número entero."})
            return Response(response_content, content_type='application/json', status=400)

        # Llamar al método para generar el código de lote
        isvalid, codegclot = sz.Odoo_CodegcLot.Generate(env=request.env, codegc=codegc, qty=qty, moreinfo=moreinfo)
        
        # Devolver la respuesta basada en si la operación fue válida o no
        if isvalid:
            response_content = json.dumps(codegclot)
            return Response(response_content, content_type='application/json', status=200)
        else:
            # Si la operación no fue válida, incluir el mensaje de error en la respuesta
            response_content = json.dumps({"error": codegclot})
            return Response(response_content, content_type='application/json', status=400)
        
    @http.route('/api/codegclot/ensure/data', type='http', methods=['POST'], auth='public', csrf=False)
    @hlog_api()
    def api_codegclot_ensure_data(self, **kw):
        # Asegurar la extracción de los datos
        data = json.loads(request.httprequest.data)
        
        # Extraer 'entries' del cuerpo de la solicitud JSON
        entries = data.get('entries', [])
        
        isvalid, entries = sz.Odoo_CodegcLot.EnsureData(env=request.env, entries=entries)

        if not isvalid:
            to_return = { 'error':  'Bad Request', 'message': 'Invalid entries found', 'entries': entries }
            return Response(json.dumps(to_return), content_type='application/json', status=400)
        else:
            return Response(json.dumps(entries), content_type='application/json', status=200)