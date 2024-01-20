import json
class sx_XListDict:
    # @classmethod
    # def getDistinctKeys(cls, list_dicts, key_field, **conditions):
    #     """
    #     Obtains unique values for a specific key from a list of dictionaries, applying a filter.

    #     :param list_dicts: List of dictionaries to process.
    #     :param key_field: The key for which unique values will be extracted.
    #     :param conditions: Filtering conditions (key=value).
    #     :return: A set of unique values that meet the conditions.
    #     """
    #     # Filter the list of dictionaries according to the provided conditions
    #     filtered_list = [detail for detail in list_dicts if all(detail.get(cond) == value for cond, value in conditions.items())]

    #     # Obtain unique values for the given key
    #     unique_values = set(detail[key_field] for detail in filtered_list if key_field in detail)

    #     # Convert the set of unique values to a list
    #     return list(unique_values)
    
    @classmethod
    def join(cls, target_data, target_field_on, reference_data, reference_field_on, mapping_fields):
        """
        Realiza una operación de 'join' entre dos listas de diccionarios basada en claves coincidentes.

        Esta función combina datos de dos listas de entradas de datos (cada entrada siendo un diccionario) basándose en claves coincidentes.
        Los campos especificados de la lista de referencia se añaden o actualizan en la lista objetivo según el mapeo de campos proporcionado.

        :param target_data: Lista de entradas de datos (diccionarios) que serán actualizados (objetivo).
        :param target_field_on: Clave en los datos objetivo utilizada para el emparejamiento.
        :param reference_data: Lista de referencia de entradas de datos (diccionarios) de donde se unirán los datos.
        :param reference_field_on: Clave en los datos de referencia utilizada para el emparejamiento.
        :param mapping_fields: Diccionario que mapea los campos objetivo a los campos de referencia.
        :return: Lista actualizada de entradas de datos (datos objetivo).
        """
        # Crear un mapa de referencia utilizando reference_field_on
        reference_map = {record[reference_field_on]: record for record in reference_data if reference_field_on in record}

        # Fusionar los datos de la referencia en los datos objetivo
        for item in target_data:
            matching_record = reference_map.get(item.get(target_field_on))
            if matching_record:
                for target_field, reference_field in mapping_fields.items():
                    if '[' in reference_field and ']' in reference_field:
                        # Extraer el nombre del campo y el índice
                        field_name, index = reference_field.split('[')
                        index = int(index.rstrip(']'))

                        # Comprobar si el campo existe y es una lista o tupla
                        if field_name in matching_record and isinstance(matching_record[field_name], (list, tuple)):
                            # Extraer el valor usando el índice
                            item[target_field] = matching_record[field_name][index]
                    else:
                        if reference_field in matching_record:
                            item[target_field] = matching_record[reference_field]

        return target_data

    @classmethod
    def distinct_values(cls, items_list, distinct_key, **filtering_params):
        """
        Recopila valores distintos para una clave dada de una lista de diccionarios, utilizando parámetros de filtrado.

        :param items_list: Lista de diccionarios a ser procesados.
        :param distinct_key: Clave para la cual se recopilarán valores distintos.
        :param filtering_params: Parámetros de filtrado opcionales (clave=valor).
        :return: Lista de valores distintos que cumplen con los parámetros.
        """
        # Filtrar la lista de diccionarios según los parámetros de filtrado proporcionados
        filtered_list = [item for item in items_list if all(
            item.get(cond) != None if value == 'not None' else item.get(cond) == value
            for cond, value in filtering_params.items())]

        # Obtener valores distintos para la clave dada
        unique_values = set(item[distinct_key] for item in filtered_list if distinct_key in item)

        # Convertir el conjunto de valores distintos en una lista
        return list(unique_values)
