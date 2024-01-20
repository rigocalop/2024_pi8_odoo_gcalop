import json
from .._sx import sx_xlist
class sx_xobject:    
    @staticmethod
    def clone(object_to_clone, fields_to_clone, fields_to_set=None):
        """
        Clona un objeto de Odoo.

        :param object_to_clone: El objeto de Odoo que se va a clonar.
        :param fields_to_clone: Lista de campos que se desean clonar, separados por comas. 
                                Cada campo puede tener un mapeo origen:destino.
        :return: Diccionario con los datos clonados.
        """
        list_fields_to_clone= sx_xlist.convert(fields_to_clone)
        to_return = {}
        for field in list_fields_to_clone:
            # Dividir el campo en origen y destino si existe ':', si no, son iguales
            field_parts = field.split(':')
            field_orig = field_parts[0].strip()
            field_dest = field_parts[1].strip() if len(field_parts) > 1 else field_orig

            # Asignar el valor del campo origen al campo destino
            to_return[field_dest] = object_to_clone[field_orig]
        
        to_return.update(fields_to_set or {})
        # Retornar el diccionario con los datos clonados
        return to_return
    
    def tryget(object, key, default_value=None):
        try:
            to_return = object[key]
            return to_return
        except Exception:
            return default_value