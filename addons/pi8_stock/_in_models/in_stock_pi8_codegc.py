# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import http
from odoo.http import request, BadRequest, Response
from ..pi8 import zlog, logger, sx, sy, hlog
from werkzeug.exceptions import BadRequest, NotFound
import json

class in_stock_pi8_codegc(models.TransientModel):
    _name = 'in.stock.pi8.codegc'
    _description = 'Modelo Base GCALOP'
    
    # Diccionario de caché a nivel de clase
    codegc_cache = {}
    
    #deprecado
    @staticmethod
    @hlog.hlog_function()
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
            'catalog_key': catalog_key,
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

    @hlog.hlog_function()
    def get_codegc(self, codegc):
        # Verificar si el resultado ya está en caché
        if codegc in in_stock_pi8_codegc.codegc_cache:
            logger.info(f"Resultado obtenido del caché para: {codegc}")
            return in_stock_pi8_codegc.codegc_cache[codegc]

        # Extraer las claves de línea, precio y temporada del código GC
        claves = self._get_codegc__get_keys(codegc)
        
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
            codegc= linea['key'][0:1] +  linea['key'][2:4] + precio['key'][2:4] + temporada['key'][2:4]
            codegc = sx.base36.add_verifier(codegc)
            logger.info(f"Código GC válido: {codegc}")
            to_return = {
                'codegc': codegc,
                'linea': linea,
                'precio': precio,
                'temporada': temporada
            }
            # Almacenar en caché
            in_stock_pi8_codegc.codegc_cache[codegc] = to_return
        else:
            logger.warning(f"Código GC inválido o falta información relacionada: {codegc}")
        return to_return
    
    @hlog.hlog_function()
    def valid(self, codegc):
        codegc = self.get_codegc(codegc)
        return codegc is not None
        
    
    @hlog.hlog_function()
    def generate_codegc_with_tracking(self, codegc):
        """
        Genera un código identificador con información de tracking adjunta, basado en la información asociada al 'codegc' proporcionado.

        La función primero recupera información relacionada con el 'codegc' mediante el método 'get_codegc'. Luego, basándose en el tipo de tracking ('serial' o 'lot') definido en la información de la línea del 'codegc', genera un serial único. Finalmente, devuelve el 'codegc' con el serial adjunto, formateado de acuerdo al tipo de tracking.

        Parámetros:
        - codegc (str): El código identificador para el cual se generará la información de tracking.

        Devuelve:
        - str: El 'codegc' con la información de tracking adjunta. El formato del retorno depende del tipo de tracking:
            - Si el tracking es de tipo 'serial', devuelve 'codegc$serial'.
            - Si el tracking es de tipo 'lot', devuelve 'codegc&serial'.
            - Si no hay un tipo de tracking definido, devuelve el 'codegc' original.

        Lanza:
        - ValueError: Si no se encuentra información para el 'codegc' proporcionado.

        Ejemplo:
        - generate_codegc_with_tracking("12345") podría devolver "12345$67890" si el tipo de tracking es 'serial'.
        """
        codegc_info = self.get_codegc(codegc)
        if not codegc_info:
            raise ValueError(f"No se encontró información para el codegc: {codegc}")
        codegc_verifier = codegc_info['codegc']
        lot_name = sy.codegc.generate_serial(codegc_verifier, 10)
        if codegc_info['linea']['tracking'] == 'serial':
            return f'{codegc}${lot_name}'
        elif codegc_info['linea']['tracking'] == 'lot':
            return f'{codegc}&{lot_name}'
        else:
            return codegc



class in_stock_pi8_codegc_controller(http.Controller):
    @http.route('/api/codegc/<codegc>', type='http', methods=['GET'], auth='public', csrf=False)
    @hlog.hlog_api()
    def superapi_codegc_get(self, codegc):
        codegc_info = request.env['in.stock.pi8.codegc'].get_codegc(codegc)
        if not codegc_info: return BadRequest(codegc)
        return codegc_info
    
    @http.route('/api/codegc/<codegc>/tracking/generate', type='http', methods=['POST'], auth='public', csrf=False)
    @hlog.hlog_api()
    def superapi_codegc_tracking_get(self, codegc, **kwargs):
        model = request.env['in.stock.pi8.codegc']
        codegc_info = model.get_codegc(codegc)
        if not codegc_info: return BadRequest(codegc)
        codegc_verifier = codegc_info['codegc']

        # Generar múltiples códigos con tracking
        qty = int(request.params.get('qty', 1))
        generated_codes = [model.generate_codegc_with_tracking(codegc_verifier) for _ in range(qty)]
        return generated_codes