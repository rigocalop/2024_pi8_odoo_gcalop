from .._sx import lib_sx as sx
from ..zlogger_handlers import *
from odoo import models
class sy_OdooModel:
    #def Search(cls, env, model_name, search_field, sortend, retrieve_fields=None):
    #def SearchSimpleIN(cls, env, model_name, search_field, search_values, retrieve_fields=None):
    #JointLeftIntoListDict

    @classmethod
    @hlog_atomic()
    def SearchIn(cls, env, model_name, fields, search_field, search_values, mapping_fields=None):
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
        search_values = sx.XList.ensure(search_values)
        domain = [(search_field, 'in', search_values)]

        records = []
        if isinstance(model, models.Model):
            records = model.search(domain)

        if fields:
            # Procesar campos para extraer los nombres de campos originales si se especifica un cambio de nombre
            fields_to_extract = [field.split(':')[0] for field in fields]
            records = records.read(fields_to_extract)
        
        if mapping_fields:
            records = sx.XListDict.mapping_fields(listdict=records,mapping=mapping_fields)

        return records
    
    
    @classmethod
    @hlog_atomic(enable=True,resalt=True)
    def SearchNotIn(cls, env, model_name, fields, search_field, search_values):
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

        if fields:
            # Procesar campos para extraer los nombres de campos originales si se especifica un cambio de nombre
            fields_to_extract = [field.split(':')[0] for field in fields]
            return records.read(fields_to_extract)
        else:
            return records

 
