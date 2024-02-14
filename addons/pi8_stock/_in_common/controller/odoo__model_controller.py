import json
from ..zlogger_handlers import *
from ..zlogger_handlers import hlog_api
from odoo import http, _
from odoo.http import request, Response
from .._sy import lib_sy as sy
from .._sx import lib_sx as sx
from .._sz import lib_sz as sz
from odoo import fields as odoo_fields
from collections import OrderedDict


class Odoo_Model_Controller(http.Controller):
    @http.route('/api/odoo/model/fields', type='http', methods=['GET'], auth='public', csrf=False)
    @hlog_api()
    def api_odoo_model_fields(self, **kw):
        # Asegurar la extracción de los datos
        model = request.params.get('model', '')  # Proporciona un valor predeterminado si 'codegc' no se encuentra
        isvalid, info =  sz.Odoo_ORM.model_fields(request.env, model)
        

        if not isvalid:
            to_return = { 'error':  'Bad Request', 'message': 'Invalid entries found', 'entries': info }
            return Response(json.dumps(to_return), content_type='application/json', status=400)
        else:
            return Response(json.dumps(info), content_type='application/json', status=200)

    @http.route(['/api/odoo/model/record/<model>', '/api/odoo/model/record/<model>/<int:record_id>'], type='http', methods=['GET'], auth='public', csrf=False)
    @hlog_api()
    def api_get_odoo_model_record(self, model, record_id=None, **kw):
        """
        Obtiene un registro específico por su ID de un modelo de Odoo.
        """
        # Llamamos a una función que busca el registro por su ID.
        record = sz.Odoo_ORM.model_record_by_id(request.env, model, record_id)

        if record:
            # Convertimos el registro a un diccionario para la respuesta JSON.
            # Nota: Debes implementar 'record_to_dict' para convertir el registro de Odoo a un diccionario.
            # record_data = record
            record_data = sz.Odoo_ORM.record_fields_and_values(record,include_field_types=False)
            return Response(json.dumps(record_data), content_type='application/json', status=200)
        else:
            # Manejo de error si el registro no se encuentra
            error_response = {
                'error': 'Not Found',
                'message': f"Record with ID {record_id} not found in model '{model}'."
            }
            return Response(json.dumps(error_response), content_type='application/json', status=404)



