import json
class sx_list:
    @classmethod
    def convert(cls, text_items, separator=','):
        # Verificar si el input es un string
        if isinstance(text_items, str):
            text_items = text_items.strip()
            # Verificar si es un array JSON
            if text_items[0] == '[' or text_items[-1] == ']':
                try:
                    list_text_items = json.loads(text_items)
                    if not isinstance(list_text_items, list):
                        raise Exception(('El formato de los códigos no es un array válido.'))
                except json.JSONDecodeError:
                    raise Exception(_('El formato de los códigos no es válido.'))
            else:
                list_text_items = text_items.split(separator)
        elif isinstance(text_items, list):
            list_text_items = text_items
        else:
            raise Exception(_('La entrada proporcionada no es un string.'))
        return list_text_items