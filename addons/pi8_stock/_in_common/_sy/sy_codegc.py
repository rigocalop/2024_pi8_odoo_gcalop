from .._sx import lib_sx as sx
from ..zlogger import ZLogger
from ..zlogger_handlers import *
import re


class sy_CodeGC:   
    
    @hlog_function()
    def parse_clean_text_codes(text_codes):
        # Reemplaza diferentes separadores por un único separador (por ejemplo, una coma)
        text_codes = re.sub(r'[\r\n]+', ',', text_codes)
        text_codes = re.sub(r',+', ',', text_codes).strip()
        return text_codes
    
    @hlog_function()
    def parse_product_details(text_code, str_separators=['&', '$']):
        """
        Extracts product code, quantity, and lotname number from a single text code.
        :param text_code: String with formats like 'code$lotname*quantity' or 'code&lotname*quantity'.
        :param str_separators: List of string separators.
        :return: Tuple (code, quantity, lotname)
        """
        logger = ZLogger.get_logger()            
        # Initialize default values
        code = None
        quantity = 1.0  # Default quantity
        lotname = None

        try:
            # Find the first separator that is present in the text_code
            separator_used = next((sep for sep in str_separators if sep in text_code), None)

            if separator_used:
                parts = text_code.split(separator_used)
                code = parts[0].strip()
                rest = parts[1] if len(parts) > 1 else ''

                if '*' in rest:
                    lotname, quantity_str = rest.split('*')
                    quantity = float(quantity_str.strip()) if quantity_str else 1.0
                else:
                    lotname = rest.strip()
                lotname = separator_used + lotname if lotname else None
            else:
                if '*' in text_code:
                    code, quantity_str = text_code.split('*')
                    code = code.strip()
                    quantity = float(quantity_str.strip()) if quantity_str else 1.0
                else:
                    code = text_code.strip()
            
            # Stripping any whitespace from the lotname
            lotname = lotname.strip() if lotname else None
            

        except ValueError:
            # Handle cases where quantity cannot be converted to float
            logger.warning("Invalid format for quantity. Unable to convert to float.")

        return code, quantity, lotname, separator_used
    
    
    @classmethod
    @hlog_function()
    def validate_lot_name(cls, codegc, lot_name):
        # Validar que el serial tenga al menos 2 caracteres
        separator_user = lot_name[0]    
        lot_name = lot_name[1:]
        
        logger = ZLogger.get_logger()      
        
        is_valid_serial = sx.base62.validate(lot_name)
        if not is_valid_serial: return False
        
        #validar codigo con serial
        numero_codigo = sx.base62.to_number(codegc)
        penultimo_caracter_serial = lot_name[-2]
        valor_penultimo_caracter = sx.base62.to_number(penultimo_caracter_serial)
        residuo = numero_codigo % 62
        is_valid_serial_codigo = int(residuo) == int(valor_penultimo_caracter)
        
        #resultados de validacion
        logger.debug(f"validate_lot_name: {residuo} == {valor_penultimo_caracter}")
        if not is_valid_serial_codigo: 
            logger.warning(f"Lot_name inválido: {codegc}-{lot_name}")
        return is_valid_serial_codigo
        
    
    @classmethod
    @hlog_function()
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
    