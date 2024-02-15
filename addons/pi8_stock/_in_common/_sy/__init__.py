# -*- coding: utf-8 -*-
from .sy_codegclot import sy_CodegcLot
from .sy_odoo_orm import sy_Odoo_ORM
from .sy_odoo_model import sy_Odoo_Model
from .sy_api import sy_Api

class lib_sy:
    CodegcLot = sy_CodegcLot
    Api = sy_Api
    class Odoo:
        ORM = sy_Odoo_ORM
        Model = sy_Odoo_Model


