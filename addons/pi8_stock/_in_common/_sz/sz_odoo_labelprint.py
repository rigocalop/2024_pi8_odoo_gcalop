from ..zlogger_handlers import *
from odoo import models, _, api, SUPERUSER_ID
from ..zlogger import ZLogger
from .._sy import lib_sy as sy
from .._sx import lib_sx as sx
import re
import os
from dotenv import load_dotenv
from .sz_odoo_codegclot import sz_Odoo_CodegcLot
import requests
import pika
import threading

class in_stock_labelprint():
    _name = 'in.stock.labelprint'
    _description = 'Stock Label Printing'
    
    # @api.model
    # def callback(cls, method, properties, body):
    #     # Decodificar body de bytes a string
    #     message_str = body.decode('utf-8')
        
    #     # Cargar el string como un objeto Python
    #     message = json.loads(message_str)
        
    #     # Extraer los valores necesarios
    #     codegc = message['codegc']
    #     qty = int(message['qty'])  # Asegurarse de convertir qty a int
    #     template_key = message['template_key']
    #     idDevice = message['idDevice']
    #     namePrinter = message['namePrinter']
        
    #     # Ejecutar ToPrintLabel_FromCodeGc con los valores extraídos
    #     in_stock_labelprint.ToPrintLabel_FromCodeGc(codegc, qty, template_key, idDevice, namePrinter)

    #     print(" [x] Received %r" % body)
    #         # Aquí puedes añadir la lógica para procesar el mensaje
    # # Establecer conexión
    
    
    # def iniciar_consumidor():
    #     credentials = pika.PlainCredentials('admin','admin')
    #     parameters = pika.ConnectionParameters(host='31.220.17.110', port='5672', credentials=credentials)
    #     connection = pika.BlockingConnection(parameters)
    #     channel = connection.channel()

    #     channel.queue_declare(queue='X190200', durable=True, exclusive=False)

    #     channel.basic_consume(queue='X190200', on_message_callback=in_stock_labelprint.callback, auto_ack=True)

    #     print(' [*] Waiting for messages. To exit press CTRL+C')
    #     channel.start_consuming()
        

    # # Usar un hilo para no bloquear el hilo principal de Odoo
    # thread = threading.Thread(target=iniciar_consumidor)
    # thread.start()        
    # # Diccionario de caché a nivel de clase
    # codegc_cache = {}


    
# class sz_Odoo_LabelPrint:
    @classmethod
    @hlog_atomic()
    def send_to_labelpritner(cls, data_zpl, idDevice, printername):
        load_dotenv()
        PI8DEVICES_HOST = os.environ.get('PI8DEVICES_HOST')
        url = F'{PI8DEVICES_HOST}/api/ToDevice/{idDevice}'
        headers = {
            'action': "printraw",
            'actionmode': 'local',
            'prm1': printername,
            'Content-Type': 'text/plain'
        }
        
        # Realizar la solicitud POST
        response = requests.post(url, headers=headers, data=data_zpl)
        
        # Verificar el estado de la respuesta y actuar en consecuencia
        if response.status_code == 200:
            print("Solicitud exitosa.")
            return response.text
        else:
            print(f"Error en la solicitud: {response.status_code}")
            return None
    
        # is_success, codegclot = sz.Odoo_CodegcLot.Generate(env=request.env, codegc=codegc, qty=qty, moreinfo=moreinfo)
    @classmethod
    @hlog_superfunc()
    def ToPrintLabel_FromCodeGc(cls, env, codegc, qty, template_key, idDevice, namePrinter):
        issucces, entries = sz_Odoo_CodegcLot.Generate(env=env, codegc=codegc,qty=qty)
        if issucces == False:
            return False, entries
        return cls.ToPrintLabel_FromCodeGcLot(env, entries, template_key=template_key, idDevice=idDevice, namePrinter=namePrinter)
    
    @classmethod
    @hlog_superfunc()
    def ToPrintLabel_FromCodeGcLot(cls, env, textcodes, template_key, idDevice, namePrinter):
        def generar_texto_completo_zpl(entries, template_zpl):
            texto_completo = ""
            for record in entries:
                template_personalizado = template_zpl
                # Reemplaza el marcador {code} en el template con el código actual
                template_personalizado = template_personalizado.replace("{{CODEGCLOT}}", record['entry'])
                template_personalizado = template_personalizado.replace("{{CODEGC}}", record['code'])
                price_formated = "$ {:,.2f}".format(record['price'])
                template_personalizado = template_personalizado.replace("{{PRICE}}", price_formated)
                template_personalizado = template_personalizado.replace("{{PRODUCT_DESC}}", record['product_desc'])
                template_personalizado = template_personalizado.replace("{{PRODUCT_NAME}}", record['product_name'])
                
                # Agrega el template personalizado al texto completo, seguido de un salto de línea si es necesario
                texto_completo += template_personalizado + "\n"
            return texto_completo
        load_dotenv()
        if template_key == 'main':
            PI8DEVICES_LABELPRINTER_MAIN_ZPL = os.environ.get('PI8DEVICES_LABELPRINTER_MAIN_ZPL').replace('\\n', '\n')
        else: 
            PI8DEVICES_LABELPRINTER_MAIN_ZPL = os.environ.get('PI8DEVICES_LABELPRINTER_MAIN_ZPL').replace('\\n', '\n')
        # Asegurar la extracción de los datos
        textcodes = sx.XList.ensure(textcodes)
        joinProduct= {
            "uom_id":"product_uom",
            "display_name":"product_desc",
            "name": "product_name",
            "list_price":"price"
        }
        joinLot= {
            "name": "lot",
            "product_uom_id": "product_uom_id"
        }

        is_success, entries = sz_Odoo_CodegcLot.EnsureData(env=env, entries=textcodes, joinProduct=joinProduct, joinLot=joinLot)
        if is_success == False:
            return False, entries    
        
        try:
            data_zpl = generar_texto_completo_zpl(entries,PI8DEVICES_LABELPRINTER_MAIN_ZPL)
            cls.send_to_labelpritner(data_zpl, idDevice, namePrinter)
            return True, { 'message' : 'Send to Printer Label successfully'}
        except Exception as e:
            False, e
        
    