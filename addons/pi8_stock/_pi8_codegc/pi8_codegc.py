# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import odoo
from inspect import currentframe

from .._in_common.zlogger import ZLogger
logging.setLoggerClass(ZLogger)
_logger = logging.getLogger("testLogger")

class pi8_codegc(models.TransientModel):
    _name = 'pi8.codegc'
    _description = 'My Module Transient Model'
    # def __init__(self):
    #     self.logger = setup_zlogger('pi8_codegc')

    @api.model
    def parts_of_codegc(self, codegc):
        _logger.fini(currentframe().f_code.co_qualname, codegc=codegc)
        """
        Extrae las claves de 'linea', 'precio', y 'temporada' del código 'codegc'.
        :param codegc: El código del producto.
        :return: Diccionario con las claves de línea, precio y temporada.
        """
        if len(codegc) < 6:
            _logger.info("Código GC demasiado corto: %s", codegc)
            return {'linea_key': None, 'precio_key': None, 'temporada_key': None}

        # Dividir el código en segmentos
        linea_key = "L" + codegc[0:2]
        precio_key = "P" + codegc[2:4]
        temporada_key = "T" + codegc[4:6]

        to_return = {
            'linea_key': linea_key,
            'precio_key': precio_key,
            'temporada_key': temporada_key
        }
        _logger.fend(currentframe().f_code.co_qualname, to_return=to_return)
        return to_return

    @api.model
    def get_complete_codegc_info(self, codegc):
        _logger.fini(currentframe().f_code.co_qualname, codegc=codegc)
        """
        Extrae y valida las partes de un código GC, incluyendo la línea, el precio y la temporada.
        :param codegc: El código GC del producto.
        :return: Un diccionario con la información validada de línea, precio, temporada,
                o None si el código GC es inválido.
        """
        # Extraer las claves de línea, precio y temporada del código GC
        claves = self.parts_of_codegc(codegc)
        
        if not all(claves.values()):
            _logger.warning(f"Código GC inválido o incompleto: {codegc}")
            return None

        # Validar las partes del código GC
        linea = self.env['pi8.codegc.linea'].ckfield(claves['linea_key'])
        precio = self.env['pi8.codegc.precio'].ckfield(claves['precio_key'])
        temporada = self.env['pi8.codegc.temporada'].ckfield(claves['temporada_key'])
        to_return = None
        if linea and precio and temporada:
            _logger.info(f"Código GC válido: {codegc}")
            to_return = {
                'linea': linea,
                'precio': precio,
                'temporada': temporada
            }
        else:
            _logger.warning(f"Código GC inválido o falta información relacionada: {codegc}")
        _logger.fend(currentframe().f_code.co_qualname,to_return)
        return to_return
    
    @api.model
    def split_code_and_serial(self, code):
        parts = code.split('$', 1)  # Divide en dos partes usando '$' como separador
        product_code = parts[0]
        serial_number = parts[1] if len(parts) > 1 else None
        return product_code, serial_number
    
    @api.model        
    def validate_codegc(self, codegc):
        """
        ### HACER REFACTOR Y UNASR get_complete_codegc_info
        Valida el código 'codegc' asegurándose de que existan 'linea_name', 'precio_value', y 'temporada_name'.
        :param codegc: El código del producto a validar.
        :return: True si es válido, False si no lo es.
        """
        claves = self.parts_of_codegc(codegc)
        if not all(claves.values()):
            _logger.info(f"Código GC inválido o incompleto: {codegc}")
            return False
        
        linea =  self.env['pi8.codegc.linea'].ckfield(claves['linea_key'])
        precio = self.env['pi8.codegc.precio'].ckfield(claves['precio_key'])
        temporada = self.env['pi8.codegc.temporada'].ckfield(claves['temporada_key'])
        
        if linea and precio and temporada:
            _logger.info("Código GC válido: %s", codegc)
            return {
                'linea': linea,
                'precio': precio,
                'temporada': temporada
            }
        else:
            _logger.warning(f"Código GC inválido o falta información relacionada: {codegc}")
            return None

    @api.model
    def product_from_codegc(self, codegc):
        # Validar el código del producto
        valid_codegc = self.validate_codegc(codegc)
        if not valid_codegc:
            _logger.info("Validación fallida para el código: %s", codegc)
            raise UserError(_("Código del producto inválido o falta información relacionada."))

        # Crear el diccionario de valores del producto
        product_vals = {
            'name': valid_codegc['linea'].name,
            'description': valid_codegc['temporada'].name,
            'list_price': float(valid_codegc['precio'].value),
            'default_code': codegc,
            'type': 'product',
            'sale_ok': True,
            'purchase_ok': True,
            'available_in_pos': True
        }

        # Agregar el campo 'barcode' si es la versión Enterprise
        if odoo.release.version_info[4] == 'e':
            product_vals['barcode'] = codegc
        return product_vals
    
    @api.model
    def create_product_from_codegc(self, codegc, check_if_exists=True):
        """
        Crea un nuevo producto basado en el código GCALOP.
        :param codegc: Código GCALOP del producto a crear.
        :param check_if_exists: Si es True, verifica si el producto ya existe antes de crear uno nuevo.
        :return: Objeto 'product.product' del producto existente o recién creado.
        """
        # Verificar si el producto ya existe, si se solicita
        if check_if_exists:
            existing_product = self.env['in.product'].exist_from_barcode(codegc)
            if existing_product:
                _logger.info("Producto ya existe con el código: %s", codegc)
                return existing_product

        # Preparar valores del producto
        product_vals = self.product_from_codegc(codegc)

        # Creación del producto
        Product = self.env['product.product']
        new_product = Product.create(product_vals)
        _logger.info('Producto creado: %s', new_product.name)
        return new_product


    @api.model
    def ensure_products_exist_from_list_codegc(self, list_codegc):
        """
        Crea productos para los códigos de barras faltantes.
        :param barcodes: Lista de códigos de barras.
        """
        missing_barcodes = self.env['in.product'].find_missing_barcodes(list_codegc)
        for codegc in missing_barcodes:
            try:
                product = self.create_product_from_codegc(codegc, False)
                _logger.info("Producto creado: %s", product.display_name)
            except Exception as e:
                _logger.error("Error al crear el producto: %s", str(e))
                raise UserError(_("Error al crear el producto: %s") % str(e))
