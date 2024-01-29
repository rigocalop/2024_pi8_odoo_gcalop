from .._sx import lib_sx as sx
from ..zlogger import ZLogger
from ..zlogger_handlers import *
import re

class ExceptionEntryCodeLot(Exception):
    def __init__(self, message="Error en el formato del texto de entrada"):
        self.message = message
        super().__init__(self.message)

class sy_EntryCodeLot:
    
    @classmethod
    @hlog_atomic(enable=True, resalt=False, compact=True)
    def expandEntryTextCode(cls, textcode):
        """
        Extrae el código del producto, la cantidad y el número de lote de un código de texto único.
        :param entry_textcode: Cadena de texto con formatos como 'codigo$lote*cantidad' o 'codigo&lote*cantidad'.
            Los separadores utilizados para dividir el texto son '&' y '$'.
        :return: Diccionario con los siguientes campos:
            - 'entry': Texto original.
            - 'code': Código del producto extraído del texto.
            - 'qty': Cantidad del producto como un valor flotante.
            - 'lot': Nombre o número de lote del producto.
            - 'tracking': Tipo de seguimiento ('serial', 'lot' o 'none').
        :raises ExceptionEntryTextCode: Si el formato del texto de entrada no es válido.
        """
        # Mapeo de separadores a tipos de seguimiento
        tracking_map = {'$': 'serial', '&': 'lot'}
        separator = tracking_map.keys()

        # Inicializar valores predeterminados
        code = None
        qty = 1.0  # Cantidad por defecto
        lot = None
        tracking = 'none'

        try:
            # Encontrar el primer separador que está presente en entry_textcode
            separator_used = next((sep for sep in separator if sep in textcode), None)

            if separator_used:
                parts = textcode.split(separator_used)
                code = parts[0].strip()
                rest = parts[1] if len(parts) > 1 else ''

                if '*' in rest:
                    lot, qty_str = rest.split('*')
                    qty = float(qty_str.strip()) if qty_str else 1.0
                else:
                    lot = rest.strip()

                lot = separator_used + lot if lot else None
                tracking = tracking_map.get(separator_used, 'none')
            else:
                if '*' in textcode:
                    code, qty_str = textcode.split('*')
                    code = code.strip()
                    qty = float(qty_str.strip()) if qty_str else 1.0
                else:
                    code = textcode.strip()

            # Eliminar espacios en blanco del nombre del lote
            lot = lot.strip() if lot else None

            if not lot and not code:
                raise ExceptionEntryCodeLot('No existen código y lote')

            # Agregar la excepción cuando tracking sea 'none' y exista un lote
            if tracking == 'none' and lot is not None:
                raise ExceptionEntryCodeLot('Tracking es none pero existe un lote')

            # Si todo está bien, se devuelve la entrada
            entry = {'entry': textcode, 'code': code, 'qty': qty, 'lot': lot, 'tracking': tracking}
            return entry

        except ValueError:
            # Específicamente para errores de conversión a float
            raise ExceptionEntryCodeLot('Formato de cantidad inválido. No se puede convertir a flotante.')
        except Exception as e:
            # Para cualquier otro tipo de excepción
            raise ExceptionEntryCodeLot('Error desconocido. ' + str(e))

    @classmethod
    @hlog_atomic()
    def processEntryTextCodes(cls, env, textcodes, default_values=None, mapping_dict=None, validation_function=None):
        """
        Procesa una lista de códigos de texto de entrada y los clasifica como válidos o inválidos.
        :param entry_textcodes: Lista de cadenas de texto, cada una con formatos como 'codigo$lote*cantidad' o 'codigo&lote*cantidad'.
        :param default_values: Valores iniciales por defecto para aplicar a cada entrada antes de la expansión.
        :param mapping_dict: Diccionario de mapeo para asignar campos de las entradas expandidas a nuevos nombres de campos.
        :param validation_function: Función opcional para validar el 'default_code'.
        :return: Dos listas: la primera con las entradas válidas y la segunda con las entradas inválidas.
        """
        valid_entries = []
        invalid_entries = []
        textcodes = sx.XList.ensure(textcodes)

        for textcode in textcodes:
            try:
                # Aplicar valores por defecto si están disponibles
                entry = default_values.copy() if default_values else {}
                expanded_entry = cls.expandEntryTextCode(textcode=textcode)
                entry.update(expanded_entry)

                # Aplicar el mapeo si está disponible
                if mapping_dict:
                    mapped_entry = {new_key: entry[old_key] for new_key, old_key in mapping_dict.items() if old_key in expanded_entry}
                    entry.update(mapped_entry)

                # Validar 'default_code' si la función de validación está disponible
                if validation_function and 'default_code' in entry:
                    is_valid = validation_function(env, entry['default_code'])
                    if not is_valid:
                        raise ExceptionEntryCodeLot('default_code inválido')
                valid_entries.append(entry)

            except ExceptionEntryCodeLot as e:
                invalid_entries.append({'entry': textcode, 'msg': str(e)})

        return valid_entries, invalid_entries

    @classmethod
    def validate_CODE(cls, code):
        """
        Valida un código que se presume incluye un dígito verificador.

        :param code: Código que se va a validar. Se espera que este código ya incluya un dígito verificador.

        :return: Retorna True si el código es válido, False en caso contrario.

        La función asume que el último carácter del código es el dígito verificador. 
        Se genera un nuevo dígito verificador a partir de la parte base del código y se compara con el original.
        """
        if len(code) < 2:
            # El código debe tener al menos 2 caracteres (1 del código base + 1 del verificador)
            return False

        code_base = code[:-1]  # Todo excepto el último carácter

        regenerated_code_with_verifier = sx.base36.add_verifier(code_base)

        # Verificar si el dígito verificador regenerado coincide con el original
        return code == regenerated_code_with_verifier

    @classmethod
    def validate_LOT(cls, code, LOT):
        """
        Valida un LOT basado en un código y un identificador de LOT.

        :param code: Código del LOT a validar.
        :param LOT: Identificador del LOT que incluye un separador seguido del identificador en sí.

        :return: Retorna True si el identificador de LOT es válido, False en caso contrario.

        La validación se realiza en dos etapas:
        1. Se valida el identificador del LOT usando una codificación base62.
        2. Se verifica que el penúltimo carácter del identificador del LOT coincida con el residuo de la división del código del LOT (también en base62) por 62.
        """
        # Validar que el identificador del LOT tenga al menos 2 caracteres
        logger = ZLogger.get_logger()
        if len(LOT) < 2:
            logger.warning("El identificador del LOT es demasiado corto.")
            return False

        LOT_separator = LOT[0]
        LOT_identifier = LOT[1:]
        
        # Validar el identificador del LOT
        is_valid_LOT_identifier = sx.base62.validate(LOT_identifier)
        if not is_valid_LOT_identifier: 
            logger.warning("Identificador del LOT inválido.")
            return False
        
        # Validar el código con respecto al identificador del LOT
        # HACER REFACTORING A ESTE CODIGO
        numero_codigo = sx.base62.to_number(code)
        penultimo_caracter_LOT = LOT_identifier[-2]
        valor_penultimo_caracter = sx.base62.to_number(penultimo_caracter_LOT)

        residuo = numero_codigo % 62
        is_valid_code_LOT = int(residuo) == int(valor_penultimo_caracter)
        
        # Registro de resultados de la validación
        logger.debug(f"validate_lot: {residuo} == {valor_penultimo_caracter}")
        if not is_valid_code_LOT: 
            logger.warning(f"LOT inválido: {code}-{LOT}")

        return is_valid_code_LOT