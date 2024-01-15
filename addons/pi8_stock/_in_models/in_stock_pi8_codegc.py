# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo
from odoo import http
from odoo.http import request, Response
from inspect import currentframe
import random

from .. import pi8 as PI8
from ..pi8 import zlog, logger


class in_stock_pi8_codegc(models.TransientModel):
    _name = 'in.stock.pi8.codegc'
    _description = 'Modelo Base GCALOP'
    
    # Diccionario de caché a nivel de clase
    codegc_cache = {}
    
    @staticmethod
    @zlog.function_handler
    def _get_codegc__get_keys(codegc):
        if len(codegc) < 6:
            logger.info("Código GC demasiado corto: %s", codegc)
            return {'linea_key': None, 'precio_key': None, 'temporada_key': None}

        # Dividir el código en segmentos
        catalog_key = codegc[0:1]
        linea_key = catalog_key + "L" + codegc[1:3]
        precio_key = catalog_key + "P" + codegc[3:5]
        temporada_key = catalog_key + "T" + codegc[5:7]

        to_return = {
            'linea_key': linea_key,
            'precio_key': precio_key,
            'temporada_key': temporada_key
        }
        return to_return

    @api.model
    @zlog.function_handler
    def get_codegc(self, codegc):
        # Verificar si el resultado ya está en caché
        if codegc in in_stock_pi8_codegc.codegc_cache:
            logger.info(f"Resultado obtenido del caché para: {codegc}")
            return in_stock_pi8_codegc.codegc_cache[codegc]

        # Extraer las claves de línea, precio y temporada del código GC
        claves = in_stock_pi8_codegc._get_codegc__get_keys(codegc)
        
        if not all(claves.values()):
            logger.warning(f"Código GC inválido o incompleto: {codegc}")
            return None

        # Validar las partes del código GC
        linea = self.env['pi8.codegc.linea'].ckfield(claves['linea_key'])
        precio = self.env['pi8.codegc.precio'].ckfield(claves['precio_key'])
        temporada = self.env['pi8.codegc.temporada'].ckfield(claves['temporada_key'])
        
        to_return = None
        if linea and precio and temporada:
            logger.info(f"Código GC válido: {codegc}")
            to_return = {
                'linea': linea,
                'precio': precio,
                'temporada': temporada
            }
            # Almacenar en caché
            in_stock_pi8_codegc.codegc_cache[codegc] = to_return
        else:
            logger.warning(f"Código GC inválido o falta información relacionada: {codegc}")

        return to_return






    
class in_stock_pi8_codegc_controller(http.Controller):
    @http.route('/api/codegc/generate', type='http', methods=['GET'], auth='public', csrf=False)
    @PI8.zlog.function_handler
    def superapi_codegc_generate(self, **post):
        
        qty = post.get('qty')
        grupo = post.get('grupo')
        codegc = post.get('codegc')
        ll = post.get('linea')
        tt = post.get('tmp')
        pp = post.get('tmp')
        precio = post.get('precio')

        if precio: 
            pp= self.env["pi8.codegc.precio"].find_key_by_group_and_value(grupo, precio)  
            pp= pp[2:] 

        codegc = ll + tt + pp
        if not ll or not tt or not pp:
            raise UserError("CodeGC es invalido: {codegc}")
        
        in_stock_pi8_codegc.PartCode.convert_from_base36(codegc)
        
        # elif:
        #    is_valid = CodeGC_PartCode.validate(codegc)
            
            

                    
        info_codegc = in_stock_pi8_codegc.get_codegc(codegc)
        tracking = info_codegc['linea']['tracking']
        serial = None
        if tracking == 'serial':
            serial == PI8.sx.base62.random_generate(codegc, 9)
            return codegc + '$' + serial
        elif tracking == 'lot':
            serial == PI8.sx.base62.random_generate(codegc, 9)
            return codegc + '&' + serial
        elif tracking == 'none':
            return codegc













# #FUNCIONES A DESCONTINUAR
#     def extraer_default_codes_unicos(codes_details):
#         default_codes = {detail['default_code'] for detail in codes_details if not detail.get('product_id') and detail.get('codegc_isvalid') == True}
#         return default_codes


        
#     @api.model
#     def ensure_products_exist_from_barcodes(self, barcodes):
#         missing_barcodes = self.env['in.product'].find_missing_barcodes(barcodes)
#         for codegc in missing_barcodes:
#             try:
#                 product = self.create_product_from_codegc(codegc, False)
#                 _logger.info("Producto creado: %s", product.display_name)
#             except Exception as e:
#                 _logger.error("Error al crear el producto: %s", str(e))
#                 raise UserError(_("Error al crear el producto: %s") % str(e))
    
    
#     @api.model        
#     def validate_codegc(self, codegc):
#         """
#         Valida el código 'codegc' asegurándose de que existan 'linea_name', 'precio_value', y 'temporada_name'.
#         :param codegc: El código del producto a validar.
#         :return: True si es válido, False si no lo es.
#         """
#         claves = self.parts_of_codegc(codegc)
#         if not all(claves.values()):
#             _logger.info("Código GC inválido o incompleto: %s", codegc)
#             return False
        
#         linea =  self.env['pi8.codegc.linea'].ckfield(claves['linea_key'])
#         precio = self.env['pi8.codegc.precio'].ckfield(claves['precio_key'])
#         temporada = self.env['pi8.codegc.temporada'].ckfield(claves['temporada_key'])
        
