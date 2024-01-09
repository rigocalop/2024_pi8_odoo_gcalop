# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import re
import odoo
import sys

class in_product(models.AbstractModel):
    _name = 'in.product'
    _description = 'Modelo Base GCALOP'
    
    
    def find_missing__default_codes(self, default_codes):
        """
        Encuentra códigos de barras que no tienen productos asociados en 'default_code'.
        :param barcodes: Lista de códigos de barras.
        :return: Lista de códigos de barras faltantes.
        """
        # Buscar productos en 'default_code' que coincidan con los códigos de barras
        products_default_code = self.env['product.product'].search_read([('default_code', 'in', default_codes)], ['default_code'])
        found_codes = set(product['default_code'] for product in products_default_code)

        missing_barcodes = set(default_codes) - found_codes
        return list(default_codes)

    
    @api.model
    def exist_from_barcode(self, barcode):
        """
        Verifica si un producto con el código de barras dado ya existe en la base de datos.
        En la versión Enterprise, busca primero en 'barcode' y luego en 'default_code'.
        :param barcode: Código de barras del producto a buscar.
        :return: Objeto 'product.product' si existe, None de lo contrario.
        """
        Product = self.env['product.product']

        # Si es Enterprise, buscar primero por barcode
        if odoo.release.version_info[4] == 'e':
            existing_product = Product.search([('barcode', '=', barcode)], limit=1)
            if existing_product:
                return existing_product

        # Buscar por default_code
        existing_product = Product.search([('default_code', '=', barcode)], limit=1)
        if existing_product:
            return existing_product

        return None
    
    def find_missing_barcodes(self, barcodes):
        """
        Encuentra códigos de barras que no tienen productos asociados.
        En Community, busca en 'default_code'. En Enterprise, busca primero en 'barcode', luego en 'default_code'.
        :param barcodes: Lista de códigos de barras.
        :return: Lista de códigos de barras faltantes.
        """
        found_codes = set()

        # Si es Enterprise, buscar primero en barcode
        if odoo.release.version_info[4] == 'e':
            products_barcode = self.env['product.product'].search_read([('barcode', 'in', barcodes)], ['barcode'])
            found_codes.update(product['barcode'] for product in products_barcode)

            # Buscar los códigos que no se encontraron en 'barcode' en 'default_code'
            remaining_barcodes = set(barcodes) - found_codes
            if remaining_barcodes:
                products_default_code = self.env['product.product'].search_read([('default_code', 'in', list(remaining_barcodes))], ['default_code'])
                found_codes.update(product['default_code'] for product in products_default_code)
        else:
            # En Community, solo buscar en default_code
            products_default_code = self.env['product.product'].search_read([('default_code', 'in', barcodes)], ['default_code'])
            found_codes.update(product['default_code'] for product in products_default_code)

        missing_barcodes = set(barcodes) - found_codes
        return list(missing_barcodes)
    
    def get_products_by_barcode(self, barcode_list):
        """
        Retrieves product records based on a list of barcodes, associating each product with the found barcode.
        In Enterprise edition, first searches in 'barcode' field, then in 'default_code' field. In Community edition, searches only in 'default_code' field.
        :param barcode_list: List of barcodes.
        :return: Tuple of dictionary (barcode: product) and list of barcodes not found.
        """
        products_by_barcode = {}
        found_codes = set()

        # Si es Enterprise, buscar primero en barcode
        if odoo.release.version_info[4] == 'e':
            products_barcode = self.env['product.product'].search([('barcode', 'in', barcode_list)])
            for product in products_barcode:
                products_by_barcode[product.barcode] = product
                found_codes.add(product.barcode)

            # Buscar los códigos que no se encontraron en 'barcode' en 'default_code'
            remaining_barcodes = set(barcode_list) - found_codes
            if remaining_barcodes:
                products_default_code = self.env['product.product'].search([('default_code', 'in', list(remaining_barcodes))])
                for product in products_default_code:
                    products_by_barcode[product.default_code] = product
                    found_codes.add(product.default_code)
        else:
            # En Community, solo buscar en default_code
            products_default_code = self.env['product.product'].search([('default_code', 'in', barcode_list)])
            for product in products_default_code:
                products_by_barcode[product.default_code] = product
                found_codes.add(product.default_code)

        # Determinar los códigos no encontrados
        not_found_barcodes = set(barcode_list) - found_codes

        return products_by_barcode, list(not_found_barcodes)

