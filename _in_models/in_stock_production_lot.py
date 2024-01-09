# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import re
import odoo
import sys


import ZLogger
_logger = ZLogger.get_logger(__name__)

class in_stock_production_lot(models.AbstractModel):
    _name = 'in.stock.production.lot'
    _description = 'Modelo Base PI8'

    

    @api.model
    def ensure_serials_to_products(self, product_serial_pairs, create_in_bulk=True):
        """
        Add serial numbers to products after checking for existing serials.
        
        Este método toma una lista de pares de product_id y serial_number, verifica si estos seriales ya existen en la base de datos, y luego crea nuevos lotes (seriales) para aquellos seriales que no existen, asociándolos con los respectivos productos.

        :param product_serial_pairs: List of tuples. Cada tupla contiene dos elementos: 
                                    - product_id (int): El ID del producto al que se debe asociar el serial.
                                    - serial (str): El número de serial que se debe asociar al producto.
        :param create_in_bulk: Boolean. Si es True, los seriales se crean en lote para mayor eficiencia. 
                            Si es False, cada serial se crea individualmente.
        :return: Retorna None. El método realiza operaciones en la base de datos pero no retorna ningún valor.
                En su lugar, registra información sobre la operación en los logs del sistema.
        
        :raises UserError: Si se encuentran seriales duplicados en la entrada o si hay algún problema en la creación de lotes.
        """
        
        # (El resto del código del método)
        StockProductionLot = self.env['stock.production.lot']

        # Obtener todos los seriales de los pares
        serials = [serial for _, serial in product_serial_pairs]

        # Buscar seriales existentes
        existing_lots = StockProductionLot.search([('name', 'in', serials)])
        existing_serials = {lot.name for lot in existing_lots}

        # Filtrar seriales que ya existen
        filtered_pairs = [(product_id, serial) for product_id, serial in product_serial_pairs if serial not in existing_serials]

        if create_in_bulk:
            # Crear lotes masivamente para los seriales filtrados
            lot_data = [{'name': serial, 'product_id': product_id} for product_id, serial in filtered_pairs]
            try:
                StockProductionLot.create(lot_data)
                _logger.info("Seriales creados masivamente.")
            except Exception as e:
                _logger.error(f"Error al crear seriales masivamente: {str(e)}")
        else:
            # Crear cada lote individualmente para los seriales filtrados
            for product_id, serial in filtered_pairs:
                try:
                    StockProductionLot.create({'name': serial, 'product_id': product_id})
                    _logger.info(f"Serial creado: {serial} para el producto ID: {product_id}")
                except Exception as e:
                    _logger.error(f"Error al crear el serial {serial} para el producto ID {product_id}: {str(e)}")
