import json
from ..zlogger_handlers import *
class sx_XListDict:
    @classmethod
    def ensure_list(cls, value):
        if not isinstance(value, list):
            return [value]
        return value

    @classmethod
    def ensure_string(cls, value):
        if isinstance(value, list) and len(value) == 1:
            return value[0]
        return value  # O manejar el error si value no es una lista con un solo elemento
    
    # @classmethod
    # @hlog_atomic()
    # def select_fields(listdict, fields_to_select):
    #     """
    #     Procesa los registros en formato listdict para seleccionar los campos especificados.

    #     Args:
    #     - listdict: Lista de diccionarios representando los registros.
    #     - fields_to_select: Lista de nombres de campos a seleccionar.

    #     Returns:
    #     - Lista de diccionarios representando los registros con solo los campos seleccionados.
    #     """
    #     if not fields_to_select:
    #         return listdict

    #     # Iterar sobre los registros y seleccionar solo los campos especificados
    #     selected_records = []
    #     for record in listdict:
    #         selected_record = {}
    #         for field in fields_to_select:
    #             selected_record[field] = record.get(field)
    #         selected_records.append(selected_record)

    #     return selected_records

    
    @classmethod
    @hlog_atomic()
    def join(cls, target_data, target_field_on, reference_data, reference_field_on, join_fields):
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
        target_field_on = cls.ensure_string(target_field_on)
        # Crear un mapa de referencia utilizando reference_field_on
        reference_map = {record[reference_field_on]: record for record in reference_data if reference_field_on in record}

        # Fusionar los datos de la referencia en los datos objetivo
        for item in target_data:
            matching_record = reference_map.get(item.get(target_field_on))
            if matching_record:
                for reference_field, target_field in join_fields.items():
                    if target_field == None:
                        target_field = reference_field
                        
                    if '[' in reference_field and ']' in reference_field:
                        # Extraer el nombre del campo y el índice
                        field_name, index = target_field.split('[')
                        index = int(index.rstrip(']'))

                        # Comprobar si el campo existe y es una lista o tupla
                        if field_name in matching_record and isinstance(matching_record[field_name], (list, tuple)):
                            # Extraer el valor usando el índice
                            item[target_field] = matching_record[field_name][index]
                        else:
                            raise KeyError(f"Campo '{field_name}' no encontrado o no es una lista/tupla.")
                        
                    else:
                        if reference_field in matching_record:
                            item[target_field] = matching_record[reference_field]
                        else:
                            raise KeyError(f"Campo de referencia '{reference_field}' no encontrado en el registro de referencia.")

        return target_data
    
    
    
    @classmethod
    def extract_field_value(cls, record, field):
        """
        Extrae un valor de un campo, manejando campos normales y campos de lista.
        """
        if '[' in field and ']' in field:
            field_name, index = field.split('[')
            index = int(index.rstrip(']'))
            if field_name in record and isinstance(record[field_name], (list, tuple)):
                try:
                    return record[field_name][index]
                except IndexError:
                    return None
            return None
        return record.get(field)


    @classmethod
    @hlog_function(default_error='Error en los parametros de _sort, el formato apropiado es un simple string con el nombre del campo a ordenar, y separados por comas.. Ejemplo: "name asc, date, id desc"')
    def sort(cls, listdict, order_str):
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


    def _flatten_tuple_array(array):
        """ Aplana un array de tuplas de un solo elemento en un array simple. """
        if not array:
            return array
        if isinstance(array[0], tuple):
            return [item[0] for item in array if len(item) == 1]
        return array

    @hlog_atomic()
    def filter(listdict, filters):
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
        @hlog_atomic(default_error='Error en los parametros de filtro...')
        def meets_conditions(element, filtro):
            field, operator, value = filtro

            # Obtener el valor del campo en el elemento
            current_value = element[field] if isinstance(element, dict) else element

            # Definir qué se considera un valor "vacío"
            def is_empty(v):
                return v is None or v == '' or v == []

            # Definir una función interna para aplanar un array de tuplas de un solo elemento
            def flatten_tuple_array(array):
                if not array:
                    return array
                if isinstance(array[0], tuple):
                    return [item[0] for item in array if len(item) == 1]
                return array

            # Aplanar el array de tuplas para 'in' y 'not in'
            if operator in ['in', 'not in']:
                value = flatten_tuple_array(value)

            # Aplicar el operador de comparación
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
                return False
            return True
        return [element for element in listdict if all(meets_conditions(element=element,filtro=filtro) for filtro in filters)]

    @classmethod
    @hlog_atomic()
    def distinct(cls, listdict):
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
    @hlog_atomic()
    def group_and_process(cls, listdict, grouping_fields, operations):
        """
        Agrupa y procesa filas en una lista de diccionarios según operaciones especificadas.

        :param list_dict: Lista de diccionarios a procesar.
        :param grouping_fields: Campos por los cuales se realizará la agrupación.
        :param operations: Lista de tuplas (field, function, new_field) para procesar y renombrar campos.
        :return: Lista de diccionarios con los resultados agrupados y procesados.
        """
        result = {}

        for item in listdict:
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
        
    @classmethod
    @hlog_atomic()
    def select_fields(cls, listdict, fields):
        """
        Extrae campos específicos de una lista de diccionarios. Lanza un error si un campo especificado no existe.

        :param listdict: Lista de diccionarios de donde se extraerán los datos.
        :param fields: Lista de campos a extraer de cada diccionario. Si es None, extrae todos los campos.
        :return: Lista de diccionarios con solo los campos especificados.
        :raises FieldNotFoundError: Si algún campo especificado no existe en uno de los diccionarios.
        """
        if not listdict:
            return []

        # Asegura que 'fields' sea una lista
        fields = cls.ensure_list(fields)
        if fields is None:
            fields = list(listdict[0].keys())

        # Verifica la existencia de los campos
        for field in fields:
            if all(field not in record for record in listdict):
                raise Exception("El campo " + field + " no existe en uno de los diccionarios.")

        return [{field: record[field] for field in fields} for record in listdict]

    @classmethod
    @hlog_atomic()
    def mapping_fields(cls, listdict, mapping, remove_original=False):
        """
        Renombra campos de una lista de diccionarios según un mapeo dado y extrae elementos de una tupla si es necesario.
        Los campos no mencionados en el mapeo se copian directamente. Los campos originales pueden ser eliminados después del mapeo.

        :param listdict: Lista de diccionarios a procesar.
        :param mapping: Diccionario para mapear nombres de campos a nuevos nombres.
                        Formato: {nuevo_nombre_campo: 'nombre_campo_original' o 'nombre_campo_original[index]'}
        :param remove_original: Si es True, elimina los campos originales después del mapeo.
        :return: Lista de diccionarios con campos renombrados y elementos de tupla extraídos si es necesario.
        """
        updated_list = []
        for record in listdict:
            new_record = {}
            for field in record:
                new_record[field] = record[field]
            
            for new_field, original_field in mapping.items():
                if '[' in original_field and ']' in original_field:
                    field_name, index = original_field.split('[')
                    index = int(index.rstrip(']'))
                    value = record.get(field_name, ())
                    if isinstance(value, tuple) and len(value) > index:
                        new_record[new_field] = value[index]
                    else:
                        new_record[new_field] = None
                else:
                    new_record[new_field] = record.get(original_field)
                    if remove_original and original_field in new_record:
                        del new_record[original_field]
            
            updated_list.append(new_record)
        return updated_list

    @classmethod
    @hlog_function()
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
            listdict = cls.filter(listdict=listdict, filters=filters)

        # Ordenar
        if order:
            listdict = cls.sort(listdict=listdict, order_str=order)

        # Extraer campos
        if fields:
            listdict = cls.select_fields(listdict=listdict, fields=fields)
            
        # Renombrar campos
        if mapping:
            listdict = cls.mapping_fields(listdict=listdict, mapping=mapping, remove_original=True)
            
 
            
        return listdict
        
    
    @classmethod
    @hlog_function()
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
            listdict = cls.filter(listdict, filters)
        
        # Agrupar y procesar
        listdict = cls.group_and_process(listdict, grouping_fields, grouping_operations)

        # Ordenar
        if order:
            listdict = cls.sort(listdict, order)

        # Renombrar campos
        if mapping:
            listdict = cls.mapping_fields(listdict, mapping)

        return listdict

    @classmethod
    @hlog_atomic()
    def SelectDistinct(cls, listdict, fields=None, filters=None, order=None, remove_empty=True, return_tuples=True):
        """
        Selecciona valores distintos de una lista de diccionarios basándose en parámetros de selección.

        :param listdict: Lista de diccionarios a procesar.
        :param fields: Lista de campos a extraer de cada diccionario.
        :param filters: Lista de filtros a aplicar (campo, operador, valor).
        :param order: Cadena que define cómo se debe ordenar la lista.
            Formato: 'campo1 asc, campo2 desc, ...'
            'asc' para orden ascendente (por defecto),
            'desc' para orden descendente.
        :param remove_empty: Si es True, elimina los campos que tengan valores vacíos o None.
        :return: Lista de diccionarios con valores distintos y que cumplen con todos los criterios.
        """

        listdict = cls.Select(listdict=listdict, fields=fields, filters=filters, order=order)
        result = cls.distinct(listdict=listdict)
        
        if remove_empty:
            # Filtrar los campos vacíos o None en cada tupla del resultado
            new_result = []
            for item in result:
                filtered_item = tuple(value for value, field in zip(item, fields) if value is not None and value != '')
                new_result.append(filtered_item)
            result = new_result
            
        if return_tuples==False:
            result = cls.from_tuples(result, fields)

        return result


    @classmethod
    @hlog_atomic()
    def from_tuples(cls, tuples_result, fields):
        """
        Convierte una lista de tuplas a una lista de diccionarios, basándose en los campos especificados.

        :param tuples_result: Lista de tuplas, donde cada tupla contiene valores para los campos especificados.
        :param fields: Lista de campos que corresponden a los valores en las tuplas.
        :return: Lista de diccionarios, donde cada diccionario representa un registro con los campos especificados.
        """
        listdict = []
        for tup in tuples_result:
            # Crear un diccionario para la tupla actual, usando los campos como claves
            dict_item = {field: value for field, value in zip(fields, tup)}
            listdict.append(dict_item)
        return listdict