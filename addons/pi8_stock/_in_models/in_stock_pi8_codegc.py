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
    @staticmethod
    def filter_dictionary_by_keys(keys_list, original_dict):
        """
        Filtra un diccionario, dejando solo las claves especificadas en keys_list.

        :param keys_list: Una cadena de texto con claves separadas por comas.
        :param original_dict: El diccionario original a filtrar.
        :return: Un nuevo diccionario con solo las claves especificadas.
        """
        # Convertimos la cadena de claves en una lista, separando por comas y eliminando espacios en blanco
        keys = [key.strip() for key in keys_list.split(',')]

        # Creamos un nuevo diccionario que contenga solo las claves de interés
        filtered_dict = {key: original_dict[key] for key in keys if key in original_dict}

        return filtered_dict

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
            linea = self.filter_dictionary_by_keys('key,name,tracking', linea)
            precio = self.filter_dictionary_by_keys('key,name,value', precio)
            temporada = self.filter_dictionary_by_keys('key,name', temporada)
            
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


