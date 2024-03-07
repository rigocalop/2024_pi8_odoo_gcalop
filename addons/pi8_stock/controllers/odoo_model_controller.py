from .._in_common.zlogger_handlers import hlog_api
from odoo import http, _
from odoo.http import request
from .._in_common._sy import lib_sy as sy

class Odoo_Model_Controller(http.Controller):
    @http.route('/api/odoo/model/fields', type='http', methods=['GET'], auth='public', csrf=False)
    @hlog_api()
    def api_odoo_model_fields(self, **kw):
        # Asegurar la extracción de los datos
        model = request.params.get('model', '')  # Proporciona un valor predeterminado si 'codegc' no se encuentra
        
        # Llamamos a una función que busca el registro por su ID.
        is_success, data =  sy.Odoo.Model.fields(request.env, model)
        return sy.Api.ApiResponse(is_success, data, message_error= f'Invalid entries found {data}')

    @http.route(['/api/odoo/model/record/<model>', '/api/odoo/model/record/<model>/<int:record_id>'], type='http', methods=['GET'], auth='public', csrf=False)
    @hlog_api()
    def api_get_odoo_model_record(self, model, record_id=None, **kw):
        """
        Obtiene un registro específico por su ID de un modelo de Odoo.
        """
        # Convertir el parámetro 'types' de la URL a booleano
        types = sy.Api.param_boolean('types')

        # Llamamos a una función que busca el registro por su ID.
        is_success, record = sy.Odoo.Model.record_by_id(request.env, model, record_id, types= types)
        return sy.Api.ApiResponse(is_success, record, message_error= f"Record with ID {record_id} not found in model '{model}'.", status_error=404)


    