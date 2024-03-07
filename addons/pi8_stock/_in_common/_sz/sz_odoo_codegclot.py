from ..zlogger_handlers import *
from odoo import models, _
from ..zlogger import ZLogger
from .._sy import lib_sy as sy
from .._sx import lib_sx as sx
import re


class sz_Odoo_CodegcLot:
        
    # Diccionario de caché a nivel de clase
    codegc_cache = {}

    
    @classmethod
    @hlog_atomic()
    def _entries_to_moreinfo(cls, env, entries):
        """
        Procesa una lista de códigos de texto de entrada y los clasifica como válidos o inválidos.
        :param entry_textcodes: Lista de cadenas de texto, cada una con formatos como 'codigo$lote*cantidad' o 'codigo&lote*cantidad'.
        :param default_values: Valores iniciales por defecto para aplicar a cada entrada antes de la expansión.
        :param mapping_dict: Diccionario de mapeo para asignar campos de las entradas expandidas a nuevos nombres de campos.
        :param validation_function: Función opcional para validar el 'default_code'.
        :return: Dos listas: la primera con las entradas válidas y la segunda con las entradas inválidas.
        """
        notError = True
        to_return = []
        for entry in entries:
            
            try:
                isvalid, info = cls._info_codegc(env, entry)
                if not isvalid:
                    notError = False
                expandentry = sy.CodegcLot.expandEntry(entry=entry)
                info.update(expandentry)

                to_return.append(info)
                # Validar 'default_code' si la función de validación está disponible
            except Exception as e:
                notError = False
                to_return.append({'entry': entry, 'msg': str(e)})
        return notError, to_return

    @classmethod
    @hlog_atomic()
    def _info_codegc(cls, env, codegclot, expandcode = True):
        """
        Procesa una lista de códigos de texto de entrada y los clasifica como válidos o inválidos.
        :param entry_textcodes: Lista de cadenas de texto, cada una con formatos como 'codigo$lote*cantidad' o 'codigo&lote*cantidad'.
        :param default_values: Valores iniciales por defecto para aplicar a cada entrada antes de la expansión.
        :param mapping_dict: Diccionario de mapeo para asignar campos de las entradas expandidas a nuevos nombres de campos.
        :param validation_function: Función opcional para validar el 'default_code'.
        :return: Dos listas: la primera con las entradas válidas y la segunda con las entradas inválidas.
        """
        if len(codegclot) < 7:
            return False, {'entry': codegclot, 'info': 'El codegclot demasiado corto.'}
        
        # Dividir el código en segmentos
        catalog_key = codegclot[0:1]
        linea_key = catalog_key + "L" + codegclot[1:3]
        precio_key = catalog_key + "P" + codegclot[3:5]
        temporada_key = catalog_key + "T" + codegclot[5:7]
        
        # Inicializar las variables para almacenar las validaciones
        linea = precio = temporada = None
        msg_error = ""

        # Validar las partes del código GC
        try:
            linea = env['pi8.codegc.linea'].ckfield(linea_key)
            precio = env['pi8.codegc.precio'].ckfield(precio_key)
            temporada = env['pi8.codegc.temporada'].ckfield(temporada_key)
        except Exception as ex:
            return False, {'entry': codegclot, 'error': ex}
        
        # Construir el mensaje de error basado en la parte del código que falló la validación
        if (linea is None) or (precio is None) or (temporada is None):
            if linea is None:
                msg_error = f"Linea no valida: {linea_key}"
            elif precio is None:
                msg_error = f"Precio no valido: '{precio_key}"
            elif temporada is None:
                msg_error = f"Temporada no valida: {temporada_key}"
            return False,  {'entry': codegclot, 'info': msg_error}
        
        to_return = {
            'entry': codegclot,
            'linea': sx.XObj.copy(linea, ['key','name','depto','tracking']),
            'precio': sx.XObj.copy(precio, ['key','name','value']),
            'temporada': sx.XObj.copy(temporada, ['key','name'])
        }

        return True, to_return
        
    @classmethod
    @hlog_atomic()
    def _processTextCodes(cls, env, textcodes, default_values=None):
        """
        Procesa una lista de códigos de texto de entrada y los clasifica como válidos o inválidos.
        :param entry_textcodes: Lista de cadenas de texto, cada una con formatos como 'codigo$lote*cantidad' o 'codigo&lote*cantidad'.
        :param default_values: Valores iniciales por defecto para aplicar a cada entrada antes de la expansión.
        :param mapping_dict: Diccionario de mapeo para asignar campos de las entradas expandidas a nuevos nombres de campos.
        :param validation_function: Función opcional para validar el 'default_code'.
        :return: Dos listas: la primera con las entradas válidas y la segunda con las entradas inválidas.
        """
        valid_entries = []
        invalid_entries = []
        textcodes = sx.XList.ensure(textcodes)

        for textcode in textcodes:
            try:
                # Aplicar valores por defecto si están disponibles
                entry = default_values.copy() if default_values else {}
                expanded_entry = sy.CodegcLot.expandTextCode(textcode=textcode)
                
                entry.update(expanded_entry)

                # Validar 'default_code' si la función de validación está disponible
                if 'code' in entry:
                    codegclot = entry['entry']
                    isvalid, info = cls.ValidateCodegcLot(env, codegclot)
                    if not isvalid:
                        raise sy.CodegcLot.ExceptionEntryCodeLot({'entry': codegclot, 'msg': info})
                    else:
                        valid_entries.append(entry)
            except sy.CodegcLot.ExceptionEntryCodeLot as ex1:
                invalid_entries.append(ex1.message)
            except Exception as e:
                invalid_entries.append({'entry': textcode, 'msg': str(e)})

        return valid_entries, invalid_entries

    @classmethod
    @hlog_function()
    def ValidateCodegcLot(cls, env, codegclot):
        isvalid, info_base = sy.CodegcLot.validate(codegclot)
        if not isvalid:
            return False, info_base

        isvalid, info_odoo = cls._info_codegc(env, codegclot)
        if isvalid is None:
            return False, info_odoo
        else:
            tracking_base = info_base['tracking'] 
            tracking_odoo = info_odoo['linea']['tracking']
            if tracking_base != tracking_odoo:
                return False, f'El tracking *{tracking_base}* no corresponde al de la linea *{tracking_odoo}*'

            return True, info_odoo
        
    @classmethod
    @hlog_superfunc()
    def Ensure(cls, env, textcodes, return_entries=True):
        logger = ZLogger.get_logger()

        def joinLot_ModeTextCode(env, target_list):
            return sy.Odoo.ORM.Join(env,target_data=target_list, target_fieldon='lot', model='stock.lot', reference_fieldon='name',join_fields={'id': 'lot_id', 'product_id': None})
            
        def joinCode_ModeTextCode(env, target_list):
            return sy.Odoo.ORM.Join(env,target_data=target_list, target_fieldon='code', model='product.product', reference_fieldon='default_code',join_fields={'id': 'product_id'})
        
        def createStockLots_FromCodeValues(env, list_lots):
            lots_to_create = []
            for item in list_lots:
                new_lot = {
                    'product_id': item['product_id'],
                    'name': item['lot']
                }
                lots_to_create.append(new_lot)
                logger.warning(f"LOTs Agregados: {item['lot']}")
                
            # Create products in the environment
            odoomodel = env['stock.lot']
            to_return = None
            if isinstance(odoomodel, models.Model):
                to_return = odoomodel.create(lots_to_create)
            return to_return
        
        def createProducts_FromCodeValues(env, list_codes):
            # Iterate over each product and create new products
            products_to_create = []
            for item in list_codes:
                item = item[0]
                isvalid, codegc_info = cls._info_codegc(env, item)

                new_product = {
                    'name': codegc_info['linea']['name'],
                    'description': codegc_info['temporada']['name'],
                    'list_price': float(codegc_info['precio']['value']),
                    'default_code': item,
                    'tracking': codegc_info['linea']['tracking'],
                    'sale_ok': True,
                    'purchase_ok': True,
                    'available_in_pos': True,
                    'type': 'product'
                }

                logger.warning(f"Producto Agregado: {item}")
                products_to_create.append(new_product)

            # Create products in the environment
            odoomodel = env['product.product']
            to_return = None
            if isinstance(odoomodel, models.Model):
                to_return = odoomodel.create(products_to_create)
            return to_return
        
        list_CodeLot, entries_invalids = cls._processTextCodes(env=env, textcodes=textcodes, default_values={ 'product_id': None, 'lot_id': None })
        if len(entries_invalids) > 0:
            return False, entries_invalids
            
        list_CodeLot = joinLot_ModeTextCode(env=env, target_list=list_CodeLot)
        list_CodeLot = joinCode_ModeTextCode(env=env, target_list=list_CodeLot)
            
        # Actualizar información desde 'stock.lot' para los casos en que no se encuentre el lot_name
        list_to_create = sx.XListDict.SelectDistinct(listdict=list_CodeLot, fields=['code'], filters=[('code', 'not empty', None),('product_id', 'empty', None)])
        
        if len(list_to_create) > 0:
            updatestatus = createProducts_FromCodeValues(env=env, list_codes=list_to_create)
            list_CodeLot = joinCode_ModeTextCode(env=env, target_list=list_CodeLot)

                
        # actualizar información desde 'product.product' para los casos en que no se encuentre el 'product.product'
        list_to_create = sx.XListDict.SelectDistinct(listdict=list_CodeLot, fields=['product_id','lot'], filters=[('lot', 'not empty', None) ,('lot_id', 'empty', None)], return_tuples=False)
        if len(list_to_create) > 0:
            updatestatus = createStockLots_FromCodeValues(env=env, list_lots=list_to_create)
            list_CodeLot = joinLot_ModeTextCode(env=env, target_list=list_CodeLot)
                
        if return_entries:
            return True, list_CodeLot
        return True, None

    
    # "product_id,lot_id,product_uom_qty,product_uom,name,lot_name"
    
    @classmethod
    @hlog_superfunc()
    def Generate(cls, env, codegc, qty=1, moreinfo = False):
        isvalid, info = cls._info_codegc(env, codegc)
        if not isvalid:
            return isvalid, info
        
        # Inicializar un arreglo para almacenar los códigos de lote generados
        to_return = []
        
        # Generar la cantidad 'qty' de códigos de lote
        for _ in range(qty):
            codegclot = sy.CodegcLot.generate(codegc=codegc, tracking=info['linea']['tracking'], length_lot=10)
            to_return.append(codegclot)
        
        if moreinfo:
            to_return = cls._entries_to_moreinfo(env, to_return)
        
        return True, to_return

    @classmethod
    @hlog_superfunc()
    def EnsureData(cls, env, entries, joinProduct, joinLot):
        logger = ZLogger.get_logger()
        isvalid, data = cls.Ensure(env=env, textcodes=entries, return_entries=True)
        if not isvalid:
            return False, data
                
        data = sy.Odoo.ORM.Join(env, target_data=data,target_fieldon='product_id',model='product.product', reference_fieldon='id', join_fields=joinProduct)
        data = sy.Odoo.ORM.Join(env, target_data=data,target_fieldon='lot_id',model='stock.lot', reference_fieldon='id', join_fields=joinLot)
        return True, data
    
    