#         if linea and precio and temporada:
#             _logger.info("Código GC válido: %s", codegc)
#             return {
#                 'linea': linea,
#                 'precio': precio,
#                 'temporada': temporada
#             }
#         else:
#             _logger.warning("Código GC inválido o falta información relacionada: %s", codegc)
#             return None

#     @api.model
#     def product_from_codegc(self, codegc):
#         # Validar el código del producto
#         valid_codegc = self.validate_codegc(codegc)
#         if not valid_codegc:
#             _logger.info("Validación fallida para el código: %s", codegc)
#             raise UserError(_("Código del producto inválido o falta información relacionada."))

#         # Crear el diccionario de valores del producto
#         product_vals = {
#             'name': valid_codegc['linea'].name,
#             'description': valid_codegc['temporada'].name,
#             'list_price': float(valid_codegc['precio'].value),
#             'default_code': codegc,
#             'type': 'product',
#             'sale_ok': True,
#             'purchase_ok': True,
#             'available_in_pos': True
#         }

#         # Agregar el campo 'barcode' si es la versión Enterprise
#         if odoo.release.version_info[4] == 'e':
#             product_vals['barcode'] = codegc
#         return product_vals
    
#     @api.model
#     def create_product_from_codegc(self, codegc, check_if_exists=True):
#         """
#         Crea un nuevo producto basado en el código GCALOP.
#         :param codegc: Código GCALOP del producto a crear.
#         :param check_if_exists: Si es True, verifica si el producto ya existe antes de crear uno nuevo.
#         :return: Objeto 'product.product' del producto existente o recién creado.
#         """
#         # Verificar si el producto ya existe, si se solicita
#         if check_if_exists:
#             existing_product = self.env['in.product'].exist_from_barcode(codegc)
#             if existing_product:
#                 _logger.info("Producto ya existe con el código: %s", codegc)
#                 return existing_product

#         # Preparar valores del producto
#         product_vals = self.product_from_codegc(codegc)

#         # Creación del producto
#         Product = self.env['product.product']
#         new_product = Product.create(product_vals)
#         _logger.info('Producto creado: %s', new_product.name)
#         return new_product


#     @api.model
#     def ensure_products_exist_from_barcodes(self, barcodes):
#         """
#         Crea productos para los códigos de barras faltantes.
#         :param barcodes: Lista de códigos de barras.
#         """
#         missing_barcodes = self.env['in.product'].find_missing_barcodes(barcodes)
#         for codegc in missing_barcodes:
#             try:
#                 product = self.create_product_from_codegc(codegc, False)
#                 _logger.info("Producto creado: %s", product.display_name)
#             except Exception as e:
#                 _logger.error("Error al crear el producto: %s", str(e))
#                 raise UserError(_("Error al crear el producto: %s") % str(e))

#     @api.model
#     def ensure_products_exist_from_text_codes(self, text_codes):
#         try:
#             # Parse the text codes to get product codes, quantities, and serials
#             codes_quantities_serial, invalid_codes = self.env['sy.codes'].parse_codes_quantities_serials(text_codes)
#             if invalid_codes:
#                 raise UserError(_("Códigos inválidos encontrados: %s") % ', '.join(invalid_codes))
            
#             # Extract product codes
#             product_codes = [code for code, quantity, serial in codes_quantities_serial]

#             # Ensure products exist
#             self.ensure_products_exist_from_barcodes(product_codes)

#             # Extract serials
#             serials = [serial for _, _, serial in codes_quantities_serial if serial]
#             missing_serials = self.find_missing_serials(serials)

#             # Map missing serials to their corresponding products
#             missing_serials_to_products = {serial: code for code, _, serial in codes_quantities_serial if serial in missing_serials}

#         except Exception as e:
#             _logger.error("Error al procesar los códigos de texto: %s", str(e))
#             raise UserError(_("Error al procesar los códigos de texto: %s") % str(e))

#     @api.model
#     def find_missing_serials(self, serials):
#         """
#         Find serial numbers that do not exist in the system using the 'stock.production.lot' model.
#         :param serials: List of serial numbers to check.
#         :return: List of serials that do not exist.
#         """
#         StockProductionLot = self.env['stock.lot']
#         lots = StockProductionLot.search([('name', 'in', serials)])
        
#         existing_serials = {lot.name for lot in lots}
#         not_found_serials = [serial for serial in serials if serial not in existing_serials]

#         return not_found_serials

#     @api.model
#     def add_serial_to_product(self, product_code, serial_number):
#         """
#         Add a serial number to a specific product.
#         :param product_code: Code of the product to which the serial will be added.
#         :param serial_number: Serial number to add to the product.
#         """
#         Product = self.env['product.product']
#         StockProductionLot = self.env['stock.lot']

#         # Buscar el producto por su código
#         product = Product.search([('default_code', '=', product_code)], limit=1)
#         if not product:
#             raise UserError(_("Producto no encontrado con código: %s") % product_code)

#         # Verificar si el serial ya existe
#         existing_lot = StockProductionLot.search([('name', '=', serial_number)], limit=1)
#         if existing_lot:
#             raise UserError(_("El serial ya existe: %s") % serial_number)

#         # Crear un nuevo lote (serial) y asociarlo con el producto
#         new_lot = StockProductionLot.create({
#             'name': serial_number,
#             'product_id': product.id,
#         })
#         return new_lot