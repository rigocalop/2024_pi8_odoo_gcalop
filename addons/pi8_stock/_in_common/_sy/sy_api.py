from .._sx import lib_sx as sx
from ..zlogger import ZLogger
from ..zlogger_handlers import *
import re
from odoo.http import request as odoo_request


class sy_Api:
    @classmethod
    def prmBool(cls, name, default=False, required=False):
        # Retrieve a boolean parameter from the request
        param_value = odoo_request.params.get(name)
        if param_value is None:
            if required:
                raise ApiException(f"El parametro *{name}* es requerido.")
            else:
                return default
        # Ensure the parameter value is treated as a boolean
        true_values = ['True', 'true', '1']
        false_values = ['False', 'false', '0']
        if param_value in true_values:
            return True
        elif param_value in false_values:
            return False
        else:
            # If the value does not match expected boolean values, raise an error
            raise ApiException(f"El valor del parametro *{name}* debe ser booleano (True, true, 1, False, false, 0), pero se recibio: {param_value}.")
    
    @classmethod
    def prmStr(cls, name, default=None, required=False):
        # Implementation for prmStr, assuming it's correct as provided
        to_return = odoo_request.params.get(name)
        if to_return is None:
            if required:
                raise ApiException(f"El parametro *{name}*  es requerido.")
            else:
                return default
        return to_return
        
    @classmethod
    def prmInt(cls, name, default=0):
        param_value = odoo_request.params.get(name)
        if param_value is None:
            return default
        
        try:
            # Attempt to convert the parameter to an integer
            return int(param_value)
        except ValueError:
            # If conversion fails, raise an ApiParamException
            raise ApiException(f"Parameter '{name}' must be an integer.")
    
    @classmethod
    def param_boolean(cls, param_name, default=False):
        """
        Procesa un parámetro booleano de la URL y retorna un valor booleano.
        Acepta '1', 'true', 't' como verdaderos y '0', 'false', 'f' como falsos.
        Ahora recibe el objeto request directamente.

        Parámetros:
        param_name (str): Nombre del parámetro a procesar.
        default (bool): Valor por defecto si el parámetro no está presente o es inválido.
        request (werkzeug.local.LocalProxy): Objeto request de la solicitud actual.

        Retorna:
        bool: El valor booleano del parámetro.
        """
        params = odoo_request.params
        param_value = str(params.get(param_name, '')).lower()  # Convertir el valor a minúsculas para estandarizar
        true_values = ['1', 'true', 't']  # Lista de valores que representan verdadero
        false_values = ['0', 'false', 'f']  # Lista de valores que representan falso

        if param_value in true_values:
            return True
        elif param_value in false_values:
            return False
        else:
            return default

    @classmethod
    def ApiResponse(cls, is_success, data=None, message_error="Error", status_success=200, status_error=400, message_success="Success"):
        """
        Genera una respuesta HTTP para la API basada en el éxito o falla de la operación.

        Parámetros:
        is_success (bool): Indica si la operación fue exitosa.
        data (dict, opcional): Los datos a incluir en la respuesta. Puede ser información de éxito o detalles de error.
        status_success (int): Código de estado HTTP para respuestas exitosas.
        status_error (int): Código de estado HTTP para respuestas de error.
        message_success (str): Mensaje para respuestas exitosas.
        message_error (str): Mensaje para respuestas de error.

        Retorna:
        Response: Objeto Response de Odoo listo para ser retornado por un controlador HTTP.
        """
        if is_success:
            response_content = data
            status=status_success
        else:
            response_content = {
                'status': 'error',
                'message': message_error,
                'data': data
            }
            status = status_error
        
  
        
        try:
            # Attempt to convert the parameter to an integer
            response_content = json.dumps(response_content)
        except Exception:
            response_content = "ERROR NO CONTROLADO EN EL RETORNO DEL CONTENT"
            # If conversion fails, raise an ApiParamException

        return Response(response_content, content_type='application/json', status=status)

    