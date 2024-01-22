from .._sx import lib_sx as sx
from ..zlogger_handlers import *
from odoo import models
class sy_OdooModel:
    #def Search(cls, env, model_name, search_field, sortend, retrieve_fields=None):
    #def SearchSimpleIN(cls, env, model_name, search_field, search_values, retrieve_fields=None):
    #JointLeftIntoListDict

    @classmethod
    @hlog_atomic(enable=True,resalt=True)
    def SearchIn(cls, env, model_name, search_field, search_values, retrieve_fields=None):
        """
        Encuentra registros en un modelo de Odoo basándose en una lista de valores para un campo específico, con la opción de especificar campos para recuperar.

        :param env: Entorno de Odoo.
        :param model_name: Nombre del modelo de Odoo (por ejemplo, 'product.product').
        :param search_field: Nombre del campo en el que buscar (por ejemplo, 'default_code').
        :param search_values: Lista de valores para buscar en el campo especificado.
        :param retrieve_fields: Lista opcional de campos para recuperar.
        :return: Lista de diccionarios representando los registros encontrados, conteniendo únicamente los campos especificados si se proporcionan.
        """
        model = env[model_name]
        domain = [(search_field, 'in', search_values)]

        records = []
        if isinstance(model, models.Model):
            records = model.search(domain)

        if retrieve_fields:
            # Procesar campos para extraer los nombres de campos originales si se especifica un cambio de nombre
            fields_to_extract = [field.split(':')[0] for field in retrieve_fields]
            return records.read(fields_to_extract)
        else:
            return records
    
    
    @classmethod
    @hlog_atomic(enable=True,resalt=True)
    def SearchNotIn(cls, env, model_name, search_field, search_values, retrieve_fields=None):
        """
        Encuentra registros en un modelo de Odoo basándose en una lista de valores que "no coincidan" para un campo específico, con la opción de especificar campos para recuperar.

        :param env: Entorno de Odoo.
        :param model_name: Nombre del modelo de Odoo (por ejemplo, 'product.product').
        :param search_field: Nombre del campo en el que buscar (por ejemplo, 'default_code').
        :param search_values: Lista de valores para buscar en el campo especificado.
        :param retrieve_fields: Lista opcional de campos para recuperar.
        :return: Lista de diccionarios representando los registros encontrados, conteniendo únicamente los campos especificados si se proporcionan.
        """
        model = env[model_name]
        domain = [(search_field, 'not in', search_values)]

        records = []
        if isinstance(model, models.Model):
            records = model.search(domain)

        if retrieve_fields:
            # Procesar campos para extraer los nombres de campos originales si se especifica un cambio de nombre
            fields_to_extract = [field.split(':')[0] for field in retrieve_fields]
            return records.read(fields_to_extract)
        else:
            return records

    @classmethod
    @hlog_atomic(enable=True,resalt=False, compact=False)
    def JoinLeft(cls, env, left_data, target_field_on, left_list_filtering_params, model_name, model_field_on, model_retreive_fields, mapping_fields):
        """
        Actualiza una lista de diccionarios con datos provenientes de un modelo de Odoo.

        :param env: Entorno de Odoo para acceder a los modelos.
        :param target_data: Lista de diccionarios que se actualizará.
        :param target_field_on: Clave en target_data utilizada para la coincidencia.
        :param target_filtering_params: Condiciones para filtrar claves únicas de target_data.
        :param model_name: Nombre del modelo de Odoo en el que se buscará.
        :param model_field_on: Clave en el modelo de Odoo utilizada para la coincidencia.
        :param model_retreive_fields: Campos que se recuperarán del modelo de Odoo.
        :param maping_fields: Diccionario que mapea los campos de target_data a los campos del modelo de Odoo.
        :return: Lista actualizada de diccionarios.
        """
        left_filtering = {target_field_on: '#not_empty'}
        # Obtener los valores únicos de target_field_on que cumplan con las condiciones de filtro
        search_values = sx.XListDict.distinct_values(left_data, target_field_on, **left_list_filtering_params)

        # Buscar los registros correspondientes en el modelo de Odoo
        reference_data = cls.SearchIn(env, model_name, model_field_on, search_values, model_retreive_fields)

        # Fusionar los datos de los registros de Odoo en la lista de diccionarios original
        updated_list =  sx.XListDict.join(left_data, target_field_on, reference_data, model_field_on, mapping_fields)

        return updated_list
