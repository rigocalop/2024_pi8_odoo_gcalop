import json
from ..zlogger_handlers import *
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
    @hlog_atomic(enable=True,resalt=True)
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
    @hlog_function(enable=True,resalt=True, compact=False)
    def distinct_values(cls, items_list, distinct_key, **list_filtering_params):
        """
        Recopila valores distintos para una clave dada de una lista de diccionarios, utilizando parámetros de filtrado.

        :param items_list: Lista de diccionarios a ser procesados.
        :param distinct_key: Clave para la cual se recopilarán valores distintos.
        :param filtering_params: Parámetros de filtrado opcionales (clave=valor).
        :return: Lista de valores distintos que cumplen con los parámetros.
        """
        # Filtrar la lista de diccionarios según los parámetros de filtrado proporcionados
        
        logger = ZLogger.get_logger()
        logger.info('items_list: ' + json.dumps(items_list), **list_filtering_params)
        filtered_list = [item for item in items_list if all(
            (value == 'None' and item.get(cond) is None) or
            (value == '#empty' and not item.get(cond)) or
            (value == '#not_empty' and item.get(cond)) or
            (value not in ['None', '#empty', '#not_empty'] and item.get(cond) == value)
            for cond, value in list_filtering_params.items())]

        # Obtener valores distintos para la clave dada
        unique_values = set(item[distinct_key] for item in filtered_list if distinct_key in item)

        # Convertir el conjunto de valores distintos en una lista
        return list(unique_values)

    def _sort(listdict, order_str):
        """
        Ordena una lista de diccionarios basada en una cadena de ordenamiento.

        :param lista: Lista de diccionarios a ordenar.
        :param order_str: Cadena que define cómo se debe ordenar la lista.
            Formato: 'campo1 asc, campo2 desc, ...'
            'asc' para orden ascendente (por defecto),
            'desc' para orden descendente.

        :return: Lista de diccionarios ordenada.
        """

        def get_sort_key(item):
            keys = []
            for field_order in order_str.split(','):
                field_name, _, order_type = field_order.strip().partition(' ')
                value = item
                for key in field_name.split('.'):
                    value = value.get(key) if isinstance(value, dict) else getattr(value, key, None)
                if value is not None and order_type == 'desc':
                    value = -value if isinstance(value, (int, float)) else value[::-1]
                keys.append(value)
            return tuple(keys)
        return sorted(listdict, key=get_sort_key)

    def _filter(listdict, filters):
        """
        Filtra una lista de diccionarios basándose en una lista de criterios de filtro.

        :param lista: Lista de diccionarios a filtrar.
        :param filtros: Lista de tuplas, donde cada tupla contiene un campo, operador y valor para el filtro.

        Cada tupla en 'filtros' tiene la forma (campo, operador, valor), donde:
        - 'campo' es una cadena que especifica la clave en el diccionario (puede ser anidada, separada por '.').
        - 'operador' es una cadena que define cómo se compara el valor del campo con el valor proporcionado.
        - 'valor' es el valor contra el cual se compara el valor del campo.

        Los operadores soportados son:
        - '=' : Igual a
        - '>' : Mayor que
        - '<' : Menor que
        - '>=' : Mayor o igual que
        - '<=' : Menor o igual que
        - 'in' : El valor del campo está en (valor debe ser iterable)
        - 'not in' : El valor del campo no está en (valor debe ser iterable)
        - 'like' : Similar a (para cadenas)
        - 'empty' : El campo está vacío (None, '', [])
        - 'not empty' : El campo no está vacío

        :return: Lista de diccionarios que cumplen con todos los criterios de filtro.
        """
        def meets_conditions(element, filtro):
            field, operator, value = filtro

            # Obtain the value of the field in the element
            current_value = element
            for key in field.split('.'):
                current_value = current_value.get(key) if isinstance(current_value, dict) else getattr(current_value, key, None)

            # Define what is considered an "empty" value
            def is_empty(v):
                # A value is considered empty if it is None, an empty string, or an empty list
                return v is None or v == '' or v == []

            # Apply the comparison operator
            if operator == '=' and current_value != value:
                return False
            elif operator == '>' and current_value <= value:
                return False
            elif operator == '<' and current_value >= value:
                return False
            elif operator == '>=' and current_value < value:
                return False
            elif operator == '<=' and current_value > value:
                return False
            elif operator == 'in' and current_value not in value:
                return False
            elif operator == 'not in' and current_value in value:
                return False
            elif operator == 'like' and value not in current_value:
                # Assuming both value and current_value are strings
                return False
            elif operator == 'empty' and not is_empty(current_value):
                return False
            elif operator == 'not empty' and is_empty(current_value):
                # Retorna False si el campo está vacío cuando se espera que no lo esté
                return False
            return True

        return [element for element in listdict if all(meets_conditions(element, filtro) for filtro in filters)]

    def _fields_mapping(listdict, fields=None, mapping=None):
        """
        Extrae y opcionalmente renombra campos de una lista de diccionarios.

        :param listdict: Lista de diccionarios de donde se extraerán los datos.
        :param fields: Lista de campos a extraer de cada diccionario o None para todos los campos.
        :param mapping: Diccionario opcional para mapear nombres de campos a nuevos nombres.
                        Formato: {nombre_campo_original: nuevo_nombre_campo}
        :return: Lista de diccionarios con campos extraídos y renombrados.
        """

        def rename_fields(record, fields_to_extract, field_mapping):
            return {field_mapping.get(field, field): record.get(field) for field in fields_to_extract}

        # Determinar campos a extraer
        fields_to_extract = fields if fields is not None else (list(listdict[0].keys()) if listdict else [])

        return [rename_fields(element, fields_to_extract, mapping or {}) for element in listdict]

    def _distinct(listdict):
        """
        Devuelve una lista de tuplas con combinaciones únicas de valores para todas las claves en una lista de diccionarios.

        :param listdict: Lista de diccionarios a procesar.
        :return: Una lista de tuplas, cada una representando una combinación única de valores.
        """
        unique_values = set()
        for dict_item in listdict:
            # Crea una tupla con los valores de todas las claves en el diccionario
            value_tuple = tuple(dict_item.values())
            unique_values.add(value_tuple)

        return list(unique_values)
    class OperationNotSupportedError(Exception):
        """Excepción para operaciones no soportadas en el agrupamiento y procesamiento."""
    pass

    @classmethod
    def _group_and_process(cls, list_dict, grouping_fields, operations):
        """
        Agrupa y procesa filas en una lista de diccionarios según operaciones especificadas.

        :param list_dict: Lista de diccionarios a procesar.
        :param grouping_fields: Campos por los cuales se realizará la agrupación.
        :param operations: Lista de tuplas (field, function, new_field) para procesar y renombrar campos.
        :return: Lista de diccionarios con los resultados agrupados y procesados.
        """
        result = {}

        for item in list_dict:
            grouping_key = tuple(item[field] for field in grouping_fields)
            if grouping_key not in result:
                result[grouping_key] = {}
                for field, function, new_field in operations:
                    result[grouping_key][new_field] = []

            for field, function, new_field in operations:
                if function == 'sum':
                    result[grouping_key][new_field].append(item[field])
                elif function == 'count':
                    result[grouping_key][new_field].append(1)
                elif function == 'array':
                    result[grouping_key][new_field].append(item[field])
                else:
                    raise cls.OperationNotSupportedError(f"Operación '{function}' no soportada.")

        # Realizar las operaciones finales
        for key, values in result.items():
            for field, function, new_field in operations:
                if function == 'sum':
                    result[key][new_field] = sum(values[new_field])
                elif function == 'count':
                    result[key][new_field] = len(values[new_field])
                # No se necesita una operación final para 'array'

        # Crear la lista final de resultados
        return [
            dict(zip(grouping_fields + [new_field for _, _, new_field in operations],
                    key + tuple(result[key][new_field] for _, _, new_field in operations)))
            for key in result
        ]

    def _fields_extract(listdict, fields):
        """
        Extrae campos específicos de una lista de diccionarios.

        :param list_dict: Lista de diccionarios de donde se extraerán los datos.
        :param fields: Lista de campos a extraer de cada diccionario o None para todos los campos.
        :return: Lista de diccionarios con solo los campos especificados.
        """
        fields_to_extract = fields if fields is not None else (list(listdict[0].keys()) if listdict else [])

        return [{field: record.get(field) for field in fields_to_extract} for record in listdict]

    def _fields_rename(listdict, mapping):
        """
        Renombra campos de una lista de diccionarios según un mapeo dado.

        :param list_dict: Lista de diccionarios a procesar.
        :param mapping: Diccionario para mapear nombres de campos a nuevos nombres.
                        Formato: {nombre_campo_original: nuevo_nombre_campo}
        :return: Lista de diccionarios con campos renombrados.
        """
        return [{mapping.get(field, field): value for field, value in record.items()} for record in listdict]
    


    @classmethod
    @hlog_function(enable=True, resalt=True, compact=False)
    def Select(cls, listdict, fields=None, filters=None, order=None, mapping=None):
        """
        Selecciona y procesa filas en una lista de diccionarios basándose en parámetros de selección.

        :param listdict: Lista de diccionarios a procesar.
        :param fields: Lista de campos a extraer de cada diccionario o None para todos los campos.
        :param filters: Lista de tuplas, donde cada tupla contiene un campo, operador y valor para el filtro.
        :param order: Cadena que define cómo se debe ordenar la lista.
            Formato: 'campo1 asc, campo2 desc, ...'
            'asc' para orden ascendente (por defecto),
            'desc' para orden descendente.
        :param distinct: Booleano que indica si se deben devolver solo valores distintos.
        :return: Lista de diccionarios que cumplen con todos los criterios de filtro.
        """
        # Aplicar filtros
        if filters:
            listdict = cls._filter(listdict, filters)

        # Ordenar
        if order:
            listdict = cls._sort(listdict, order)

        # Extraer campos
        if fields:
            listdict = cls._fields_extract(listdict, fields)
            
        # Renombrar campos
        if mapping:
            listdict = cls._fields_rename(listdict, mapping)

        return listdict
        
    
    @classmethod
    @hlog_function(enable=True, resalt=True, compact=False)
    def SelectGroup(cls, listdict, grouping_fields, grouping_operations, filters=None, order=None, mapping=None):
        """
        Selecciona y procesa filas en una lista de diccionarios basándose en parámetros de selección.

        Este método permite una selección avanzada y procesamiento de datos estructurados en forma de listas de diccionarios.
        Se pueden aplicar filtros, realizar agrupaciones basadas en campos específicos, ordenar los resultados y renombrar campos
        según sea necesario.

        :param listdict: Lista de diccionarios a procesar.
        :param grouping_fields: Campos por los cuales se realizará la agrupación.
        :param grouping_operations: Operaciones de agrupación a aplicar, en formato de tuplas (campo, función, nuevo_campo).
        :param filters: Lista opcional de tuplas para filtrar los datos (campo, operador, valor).
        :param order: Cadena opcional que define cómo se debe ordenar la lista ('campo1 asc, campo2 desc, ...').
        :param mapping: Diccionario opcional para mapear nombres de campos a nuevos nombres.
        :return: Lista de diccionarios que cumplen con todos los criterios especificados.
        """
        # Aplicar filtros
        if filters:
            listdict = cls._filter(listdict, filters)
        
        # Agrupar y procesar
        listdict = cls._group_and_process(listdict, grouping_fields, grouping_operations)

        # Ordenar
        if order:
            listdict = cls._sort(listdict, order)

        # Renombrar campos
        if mapping:
            listdict = cls._fields_rename(listdict, mapping)

        return listdict


# # Ejemplo de uso
# empleados = [
#     {'nombre': 'Ana', 'edad': 30, 'habilidades': ['Python', 'Odoo']},
#     {'nombre': 'Luis', 'edad': 25, 'habilidades': []}
# ]

# # Definir filtros como lista de tuplas
# filtros = [('edad', '<=', 30), ('habilidades', 'empty', None)]

# # Aplicar filtros
# empleados_filtrados = filtrar_lista_por_tuplas(empleados, filtros)
