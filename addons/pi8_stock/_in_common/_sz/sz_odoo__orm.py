from ..zlogger_handlers import *
from odoo import models, _
from ..zlogger import ZLogger
from .._sy import lib_sy as sy
from .._sx import lib_sx as sx
import re
from odoo import fields as odoo_fields
from collections import OrderedDict

class sz_Odoo_ORM:
        
    # Diccionario de caché a nivel de clase
    codegc_cache = {}

    @classmethod
    @hlog_function()
    def first_record_id(cls, env, model):
        """
        Obtiene el primer ID de un registro para un modelo específico en Odoo.

        Parámetros:
        model_env (odoo.api.Environment): El entorno de Odoo, usado para acceder a los modelos.
        model_name (str): El nombre técnico del modelo del cual se quiere obtener el primer ID.

        Retorna:
        int/None: El ID del primer registro encontrado para el modelo especificado, o None si no se encontraron registros.
        """
        # Realizar la búsqueda del primer registro del modelo especificado
        record_ids = env[model].search([], limit=1)

        # Verificar si se encontró algún registro y retornar su ID
        if record_ids:
            return record_ids.id
        else:
            # Retornar None si no se encontraron registros
            return None
    
    @classmethod
    @hlog_function()
    def model_fields(cls, env, model):
        """
        Obtiene los campos de un modelo específico en Odoo y los ordena por nombre.

        Parámetros:
        env (odoo.api.Environment): El entorno de Odoo.
        model_name (str): El nombre técnico del modelo (por ejemplo, 'res.partner').

        Retorna:
        tuple: (bool, dict/str) Un booleano que indica éxito o falla, y un diccionario ordenado donde las claves son los nombres de los campos y los valores son los tipos de los campos, o un mensaje de error si el modelo no existe.
        """
        # Asegurarse de que el modelo existe
        if not env['ir.model'].search([('model', '=', model)]):
            return False, f"El modelo '{model}' no existe."

        # Obtener el objeto del modelo
        modelo = env[model]
        
        # Obtener los campos del modelo
        campos = modelo.fields_get()

        # Ordenar los campos por nombre y crear un diccionario con el nombre del campo y su tipo
        campos_simplificados = {campo: datos['type'] for campo, datos in sorted(campos.items())}

        return True, campos_simplificados
    

    @classmethod
    @hlog_atomic()
    def record_fields_and_values(cls, record, include_field_types=True):
        """
        Extrae los campos y sus valores de un registro de Odoo, ordenados por el nombre del campo.
        Captura y registra excepciones para campos con errores al acceder.
        Opcionalmente incluye el tipo de cada campo en la salida y en los registros de errores.

        Parámetros:
        record (odoo.models.BaseModel): Un registro de Odoo.
        include_field_types (bool): Indica si se debe incluir el tipo de campo en la salida y los registros de error.

        Retorna:
        OrderedDict: Un diccionario ordenado con los nombres de los campos como claves, sus valores como valores,
            tipos de campos si se solicita, y detalles de errores para campos con excepciones, incluido el tipo de campo.
        """
        # Asegurarse de que el registro existe
        if not record.exists():
            return OrderedDict()

        # Preparar un diccionario ordenado para mantener los campos ordenados por nombre
        record_data = OrderedDict()
        error_data = OrderedDict()
        sorted_fields = sorted(record._fields.items(), key=lambda item: item[0])

        for field_name, field in sorted_fields:
            try:
                value = getattr(record, field_name)
                field_data = {
                    'value': None,
                    'type': field.type if include_field_types else 'unknown'
                }
                if isinstance(field, odoo_fields.Date) or isinstance(field, odoo_fields.Datetime):
                    field_data['value'] = value and value.isoformat() or False
                elif hasattr(value, 'id'):
                    field_data['value'] = value.name_get()[0][1] if hasattr(value, 'name_get') else value.id
                else:
                    field_data['value'] = value
                record_data[field_name] = field_data['value'] if not include_field_types else field_data
            except Exception as e:
                error_info = {
                    'error': str(e),
                    'type': field.type
                }
                error_data[field_name] = error_info

        if error_data:
            record_data['_errors'] = error_data

        return record_data
    
    
    
    @classmethod
    @hlog_function()
    def model_record_by_id(cls, env, model, record_id=None):
        """
        Obtiene un registro por su ID principal en un modelo específico de Odoo.

        Parámetros:
        env (odoo.api.Environment): El entorno de Odoo.
        model_name (str): El nombre técnico del modelo (por ejemplo, 'res.partner').
        record_id (int): El ID principal del registro a obtener.

        Retorna:
        odoo.models.BaseModel/None: El registro obtenido por su ID, o None si el registro no existe.
        """
        
        # Realizar la búsqueda del primer registro del modelo especificado
        record = None
        if not record_id:
            record = env[model].search([], limit=1)
        else: 
            record = env[model].browse(record_id)
        
        # Verificar si el registro existe
        if record.exists():
            return record
        else:
            return None