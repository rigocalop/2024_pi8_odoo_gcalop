# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import re
from ..pi8 import zlog

class sy_codes(models.AbstractModel):
    _name = 'sy.codes'
    _description = 'Modelo Base GCALOP'

    @staticmethod
    def clean_text_codes(text_codes):
        """
        Procesa el texto de códigos para separarlos adecuadamente.
        :param texto: string con los códigos.
        :return: list de códigos.
        """
        # Reemplaza diferentes separadores por un único separador (por ejemplo, una coma)
        text_codes = re.sub(r'[\r\n]+', ',', text_codes)
        text_codes = re.sub(r',+', ',', text_codes).strip()
        return text_codes
    
    @staticmethod
    def extract_code_quantity_serial(text_code):
        """
        Extracts product code, quantity, and serial number from a single text code.
        :param text_code: String with the format 'code$serial*quantity' or variations thereof.
        :return: Tuple (code, quantity, serial)
        """
        # Initialize default values
        code = None
        quantity = 1.0  # Default quantity
        serial = None

        # Splitting the string based on the presence of '$' and '*'
        if '$' in text_code:
            parts = text_code.split('$')
            code = parts[0].strip()
            rest = parts[1]

            if '*' in rest:
                serial, quantity_str = rest.split('*')
                quantity = float(quantity_str.strip()) if quantity_str else 1.0
            else:
                serial = rest.strip()
        else:
            if '*' in text_code:
                code, quantity_str = text_code.split('*')
                code = code.strip()
                quantity = float(quantity_str.strip()) if quantity_str else 1.0
            else:
                code = text_code.strip()

        # Stripping any whitespace from the serial
        serial = serial.strip() if serial else None

        return code, quantity, serial

    @staticmethod
    def parse_codes_quantities_serials(text_codes):
        """
        Processes a text string containing barcodes, quantities, and serial numbers.
        Serial numbers are identified by the symbol '$' and are ignored in the parsing.
        :param text_codes: string with barcodes and quantities (format 'code*quantity').
        :return: tuple of two lists: ([(code, quantity)], [invalid_codes])
        """
        # Prepare the text
        text_codes = sy_codes.clean_text_codes(text_codes)

        codes_quantities_list = []
        invalid_codes = []

        for entry in text_codes.split(','):
            entry = entry.strip()
            
            # Extract code, quantity, and serial using the helper method
            code, quantity, serial = sy_codes.extract_code_quantity_serial(entry)

            # Check if code is valid
            if not code:
                continue

            # Check if quantity is valid
            try:
                quantity = float(quantity)
            except ValueError:
                invalid_codes.append(code)
                continue

            codes_quantities_list.append((code, quantity, serial))
        return codes_quantities_list, invalid_codes

    @staticmethod
    def group_and_sort_codes(list_codes_quantities):
        """
        Groups and sorts codes by summing up the quantities.
        :param list_codes_quantities: list of tuples (code, quantity).
        :return: list of tuples (code, total_quantity) sorted by code.
        """
        from collections import defaultdict

        # Create a dictionary to sum quantities for each code
        code_quantity = defaultdict(float)

        # Sum up the quantities for each code
        for code, quantity in list_codes_quantities:
            code_quantity[code] += quantity

        # Convert the dictionary into a list of tuples and sort by code
        grouped_list = sorted(code_quantity.items())

        return grouped_list