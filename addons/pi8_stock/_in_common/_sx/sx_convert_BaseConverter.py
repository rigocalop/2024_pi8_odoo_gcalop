import random
class sx_BaseConverter:
    base = None
    characters = None

    @classmethod
    def from_number(cls, num):
        if num == 0:
            return cls.characters[0]

        result = ""
        while num > 0:
            result = cls.characters[num % cls.base] + result
            num //= cls.base
        return result

    @classmethod
    def to_number(cls, base_string):
        length = len(base_string)
        num = 0

        for i, char in enumerate(base_string):
            value = cls.characters.index(char)
            power = length - i - 1
            num += value * (cls.base ** power)
        return num

    @classmethod
    def calculate_verifier_character(cls, base_string):
        numeric_value = cls.to_number(base_string)
        remainder = numeric_value % cls.base
        verifier_character = cls.from_number(remainder)
        return verifier_character
    
    @classmethod
    def add_verifier(cls, base_without_verifier):
        verifier_character = cls.calculate_verifier_character(base_without_verifier)
        serial_with_verifier = base_without_verifier + verifier_character
        return serial_with_verifier
    
    @classmethod
    def validate(cls, base_with_verifier):
        base_without_verifier, verifier_character = base_with_verifier[:-1], base_with_verifier[-1]
        expected_verifier = cls.calculate_verifier_character(base_without_verifier)
        return verifier_character == expected_verifier

    @classmethod
    def random_generate(cls, length):
        if length <= 0:
            raise ValueError("La longitud debe ser un número positivo.")

        # Generar una cadena aleatoria de la longitud especificada
        random_string = ''.join(random.choices(cls.characters, k=length))
        return random_string
    
class sx_Base62Converter(sx_BaseConverter):
    base = 62
    characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

class sx_Base36Converter(sx_BaseConverter):
    base = 36
    characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class sx_Base16Converter(sx_BaseConverter):
    base = 16
    characters = "0123456789ABCDEF"