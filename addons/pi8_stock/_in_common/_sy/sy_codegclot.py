from .._sx import lib_sx as sx
from ..zlogger import ZLogger
from ..zlogger_handlers import *
import re


class sy_CodegcLot:   
    class ExceptionEntryCodeLot(Exception):
        def __init__(self, message="Error en el formato del texto de entrada"):
            self.message = message
            super().__init__(self.message)
    
    @classmethod
    @hlog_function()
    def generate_codegc(cls, codegc):
        """
        Genera un código base (codegc) con un verificador utilizando la codificación base36.

        Args:
            codegc (str): El código base que será procesado para añadirle un verificador.

        Returns:
            str: El código base con un carácter verificador añadido al final.

        Esta función asegura que el código base tenga una longitud adecuada antes de añadir el verificador.
        El verificador se genera a partir del código base y se añade al final del mismo, utilizando
        la codificación base36 para crear un código final seguro y verificable.
        """
        # Asegurar que codegc tiene la longitud adecuada antes de añadir el verificador
        codegc = codegc[:8]  # Ajusta según sea necesario para tu lógica específica
        
        # Añadir un verificador a codegc utilizando sx.base36.add_verifier
        codegc = sx.base36.add_verifier(codegc)
        
        return codegc
        


    @classmethod
    @hlog_function()
    def validate_codegc(cls, codegc):
        """
        Valida un código base (codegc) asegurando que el verificador sea correcto.

        Args:
            codegc (str): El código base completo con el verificador incluido para validar.

        Returns:
            tuple: Un par (bool, str) donde el primer elemento indica si el código base con el verificador
                es válido, y el segundo elemento es un mensaje descriptivo del resultado.

        Esta función extrae el código base sin el verificador, regenera el verificador para este código base,
        y luego compara el código base con verificador regenerado con el código base original proporcionado.
        Esto asegura que el verificador sea correcto y que el código base sea auténtico.
        """
        # Extraer codegc sin el verificador
        original_codegc = codegc[:-1]
        
        # Regenerar el verificador para codegc
        regenerated_codegc_with_verifier = sx.base36.add_verifier(original_codegc)
        
        # Comparar el codegc con verificador regenerado con el proporcionado
        if regenerated_codegc_with_verifier == codegc:
            return True, "El codegc con verificador es válido."
        else:
            return False, "El codegc con verificador no es válido."

    @classmethod
    @hlog_function()
    def validate_codegc(cls, codegc):
        # Extraer codegc sin el verificador
        codegc_sin_verifier = codegc[:-1]
        # Regenerar el verificador para codegc
        regenerated_codegc_with_verifier = sx.base36.add_verifier(codegc_sin_verifier)
        # Comparar el codegc con verificador regenerado con el proporcionado
        if regenerated_codegc_with_verifier == codegc:
            return True, "El codegc con verificador es válido."
        else:
            return False, "El codegc con verificador no es válido."
    
    
    @classmethod
    @hlog_function()
    def validate_lot(cls, codegc, lot):
        """
        Valida un lote generado para asegurar que coincide con el código base (codegc) y
        que el carácter verificador es correcto.

        Args:
            codegc (str): El código base utilizado para generar el lote.
            lot (str): El lote generado que se va a validar.

        Returns:
            tuple: Un par (bool, str) donde el primer elemento indica si el lote es válido
                y el segundo elemento es un mensaje que describe el resultado de la validación.

        La validación se realiza en dos pasos principales:
        1. Se verifica que el penúltimo carácter del lote coincida con el esperado, basado en el código base.
        2. Se verifica que el carácter verificador del lote sea correcto, asegurando la integridad del lote.
        """
        try:
            # Convertir el código base a un número entero usando codificación base 62 para la validación
            numero_codigo = sx.base62.to_number(codegc)

            # Separar el lote para extraer la parte sin el verificador (todos los caracteres menos el último)
            lot_sin_verificador = lot[:-1]

            # Identificar el penúltimo carácter del lote, que ahora es el último carácter de lot_sin_verificador
            penultimo_caracter_lot = lot_sin_verificador[-1]

            # Calcular qué valor del penúltimo carácter se espera basado en el número derivado del codegc
            valor_penultimo_caracter_esperado = numero_codigo % 62
            penultimo_caracter_esperado = sx.base62.from_number(valor_penultimo_caracter_esperado)

            # Verificar si el penúltimo carácter del lote coincide con el valor esperado
            if penultimo_caracter_lot != penultimo_caracter_esperado:
                # Si no coincide, el lote es considerado inválido
                return False, "El lote no es válido debido a la inconsistencia del penúltimo carácter."

            # Reconstruir el lote con el verificador para verificar la integridad completa del lote
            lot_con_verificador_regenerado = sx.base62.add_verifier(lot_sin_verificador)

            # Verificar si el lote completo, incluyendo el verificador, coincide con el lote original
            if lot_con_verificador_regenerado == lot:
                # Si coincide, el lote es considerado válido
                return True, "El lote es válido."
            else:
                # Si no coincide, el lote es considerado inválido
                return False, "El lote no es válido debido a la inconsistencia del verificador."
        except Exception as e:
            # Capturar y manejar cualquier excepción que pueda ocurrir durante el proceso de validación
            return False, str(e)
    
    @classmethod
    @hlog_function()
    def generate_lot(cls, codegc, length_lot=10):
        """
        Genera un identificador de lote único basado en el código base y la longitud especificada.

        Args:
            codegc (str): El código base utilizado para generar un elemento único del lote.
            length_lot (int, optional): La longitud total deseada para el identificador de lote.
                                        Incluye el carácter verificador y el penúltimo carácter especial.
                                        Default es 10.

        Returns:
            str: El identificador de lote generado, que incluye un carácter verificador.

        Raises:
            ValueError: Si la longitud especificada para el lote es menor que 2.
        """

        # Verificar que la longitud del lote sea adecuada
        if length_lot < 2:
            raise ValueError("La longitud del lote debe ser al menos 2")

        # Convertir el código base a un número utilizando codificación base 62
        # Esto se utiliza para determinar un componente único del lote
        numero_codigo = sx.base62.to_number(codegc)

        # Generar la parte inicial del lote de manera aleatoria, excepto los últimos dos caracteres
        parte_inicial_lot = sx.base62.random_generate(length_lot - 2)
        
        # Calcular el penúltimo carácter del lote basado en el módulo del número de código
        # Esto ayuda a incorporar una parte del código base en el lote
        valor_penultimo_caracter = numero_codigo % 62
        penultimo_caracter_lot = sx.base62.from_number(valor_penultimo_caracter)

        # Combinar la parte inicial del lote con el penúltimo carácter
        lot_temporal = parte_inicial_lot + penultimo_caracter_lot

        # Añadir un carácter verificador al final del lote para asegurar integridad
        lot = sx.base62.add_verifier(lot_temporal)

        # Retornar el lote completo con el verificador
        return lot
    
    @classmethod
    @hlog_function()
    def validate(cls, codegclot):
        """
        Valida un código generado que puede incluir un `codegc` y, opcionalmente, un lote o serial.

        Args:
            codegclot (str): El código completo generado que puede incluir `codegc` y un lote o serial.

        Returns:
            tuple: Retorna un par (bool, str), donde el primer elemento es True si el código es válido,
                False en caso contrario. El segundo elemento es un mensaje que indica el resultado de la validación.

        Esta función realiza la siguiente lógica de validación:
        - Separa el `codegclot` en `codegc` y lote/serial basándose en la presencia de '&' o '$'.
        - Valida el `codegc` utilizando `validate_codegc`.
        - Si existe un lote o serial, lo valida utilizando `validate_lot`.
        - Retorna True si todas las validaciones son exitosas, False en caso contrario.
        """
        try:
            # Separar el generated_code en sus componentes basado en el separador específico
            if '&' in codegclot:
                codegc, lot = codegclot.split('&')
                tracking = 'lot'
            elif '$' in codegclot:
                codegc, lot = codegclot.split('$')
                tracking = 'serial'
            else:
                # Si no hay separador, solo se considera el codegc
                codegc = codegclot
                lot = None
                tracking = 'none'
            
            # Verificar el codegc reconstruyendo el verificador y comprobar su validez
            codegc_valid = cls.validate_codegc(codegc)
            if not codegc_valid[0]:
                # Si el codegc no es válido, retorna False con el mensaje de error correspondiente
                return False, codegc_valid[1]
            
            # Si existe un lote o serial, validar según el tipo identificado
            if tracking != 'none':
                if not lot:
                    return False, 'Se requiere *lot*.'
                lot_valid = cls.validate_lot(codegc, lot)
                if not lot_valid[0]:
                    # Si el lote o serial no es válido, retorna False con el mensaje de error correspondiente
                    return False, lot_valid[1]
                
            info = {
                'codegc' : codegc,
                'lot' : lot,
                'tracking' : tracking
            }
    
            # Si todas las validaciones son exitosas, retorna True con un mensaje de éxito
            return True, info
        except Exception as e:
            # Maneja cualquier excepción inesperada durante el proceso de validación
            return False, str(e)
    
    @classmethod
    @hlog_function()
    def generate(cls, codegc, tracking=None, length_lot=10):
        """
        Genera un código completo que puede incluir un código base (codegc) y,
        opcionalmente, un identificador de lote o serial.

        Args:
            codegc (str): El código base al que se añadirá el identificador.
            tracking (str, optional): El tipo de identificador a añadir al código base.
                Puede ser 'lot', 'serial', o None si no se desea añadir ninguno.
            length_lot (int, optional): La longitud deseada para el identificador de lote o serial.
                Debe ser al menos 2. Default es 10.

        Returns:
            str: El código completo generado, que incluye el código base y,
                si se especificó, un identificador de lote o serial.

        Raises:
            ValueError: Si la longitud del identificador de lote o serial es menor que 2.
        """

        # Verificar que la longitud del identificador sea adecuada
        if length_lot < 2:
            raise ValueError("La longitud del serial debe ser al menos 2")
        
        # Generar el código base con un verificador
        codegc = cls.generate_codegc(codegc)

        # Si no se solicita un identificador adicional, retorna solo el código base
        if tracking == 'none' or tracking is None:
            return codegc

        # Generar el lote o serial basado en el código base y la longitud deseada
        lot = cls.generate_lot(codegc, length_lot)

        # Determinar el separador basado en el tipo de identificador solicitado
        if tracking == 'lot':
            charsep = '&'
        elif tracking == 'serial':
            charsep = '$'
        else:
            # Si se especifica un tipo de tracking desconocido, no usar separador
            charsep = ''

        # Concatenar y retornar el código base, separador, y lote/serial
        return codegc + charsep + lot


    @classmethod
    @hlog_atomic(enable=True, resalt=False, compact=True)
    def expandTextCode(cls, textcode):
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
                raise cls.ExceptionEntryCodeLot('No existen código y lote')

            # Agregar la excepción cuando tracking sea 'none' y exista un lote
            if tracking == 'none' and lot is not None:
                raise cls.ExceptionEntryCodeLot('Tracking es none pero existe un lote')

            # Si todo está bien, se devuelve la entrada
            entry = {'product_id': None, 'lot_id': None, 'entry': textcode, 'code': code, 'qty': qty, 'lot': lot, 'tracking': tracking}
            return entry

        except ValueError:
            # Específicamente para errores de conversión a float
            raise cls.ExceptionEntryCodeLot('Formato de cantidad inválido. No se puede convertir a flotante.')
        except Exception as e:
            # Para cualquier otro tipo de excepción
            raise cls.ExceptionEntryCodeLot('Error desconocido. ' + str(e))



    @classmethod
    @hlog_atomic(enable=True, resalt=False, compact=True)
    def expandEntry(cls, entry):
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
            separator_used = next((sep for sep in separator if sep in entry), None)

            if separator_used:
                parts = entry.split(separator_used)
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
                if '*' in entry:
                    code, qty_str = entry.split('*')
                    code = code.strip()
                    qty = float(qty_str.strip()) if qty_str else 1.0
                else:
                    code = entry.strip()

            # Eliminar espacios en blanco del nombre del lote
            lot = lot.strip() if lot else None

            if not lot and not code:
                raise cls.ExceptionEntryCodeLot('No existen código y lote')

            # Agregar la excepción cuando tracking sea 'none' y exista un lote
            if tracking == 'none' and lot is not None:
                raise cls.ExceptionEntryCodeLot('Tracking es none pero existe un lote')

            # Si todo está bien, se devuelve la entrada
            entry = {'entry': entry, 'code': code, 'qty': qty, 'lot': lot, 'tracking': tracking}
            return entry

        except ValueError:
            # Específicamente para errores de conversión a float
            raise cls.ExceptionEntryCodeLot('Formato de cantidad inválido. No se puede convertir a flotante.')
        except Exception as e:
            # Para cualquier otro tipo de excepción
            raise cls.ExceptionEntryCodeLot('Error desconocido. ' + str(e))