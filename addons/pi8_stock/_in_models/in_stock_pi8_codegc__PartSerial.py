from .._in_common.zlogger import ZLogger, logger_function_handler
import random
import logging
logging.setLoggerClass(ZLogger)
_logger = logging.getLogger("testLogger")

class in_stock_pi8_codegc__PartSerial:
    @classmethod
    def convert_to_base62(cls, num):
        characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        if num == 0:
            return characters[0]
        base = 62
        result = ""
        while num > 0:
            result = characters[num % base] + result
            num //= base
        return result

    @classmethod
    def convert_from_base62(cls, base62_string):
        characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        base = 62
        length = len(base62_string)
        num = 0

        for i, char in enumerate(base62_string):
            value = characters.index(char)
            power = length - i - 1
            num += value * (base ** power)
        return num

    @classmethod
    def add_verifier(cls, serial_without_verifier):
        # Convert the serial to its numeric representation using the base 62 conversion function
        numeric_serial = cls.convert_from_base62(serial_without_verifier)

        # Calculate the remainder of the division of the number by 62
        remainder = numeric_serial % 62

        # Convert the remainder back to a base 62 character
        verifier_character = cls.convert_to_base62(remainder)

        # Append the verification character to the end of the original serial
        serial_with_verifier = serial_without_verifier + verifier_character

        return serial_with_verifier

    @classmethod
    @logger_function_handler
    def validate_verifier(cls, serial):
        # Verify that the last character of the serial corresponds to the converted serial
        last_serial_character = serial[-1]
        last_character_value = cls.convert_from_base62(last_serial_character)
        numeric_serial = cls.convert_from_base62(serial[:-1])
        remainder = numeric_serial % 62
        _logger.debug(f"validate_serial: {remainder} == {last_character_value}")
        is_valid = int(remainder) == int(last_character_value)
        if not is_valid:
            _logger.warning(f"Invalid serial: {serial}")
        return is_valid
    
    @classmethod
    @logger_function_handler
    def validate_serial_codigo(cls, serial, codigo):
        # validate_codigo = in_stock_pi8_codegc.validate_codigo(codigo)
        validate_serial = cls.validate_verifier(serial)
        if not validate_serial:
            return False
        
        # Convertir el código a un número entero base 62
        numero_codigo = cls.convert_from_base62(codigo)

        # Verificar el módulo del código con el penúltimo carácter del serial
        penultimo_caracter_serial = serial[-2]
        valor_penultimo_caracter = cls.convert_from_base62(penultimo_caracter_serial)
        residuo = numero_codigo % 62
        _logger.debug(f"validate_serial_codigo: {residuo} == {valor_penultimo_caracter}")
        is_valid = int(residuo) == int(valor_penultimo_caracter)
        if not is_valid:
            _logger.warning(f"Serial-Codigo inválido: {codigo}-{serial}")
        return is_valid
        
    
    @classmethod
    @logger_function_handler
    def generate(cls, codigo, longitud_serial):
        if longitud_serial < 2:
            raise ValueError("La longitud del serial debe ser al menos 2")

        # Convertir el código a un número entero base 62
        numero_codigo = cls.convert_from_base62(codigo)

        # Calcular el penúltimo carácter del serial
        valor_penultimo_caracter = numero_codigo % 62
        penultimo_caracter_serial = cls.convert_to_base62(valor_penultimo_caracter)

        # Generar la parte inicial del serial
        caracteres = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        parte_inicial_serial = ''.join(random.choices(caracteres, k=longitud_serial-2))

        # Calcular el último carácter del serial
        serial_temporal = parte_inicial_serial + penultimo_caracter_serial
        serial = cls.add_verifier(serial_temporal)
        return serial
    

