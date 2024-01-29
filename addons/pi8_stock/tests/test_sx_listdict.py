import unittest
from odoo.tests.common import TransactionCase
import logging
from .._in_common._sx.sx_xlistdict  import sx_XListDict as XListDict

_logger = logging.getLogger(__name__)

class test_sx_listdict(TransactionCase):
    def test_Select(self):
        # Datos de prueba
        test_data = [
            {'nombre': 'Ana', 'ciudad': 'Madrid', 'ventas': 10},
            {'nombre': 'Luis', 'ciudad': 'Madrid', 'ventas': 20},
            {'nombre': 'Carlos', 'ciudad': 'Barcelona', 'ventas': 15},
            {'nombre': 'Diana', 'ciudad': 'Valencia', 'ventas': 5},
            {'nombre': 'Eva', 'ciudad': 'Madrid', 'ventas': 30},
            {'nombre': 'Fernando', 'ciudad': 'Barcelona', 'ventas': 25},
            {'nombre': 'Gloria', 'ciudad': 'Valencia', 'ventas': 7},
            {'nombre': 'Hugo', 'ciudad': 'Madrid', 'ventas': 10},
            {'nombre': 'Irene', 'ciudad': 'Barcelona', 'ventas': 20},
            {'nombre': 'Jorge', 'ciudad': 'Valencia', 'ventas': 8}
        ]

        # Parámetros de prueba
        fields = ['nombre', 'ventas']
        filters = [('ciudad', '=', 'Madrid'), ('ciudad', 'empty', None)]
        order = 'ventas desc'
        distinct = True
        mapping = {'nombre': 'Nombre', 'ventas': 'Ventas'}

        # Ejecutar el método Select
        result1 = XListDict.Select(test_data, fields=fields, filters=filters, order=order, mapping=mapping)
        result2 = XListDict.SelectGroup(test_data, grouping_fields=['ciudad'], grouping_operations=[('ventas','sum','total_ventas')], order=order, mapping=mapping)

        # Verificar el resultado
        expected_result = [
            # [Define el resultado esperado de la prueba]
        ]
        self.assertEqual(result1, expected_result)