# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError
import logging
import re

_logger = logging.getLogger(__name__)
class codegc_product_create_wizard(models.TransientModel):
    _name = "pi8.stock.codegc.product.create.wizard"

    _description = 'Create_CodeGC_Wizard'
    codes = fields.Text(string='Codes')
    
    def ensure_products_exist_from_text_codes(self):
        self.env['pi8.codegc'].ensure_products_exist_from_text_codes(self.codes)
