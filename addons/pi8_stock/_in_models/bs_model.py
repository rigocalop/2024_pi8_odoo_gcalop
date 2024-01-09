from odoo import api, models
import json
from datetime import datetime
class bs_model(models.AbstractModel):
    _name = 'bs.model'
    _description = 'Modelo Base PI8[]'
    
    @staticmethod
    def generar_json_del_objeto(self, objeto):
        if objeto:
            # Crear un diccionario con los nombres y valores de los campos del objeto
            data = {campo: getattr(objeto, campo) for campo in objeto._fields}

            # Filtrar los campos que no son serializables (como los campos Many2one)
            # y convertirlos a un formato serializable, por ejemplo, obtener solo el ID o el nombre.
            for campo, valor in data.items():
                if hasattr(valor, 'id'):
                    data[campo] = valor.id  # O puedes usar valor.name_get()[0][1] si necesitas el nombre

            # Convertir el diccionario a una cadena JSON
            return json.dumps(data)
        else:
            return json.dumps({'error': 'Objeto no encontrado'})
        
    # @staticmethod
    # def ckfield(self, key, field_name=None):
    #     # Revisar si el objeto está en caché
    #     model_name = self._name
    #     model = self.env[model_name]
    #     cache_key = (model_name, key)
    #     item_obj = self.env.cache.contains(model, model._fields['key'])
    #     # item_obj = self.env.cache.get(cache_key)
    #     if not item_obj:
    #         # Si no está en caché, buscar en la base de datos
    #         item_obj = model.search([('key', '=', key)], limit=1)
            
    #         json_data = bs_model.generar_json_del_objeto(self, item_obj)

    #         if item_obj:
    #             # Almacenar el objeto completo en caché
    #             self.env.cache.set(json_data,item_obj._fields['key'], item_obj.key)

    #     if item_obj and field_name:
    #         # Si se proporcionó field_name y el objeto existe, devolver el valor del campo
    #         return getattr(item_obj, field_name, None)

    #     # Devolver el objeto completo o None si no se encontró
    #     return item_obj
    @staticmethod
    def ckfield(self, key, field_name=None):
        model = self.env[self._name]
        item_obj = model.search([('key', '=', key)], limit=1)

        if item_obj:
            fields_data = item_obj.read()[0]  # read() devuelve una lista de diccionarios
            direct_fields = {}

            for key, value in fields_data.items():
                # Convertir campos datetime a su representación ISO
                if isinstance(value, datetime):
                    direct_fields[key] = value.isoformat()
                # Incluir campos que no son relaciones (modelos) ni listas
                elif not isinstance(value, models.BaseModel) and not isinstance(value, list):
                    direct_fields[key] = value

            # Convertir el diccionario a una cadena JSON
            # json_data = json.dumps(direct_fields)
            return direct_fields
        else:
            return None