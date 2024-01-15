from .._sx import lib_sx as sx
from ..zlogger import function_handler, ZLogger


class sy_CodeGC:   
    
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
    