from .._in_common.zlogger import ZLogger, logger_function_handler
import logging
logging.setLoggerClass(ZLogger)
_logger = logging.getLogger("testLogger")

class in_stock_pi8_codegc__PartCode:
    @classmethod
    def convert_to_base36(cls, num):
        characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if num == 0:
            return characters[0]
        base = 36
        result = ""
        while num > 0:
            result = characters[num % base] + result
            num //= base
        return result

    @classmethod
    def convert_from_base36(cls, base36_string):
        characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        base = 36
        length = len(base36_string)
        num = 0

        for i, char in enumerate(base36_string):
            value = characters.index(char)
            power = length - i - 1
            num += value * (base ** power)
        return num

    @classmethod
    def add_verifier(cls, code_without_verifier):
        # Convert the code to its numeric representation using the base 36 conversion function
        numeric_code = cls.convert_from_base36(code_without_verifier)

        # Calculate the remainder of the division of the number by 36
        remainder = numeric_code % 36

        # Convert the remainder back to a base 36 character
        verifier_character = cls.convert_to_base36(remainder)

        # Append the verification character to the end of the original code
        code_with_verifier = code_without_verifier + verifier_character

        return code_with_verifier

    @classmethod
    @logger_function_handler
    def validate_verifier(cls, code):
        # Verify that the last character of the serial corresponds to the converted serial
        last_serial_character = code[-1]
        last_character_value = cls.convert_from_base36(last_serial_character)
        numeric_code = cls.convert_from_base36(code[:-1])
        remainder = numeric_code % 36
        _logger.debug(f"validate_code: {remainder} == {last_character_value}")
        is_valid = int(remainder) == int(last_character_value)
        if not is_valid:
            _logger.warning(f"Invalid code: {code}")
        return is_valid
    
    @classmethod
    @logger_function_handler
    def complete_code_and_add_verifier(cls, code):
        # Agregar "0" al inicio si la longitud del código es exactamente 6
        if len(code) == 8:
            return code

        if len(code) == 6:
            code = '0' + code

        # Asegurarse de que el código tenga ahora 7 caracteres
        if len(code) != 7:
            raise ValueError("El código debe tener 6 o 7 caracteres antes de agregar el verificador.")
        
        completed_code = cls.add_verifier(code)
        return completed_code