# -*- coding: utf-8 -*-
{
    'name': "PI8-Inventario-CodeGC",
    'version': "1.0",
    'category': "pi8",
    'summary': "PI8, estandar de códigos de productos (CodeGC)",
    'license': "LGPL-3",
    # any module necessary for this one to work correctly
    'depends': [
        'base', 'stock', 'point_of_sale'
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'pi8_stock/static/src/**/*',
        ],
    },
    'data':[
        # security
        '__settings/security.xml',
        '__settings/ir.model.access.csv',
        '__settings/menu.xml',
        
        '_pi8_codegc/pi8_codegc_linea.xml',
        '_pi8_codegc/pi8_codegc_precio.xml',
        '_pi8_codegc/pi8_codegc_temporada.xml',
        
        '_pi8_codegc/pi8_codegc_linea_data.xml',
        '_pi8_codegc/pi8_codegc_precio_data.xml',
        '_pi8_codegc/pi8_codegc_temporada_data.xml',
        
    
        'components/product_codegc_create_wizard.xml',
        'components/product_barcode_quickadd_wizard.xml',
    ]
}
