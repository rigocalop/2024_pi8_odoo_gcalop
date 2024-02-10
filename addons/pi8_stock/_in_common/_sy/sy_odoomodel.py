from .._sx import lib_sx as sx
from ..zlogger_handlers import *
from ..zlogger import ZLogger
from odoo import models
class sy_OdooModel:

    @classmethod
    @hlog_atomic()
    def records_to_listdict(cls, model, records):
        """
        Convierte los registros de Odoo en una lista de diccionarios.

        Args:
        - model_name: El nombre del modelo de Odoo del que se están recuperando los registros.
        - records: Registros de Odoo recuperados del modelo.

        Returns:
        - Una lista de diccionarios que representan los registros en el formato especificado.
        """
        listdict = []
        logger = ZLogger.get_logger()
        
        # Obtiene todos los campos del modelo
        fields = model.fields_get()

        # Extrae los nombres de los campos
        all_fields = list(fields.keys())
        
        # Iterar sobre los registros
        for record in records:
            record_dict = {}
            # Iterar sobre los campos que queremos extraer
            for field_name in all_fields:
                # Obtener el valor del campo del registro
                field_value = record[field_name]
                # Convertir valores especiales de Odoo a tipos de datos estándar si es necesario
                try:
                    if isinstance(field_value, models.Model):
                        record_dict[field_name] = field_value.id
                    else:
                        record_dict[field_name] = field_value
                except Exception as e:
                    logger.warning(f"Error al convertir el campo {field_name}: {e}")    
            listdict.append(record_dict)
        return listdict


    @classmethod
    @hlog_atomic()
    def get_model_fields(self, model_name):
        """
        Devuelve una lista de los nombres de los campos para un modelo dado en Odoo.

        :param model_name: El nombre técnico del modelo de Odoo del que se extraerán los campos.
        :return: Lista de nombres de campos del modelo especificado.
        """
        # Obtiene una referencia al modelo especificado
        model = self.env[model_name]

        # Obtiene todos los campos del modelo
        fields = model.fields_get()

        # Extrae los nombres de los campos
        field_names = list(fields.keys())

        return field_names

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
        
        listdict = cls.records_to_listdict(model, records)

        if fields:
            listdict = sx.XListDict.select_fields(listdict,fields)

        if mapping_fields:
            listdict = sx.XListDict.mapping_fields(listdict=listdict,mapping=mapping_fields, remove_original=True)



        return listdict
    
    
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

 
