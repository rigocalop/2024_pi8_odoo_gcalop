from ..zlogger_handlers import *
from odoo import models, _
from ..zlogger import ZLogger
from .._sy import lib_sy as sy
from .._sx import lib_sx as sx


class sz_OdooCodeGC:
        
    # Diccionario de caché a nivel de clase
    codegc_cache = {}
    
    @classmethod
    @hlog_function()
    def GetInfoCodeGC(cls, env, codegc):
        logger = ZLogger.get_logger()
        
        def get_codegc__get_keys(codegc):
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
        

        # Verificar si el resultado ya está en caché
        if codegc in cls.codegc_cache:
            logger.info(f"Resultado obtenido del caché para: {codegc}")
            return cls.codegc_cache[codegc]

        # Extraer las claves de línea, precio y temporada del código GC
        claves = get_codegc__get_keys(codegc)  # Asegúrate que este método existe en tu clase

        if not all(claves.values()):
            logger.warning(f"Código GC inválido o incompleto: {codegc}")
            return None

        # Validar las partes del código GC
        linea = env['pi8.codegc.linea'].ckfield(claves['linea_key'])
        precio = env['pi8.codegc.precio'].ckfield(claves['precio_key'])
        temporada = env['pi8.codegc.temporada'].ckfield(claves['temporada_key'])

        to_return = None
        if linea and precio and temporada:
            linea = sx.XDict.Select(linea, fields=['key', 'name', 'tracking'])
            precio = sx.XDict.Select(precio, fields=['key', 'name', 'value'])
            temporada = sx.XDict.Select(temporada, fields=['key', 'name'])
            
            codegc = linea['key'][0:1] + linea['key'][2:4] + precio['key'][2:4] + temporada['key'][2:4]
            codegc = sx.base36.add_verifier(codegc)
            logger.info(f"Código GC válido: {codegc}")
            to_return = {
                'codegc': codegc,
                'linea': linea,
                'precio': precio,
                'temporada': temporada
            }
            # Almacenar en caché
            cls.codegc_cache[codegc] = to_return
        else:
            logger.warning(f"Código GC inválido o falta información relacionada: {codegc}")
        return to_return
    
    @classmethod
    @hlog_function()
    def ValidCodeGC(cls, env, codegc):
        codegc = cls.GetInfoCodeGC(env, codegc)
        return codegc is not None
    
    @classmethod
    @hlog_function()
    def CreateProducts_FromCodeValues(cls, env, list_codes):
        """
        Creates products from CodeGC.

        Args:
        env: The environment context.
        logger: Logger for logging messages.
        list_CodeLot: List of code lots to process.

        Returns:
        None, but it creates products in the environment.
        """
        # Iterate over each product and create new products
        logger = ZLogger.get_logger()
        products_to_create = []
        for item in list_codes:
            item = item[0]
            codegc_info = cls.GetInfoCodeGC(env, item)

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
        if isinstance(odoomodel, models.Model):
            odoomodel.create(products_to_create)

    @classmethod
    @hlog_function(default_error='Error al crear los lotes. Revizar que e exista el list con el campo lot y product_id')
    def CreateStockLots_FromCodeValues(cls, env, list_lots):
        logger = ZLogger.get_logger()
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
        if isinstance(odoomodel, models.Model):
            odoomodel.create(lots_to_create)

    @classmethod
    @hlog_function(fcomment="Agregado JOIN de datos a **list_CodeLot** desde 'stock.lot' para los casos en que encuentre el *lot*")
    def joinLot_ModeTextCode(cls, env, target_list, field_lot=['lot'], model_fields=['lot_id', 'name', 'product_id'], mapping_fields={'lot_id': 'id', 'product_id': 'product_id[0]'}):
        list_values = sx.XListDict.SelectDistinct(target_list, fields=field_lot, remove_empty=True)
        # reference_data = sy_OdooModel.SearchIn(env, model_name='stock.lot', fields=['id','name','product_id'], search_field='name', search_values=list_values, mapping_fields={'lot_id': 'id', 'product_id': 'product_id[0]'})
        reference_data = sy.OdooModel.SearchIn(env, model_name='stock.lot', fields=['id','name','product_id'], search_field='name', search_values=list_values, mapping_fields={'lot_id': 'id'})
        target_list = sx.XListDict.join(target_list, target_field_on='lot', reference_data=reference_data, reference_field_on='name', mapping_fields={'lot_id': 'lot_id', 'product_id': 'product_id'})
        return target_list
    
    @classmethod
    @hlog_function()
    def joinLot_ModeID(cls, env, target_list, field_lot='lot_id', model_fields=['lot', 'product_id'], mapping_fields={'lot': 'name', 'product_id': 'product_id[0]'}):
        # Actualizar información desde 'stock.lot' para los casos en que no se encuentre el lot_name
        list_values = sx.XListDict.SelectDistinct(target_list ,fields=field_lot, remove_empty=True)
        reference_data = sy.OdooModel.SearchIn(env, model_name='stock.lot',fields=model_fields, search_field='id', search_values=list_values, mapping_fields=mapping_fields)
        target_list = sx.XListDict.join(target_list, target_field_on= field_lot, reference_data=reference_data, reference_field_on='id', mapping_fields=mapping_fields)
        return target_list
        
    @classmethod
    @hlog_function()
    def joinCode_ModeTextCode(cls, env, target_list, field_code=['code'], model_fields=['id', 'default_code'], mapping_fields={'product_id': 'id'}):
        # Actualizar información desde 'stock.lot' para los casos en que no se encuentre el lot_name
        list_values = sx.XListDict.SelectDistinct(listdict=target_list ,fields=field_code, remove_empty=True)
        reference_data = sy.OdooModel.SearchIn(env, model_name='product.product',fields=model_fields, search_field='default_code', search_values=list_values)
        target_list = sx.XListDict.join(target_list, target_field_on=field_code, reference_data=reference_data, reference_field_on='default_code', mapping_fields=mapping_fields)
        return target_list

    @classmethod
    @hlog_function()
    def joinCode_ModeID(cls, env, target_list, field_id='product_id', model_fields=['id', 'code', 'uom_id'], mapping_fields={'code': 'default_code', 'product_oem': 'uom_id'}):
        """
        Actualiza la información de una lista de diccionarios con datos referenciados desde el modelo 'product.product' en Odoo.

        Esta función se utiliza para enriquecer una lista de diccionarios (target_list) con información adicional obtenida desde el modelo 'product.product', basándose en un campo de identificación común.

        Args:
            cls: La clase a la que pertenece este método. Debe ser una clase derivada de models.Model de Odoo.
            env: El entorno de Odoo utilizado para acceder a los registros de la base de datos.
            target_list (list of dict): Una lista de diccionarios que representa los registros que necesitan ser actualizados.
            field_id (str, opcional): El campo en `target_list` que se utiliza para hacer la correspondencia con los registros en 'product.product'. Por defecto es 'product_id'.
            model_fields (list of str, opcional): Los campos del modelo 'product.product' que se desean recuperar. Por defecto incluye ['id', 'code, product_oem'].
            mapping_fields (dict, opcional): Un diccionario que mapea los campos de 'product.product' a los campos en `target_list`. Esto permite renombrar los campos obtenidos del modelo a los nombres deseados en la lista de destino.

        Returns:
            list of dict: La lista actualizada de diccionarios con la información adicional de 'product.product' incorporada.

        Ejemplo:
            Supongamos que `target_list` es una lista de diccionarios donde cada uno representa un lote de producto, y queremos enriquecerla con el código por defecto ('default_code') y el ID de la unidad de medida ('uom_id') de cada producto referenciado por 'product_id':

            >>> target_list = [{'product_id': 1, 'lot_name': 'Lote1'}, {'product_id': 2, 'lot_name': 'Lote2'}]
            >>> enriched_list = joinCode_ModeID(cls, env, target_list)
            >>> print(enriched_list)
            # El resultado será `target_list` con los campos 'default_code' y 'product_uom_id' agregados desde 'product.product'.
        """
        list_values = sx.XListDict.SelectDistinct(target_list ,fields=field_id, remove_empty=True)
        reference_data = sy.OdooModel.SearchIn(env, model_name='product.product', fields=model_fields, search_field='id', search_values=list_values)
        target_list = sx.XListDict.join(target_list, target_field_on=field_id, reference_data=reference_data, reference_field_on='id', mapping_fields=mapping_fields)
        return target_list

    @classmethod
    @hlog_superfunc()
    def EnsureCodeLot(cls, env, textcodes):
        logger = ZLogger.get_logger()
        default_values = { 'product_id': None, 'lot_id': None }
        list_CodeLot, entries_invalids = sy.EntryCodeLot.processEntryTextCodes(env=env, textcodes=textcodes, default_values=default_values, validation_function = cls.ValidCodeGC)
        # if entries_invalids:
        #     return False, entries_invalids

        cls.joinLot_ModeTextCode(env=env, target_list=list_CodeLot)
        cls.joinCode_ModeTextCode(env=env, target_list=list_CodeLot)
        
        # Actualizar información desde 'stock.lot' para los casos en que no se encuentre el lot_name
        list_to_create = sx.XListDict.SelectDistinct(listdict=list_CodeLot, fields=['code'], filters=[('code', 'not empty', None),('product_id', 'empty', None)], )
        if len(list_to_create) > 0:
            cls.CreateProducts_FromCodeValues(env=env, list_codes=list_to_create)
            
        # actualizar información desde 'product.product' para los casos en que no se encuentre el 'product.product'
        list_to_create = sx.XListDict.SelectDistinct(listdict=list_CodeLot, fields=['product_id','lot'], filters=[('lot', 'not empty', None) ,('lot_id', 'empty', None)])
        list_to_create = sx.XListDict.from_tuples(list_to_create, ['product_id', 'lot'])
        
        
        
        
        if len(list_to_create) > 0:
            cls.CreateStockLots_FromCodeValues(env=env, list_lots=list_to_create)
        
        return True, list_CodeLot, entries_invalids
