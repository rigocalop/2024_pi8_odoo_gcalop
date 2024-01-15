import os
from datetime import datetime, timedelta
import json
from odoo import api, models


def cache_model_search(func):
    cache = {}
    last_reset_time = datetime.now()
    def wrapper(self, key, *args, **kwargs):
        nonlocal last_reset_time

        # Leer la variable de entorno para el tiempo de reset del caché
        reset_seconds = int(os.getenv('CACHE_RESET_TIME', '3600'))  # Valor por defecto de 3600 segundos (1 hora)
        
        # Verificar si es tiempo de resetear el caché
        if datetime.now() >= last_reset_time + timedelta(seconds=reset_seconds):
            cache.clear()
            last_reset_time = datetime.now()

        # Clave del caché
        module_name = self.__class__.__module__
        cache_key = (module_name, key)

        if cache_key in cache:
            return cache[cache_key]

        # Realizar la búsqueda y procesamiento aquí en lugar de en ckfield
        model = self.env[self._name]
        
        item_obj = model.search([('key', '=', key)], limit=1)

        if item_obj:
            fields_data = item_obj.read()[0]  # Procesamiento de los datos
            direct_fields = {}

            for field_key, value in fields_data.items():
            # Convertir campos datetime a su representación ISO
                if isinstance(value, datetime):
                    direct_fields[field_key] = value.isoformat()
            # Incluir campos que no son relaciones (modelos) ni listas
                elif not isinstance(value, models.BaseModel) and not isinstance(value, list):
                    direct_fields[field_key] = value
            result = direct_fields  # Resultado procesado
        else:
            result = None
        
        cache[cache_key] = result
        return result
    return wrapper

