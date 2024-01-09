# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import re
import odoo
import sys

class in_stock_move(models.AbstractModel):
    _name = 'in.stock.move'
    _description = 'Modelo Base GCALOP'  

    def group_and_sort_stock_moves(self, stock_moves):
        """
        Agrupa y ordena los movimientos de stock por product_id.
        :param stock_moves: Lista de diccionarios que representan los movimientos de stock.
        :return: Lista de diccionarios representando los movimientos de stock agrupados y ordenados.
        """
        from collections import defaultdict

        # Crear un diccionario para acumular las cantidades por product_id
        grouped_moves = defaultdict(lambda: {'product_id': 0, 'product_uom_qty': 0, 'product_uom': None, 'name': ''})
        
        for move in stock_moves:
            product_id = move['product_id']
            grouped_moves[product_id]['product_id'] = product_id
            grouped_moves[product_id]['product_uom_qty'] += move['product_uom_qty']
            grouped_moves[product_id]['product_uom'] = move['product_uom']
            grouped_moves[product_id]['name'] = move['name']  # Podría ser el nombre del último producto encontrado

        # Convertir el diccionario en una lista y ordenar por product_id
        sorted_moves = sorted(grouped_moves.values(), key=lambda x: x['product_id'])
        return sorted_moves

    def generate_basic_stock_moves(self, codes_quantities, group_and_sort=False):
        # Paso 2: Obtener los productos utilizando in.product
        in_product_model = self.env['in.product']
        barcodes = [code for code, _ in codes_quantities]
        products_by_barcode, not_found_barcodes = in_product_model.get_products_by_barcode(barcodes)

        # Verificar si hay productos no encontrados
        if not_found_barcodes:
            raise UserError(f"Códigos de producto no encontrados: {', '.join(not_found_barcodes)}")

        # Preparar los movimientos de stock solo con la información básica del producto
        stock_moves = []
        for barcode, qty in codes_quantities:
            product = products_by_barcode.get(barcode)
            if product:
                stock_move_data = {
                    'product_id': product.id,
                    'product_uom_qty': qty,
                    'product_uom': product.uom_id.id,
                    'name': product.display_name,
                }
                stock_moves.append(stock_move_data)

        # Opcionalmente agrupar y ordenar por product_id
        if group_and_sort:
            return self.group_and_sort_stock_moves(stock_moves)

        return stock_moves

    def create_stock_moves(self, codes_quantities, picking_id, group_and_sort=False):
        """
        Crea movimientos de stock a partir de los códigos y cantidades, agregando información de picking.
        """
        # Paso 1: Generar los movimientos básicos de stock
        stock_moves = self.generate_basic_stock_moves(codes_quantities, group_and_sort)

        # Paso 2: Obtener el picking y agregar información adicional a los movimientos
        picking = self.env['stock.picking'].browse(picking_id)
        if not picking.exists():
            raise UserError("Stock picking no encontrado.")

        # Agregar información específica del picking a cada movimiento de stock
        for move in stock_moves:
            move.update({
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'picking_id': picking.id,
            })

        return stock_moves