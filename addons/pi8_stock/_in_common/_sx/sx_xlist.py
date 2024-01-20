import json
class sx_XList:
    @classmethod
    def convert(cls, text_items, separator=','):
        """
        Convierte una cadena de texto en una lista, manejando diferentes formatos de entrada.

        :param text_items: Cadena de texto para convertir en lista. Puede estar en formato JSON
                        (por ejemplo, '["item1", "item2"]') o separada por un delimitador específico.
        :param separator: Delimitador utilizado para dividir la cadena en elementos de lista. 
                        Por defecto es una coma (',').

        :return: Lista de elementos extraídos de la cadena de texto.

        Esta función maneja tres casos:
        1. Si la entrada es una cadena vacía, devuelve una lista vacía.
        2. Si la entrada es un array JSON, intenta convertirla en una lista de Python. 
        Si la conversión falla o el resultado no es una lista, lanza una excepción.
        3. Si la entrada es una cadena normal, la divide en elementos usando el delimitador proporcionado.
        """
        list_text_items = []
        # Verificar si el input es un string
        if isinstance(text_items, str):
            text_items = text_items.strip()
            if text_items == '':
                return []
            # Verificar si es un array JSON
            elif text_items.startswith('[') and text_items.endswith(']'):
                try:
                    list_text_items = json.loads(text_items)
                    if not isinstance(list_text_items, list):
                        raise Exception('El formato de los códigos no es un array válido.')
                except json.JSONDecodeError:
                    raise Exception('El formato de los códigos no es válido.')
            else:
                list_text_items = text_items.split(separator)
        # Otras partes de la función...
        return list_text_items
    
    @classmethod
    def ensure(cls, text_items, separator=','):
        """
        Asegura que la entrada proporcionada sea una lista, ya sea convirtiéndola de una cadena de texto o validando su formato.

        :param text_items: Puede ser una cadena de texto o una lista existente. 
                        Si es una cadena, se intentará convertir en lista.
        :param separator: Delimitador utilizado para dividir la cadena en elementos de lista 
                        en caso de que text_items sea una cadena. 
                        Por defecto es una coma (',').

        :return: Lista de elementos. Si text_items ya es una lista, se devuelve tal cual.

        Esta función verifica primero si text_items es una cadena. Si es así, utiliza la función 'convert' 
        para transformarla en una lista. Si text_items es ya una lista, simplemente la devuelve. 
        Si text_items no es ni una cadena ni una lista, lanza una excepción.
        """
        list_text_items = []
        # Verificar si el input es un string
        if isinstance(text_items, str):
            list_text_items = cls.convert(text_items, separator)
        elif isinstance(text_items, list):
            list_text_items = text_items
        else:
            raise Exception(_('La entrada proporcionada no es un string.'))
        return list_text_items
    
    @classmethod
    def count_matches(cls, dict_list, field, boolean_value):
        """
        Cuenta las coincidencias de un valor booleano específico en un campo dado 
        en una lista de diccionarios.

        :param dict_list: Lista de diccionarios.
        :param field: Campo en el que buscar el valor booleano.
        :param boolean_value: Valor booleano a buscar.
        :return: Número de coincidencias del valor booleano en el campo especificado.
        """
        count = 0
        for item in dict_list:
            if item.get(field) == boolean_value:
                count += 1
        return count

    @classmethod
    def fields_include(cls, list_of_dicts, fields):
        """
        Filtra los campos en una lista de diccionarios para incluir solo los especificados.

        :param list_of_dicts: Lista de diccionarios a filtrar.
        :param fields_to_show: Cadena de nombres de campos separados por comas o lista de nombres de campos.
        :return: Lista de diccionarios con solo los campos especificados.
        """
        # if fields_to_include == None or  (isinstance(fields_to_include, str) and fields_to_include==""):
        #     return list_of_dicts
        if fields == None:
            return list_of_dicts

        fields = cls.convert(fields, separator=',')
        # Regenerar la lista para incluir solo los campos especificados
        filtered_list = [{field: obj.get(field) for field in fields} for obj in list_of_dicts]

        return filtered_list

    @classmethod
    def distinct(cls, lista_dicts, clave_distinct, **condiciones):
        """
        Obtiene valores únicos para una clave específica de una lista de diccionarios, aplicando un filtro.

        :param lista_dicts: Lista de diccionarios a procesar.
        :param clave_distinct: Clave para la cual se extraerán valores únicos.
        :param condiciones: Condiciones de filtrado (clave=valor).
        :return: Conjunto de valores únicos que cumplen las condiciones.
        """
        # Filtrar la lista de diccionarios según las condiciones proporcionadas
        lista_filtrada = [detalle for detalle in lista_dicts if all(detalle.get(cond) == valor for cond, valor in condiciones.items())]

        # Obtener valores únicos para la clave dada
        valores_unicos = set(detalle[clave_distinct] for detalle in lista_filtrada if clave_distinct in detalle)

        return valores_unicos