# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import re
import odoo
import sys

class in_stock_picking(models.AbstractModel):
    _name = 'in.stock.picking'
    _description = 'Modelo Base GCALOP'  

    def add_stock_moves_to_picking(self, codes_quantities, picking_id, group_and_sort=False):
        """
        Agrega movimientos de stock a un picking específico.
        """
        # Crear los movimientos de stock con la información del picking
        stock_moves = self.env['in.stock.move'].create_stock_moves(codes_quantities, picking_id, group_and_sort)

        # Agregar los movimientos de stock al picking
        for move in stock_moves:
            self.env['stock.move'].create(move)

        return True



    def add_stock_moves_to_picking_from_text(self, text_codes, picking_id, group_and_sort=False):
        """
        Procesa un texto con códigos y cantidades, y agrega los movimientos de stock al picking especificado.
        """
        # Acceder al modelo in.product
        in_product_model = self.env['in.product']

        # Paso 1: Procesar los códigos y cantidades utilizando in.product
        codes_quantities, invalid_codes = in_product_model.parse_codes_and_quantities(text_codes)

        # Verificar si hay códigos inválidos
        if invalid_codes:
            raise UserError(f"Códigos inválidos encontrados: {', '.join(invalid_codes)}")

        # Paso 2: Utilizar el método add_stock_moves_to_picking para agregar los movimientos
        return self.add_stock_moves_to_picking(codes_quantities, picking_id, group_and_sort)