from .._sx import lib_sx as sx
from ..zlogger import function_handler, ZLogger
import re

class sy_CodeGC:   
    @function_handler
    def parse_clean_text_codes(text_codes):
        # Reemplaza diferentes separadores por un único separador (por ejemplo, una coma)
        text_codes = re.sub(r'[\r\n]+', ',', text_codes)
        text_codes = re.sub(r',+', ',', text_codes).strip()
        return text_codes
    
    @function_handler
    def parse_product_details(text_code, str_separator='$', str_separator2='*'):
        """
        Extracts product code, quantity, and serial number from a single text code.
        :param text_code: String with the format 'code$serial*quantity' or variations thereof.
        :return: Tuple (code, quantity, serial)
        """
        logger = ZLogger.get_logger()            
        # Initialize default values
        code = None
        quantity = 1.0  # Default quantity
        serial = None

        try:
            # Splitting the string based on the presence of '$' and '*'
            if str_separator in text_code:
                parts = text_code.split(str_separator)
                code = parts[0].strip()
                rest = parts[1] if len(parts) > 1 else ''

                if str_separator2 in rest:
                    serial, quantity_str = rest.split(str_separator2)
                    quantity = float(quantity_str.strip()) if quantity_str else 1.0
                else:
                    serial = rest.strip()
            else:
                if str_separator2 in text_code:
                    code, quantity_str = text_code.split(str_separator2)
                    code = code.strip()
                    quantity = float(quantity_str.strip()) if quantity_str else 1.0
                else:
                    code = text_code.strip()

            # Stripping any whitespace from the serial
            serial = serial.strip() if serial else None

        except ValueError:
            # Handle cases where quantity cannot be converted to float
            logger.warning("Invalid format for quantity. Unable to convert to float.")

        return code, quantity, serial
    
    
    @classmethod
    @function_handler
    def validate_serial(cls, codegc, serial):
        # Validar que el serial tenga al menos 2 caracteres
        logger = ZLogger.get_logger()            
        
        is_valid_serial = sx.base62.validate(serial)
        if not is_valid_serial: return False
        
        #validar codigo con serial
        numero_codigo = sx.base62.to_number(codegc)
        penultimo_caracter_serial = serial[-2]
        valor_penultimo_caracter = sx.base62.to_number(penultimo_caracter_serial)
        residuo = numero_codigo % 62
        is_valid_serial_codigo = int(residuo) == int(valor_penultimo_caracter)
        
        #resultados de validacion
        logger.debug(f"validate_codegc_serial: {residuo} == {valor_penultimo_caracter}")
        if not is_valid_serial_codigo: 
            logger.warning(f"Serial-Codigo inválido: {codegc}-{serial}")
        return is_valid_serial_codigo
        
    
    @classmethod
    @function_handler
    def generate_serial(cls, codegc, longitud_serial):
        if longitud_serial < 2:
            raise ValueError("La longitud del serial debe ser al menos 2")

        # Convertir el código a un número entero base 62
        numero_codigo = sx.base62.to_number(codegc)
        parte_inicial_serial = sx.base62.random_generate(longitud_serial - 2)
        
        # Calcular el penúltimo carácter del serial
        valor_penultimo_caracter = numero_codigo % 62
        penultimo_caracter_serial = sx.base62.from_number(valor_penultimo_caracter)

        # Calcular el último carácter del serial
        serial_temporal = parte_inicial_serial + penultimo_caracter_serial
        serial = sx.base62.add_verifier(serial_temporal)
        return serial
    