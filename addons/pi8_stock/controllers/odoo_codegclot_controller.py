import json
from .._in_common.zlogger_handlers import hlog_api
from odoo import http, _, SUPERUSER_ID
from odoo.http import request, Response
import requests
import os
from dotenv import load_dotenv

from .._in_common._sy import lib_sy as sy
from .._in_common._sx import lib_sx as sx
from .._in_common._sz import lib_sz as sz
import pika
import threading


class Odoo_CodegcLot_Controller(http.Controller):

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
    #     sz.Odoo_LabelPrint.ToPrintLabel_FromCodeGc(request.env, codegc, qty, template_key, idDevice, namePrinter)

    #     print(" [x] Received %r" % body)
    #         # Aquí puedes añadir la lógica para procesar el mensaje
    # # Establecer conexión
    
    
    # def iniciar_consumidor():
    #     credentials = pika.PlainCredentials('admin','admin')
    #     parameters = pika.ConnectionParameters(host='31.220.17.110', port='5672', credentials=credentials)
    #     connection = pika.BlockingConnection(parameters)
    #     channel = connection.channel()

    #     channel.queue_declare(queue='X190200', durable=True, exclusive=False)

    #     channel.basic_consume(queue='X190200', on_message_callback=Odoo_CodegcLot_Controller.callback, auto_ack=True)

    #     print(' [*] Waiting for messages. To exit press CTRL+C')
    #     channel.start_consuming()
        

    # # Usar un hilo para no bloquear el hilo principal de Odoo
    # thread = threading.Thread(target=iniciar_consumidor)
    # thread.start()        
    # # Diccionario de caché a nivel de clase
    # codegc_cache = {}
    
    @http.route('/api/codegclot/toLabelPrint', type='http', methods=['POST'], auth='public', csrf=False)
    @hlog_api()
    def api_codegclot_toLabelPrint(self, **kw):
        # Asegurar la extracción de los datos
        data = json.loads(request.httprequest.data)
        textcodes = sx.XList.ensure(data)
        is_success, entries = sz.Odoo_LabelPrint.ToPrintLabel_FromCodeGcLot(textcodes=textcodes, template_key='main', idDevice='X190100', namePrinter='LabelPrinterX190')
        return sy.Api.ApiResponse(is_success=is_success, data=entries, message_error=f'Invalid entries found: {entries}')
    
    @http.route('/api/codegclot/print/fromcodegc', type='http', methods=['POST'], auth='none', csrf=False)
    @hlog_api()
    def api_codegclot_print_fromcodegc(self, **kw):
        # Asegurar la extracción de los datos
        data = json.loads(request.httprequest.data)
        codegc=data['codegc']
        qty=data['qty']
        idDevice=data['idDevice']
        namePrinter=data['namePrinter']
        
        env = request.env(user=SUPERUSER_ID)
        # is_success, entries =request.env["in.stock.labelprint"].ToPrintLabel_FromCodeGc(codegc=codegc, qty=qty, template_key='main', idDevice=idDevice, namePrinter=namePrinter)
        is_success, entries = sz.Odoo_LabelPrint.ToPrintLabel_FromCodeGc(env, codegc=codegc, qty=qty, template_key='main', idDevice=idDevice, namePrinter=namePrinter)
        return sy.Api.ApiResponse(is_success=is_success, data=entries, message_error=f'Invalid entries found: {entries}')
    
    
    
    @http.route('/api/codegclot/ensure', type='http', methods=['POST'], auth='public', csrf=False)
    @hlog_api()
    def api_codegclot_ensure(self, **kw):
        # Asegurar la extracción de los datos
        data = json.loads(request.httprequest.data)
        textcodes = sx.XList.ensure(data)

        # Extraer 'return_entries' como un parámetro de la URL, valor predeterminado a True si no se proporciona
        type_return = sy.Api.prmStr('return', '')
        return_entries = True if type_return.lower() != '' else False
        
        is_success, entries = sz.Odoo_CodegcLot.Ensure(env=request.env, textcodes=textcodes, return_entries=return_entries)
        if not return_entries: entries = { 'message' : 'Entries created successfully'}
        return sy.Api.ApiResponse(is_success=is_success, data=entries, message_error=f'Invalid entries found: {entries}')

    @http.route('/api/codegclot/generate', type='http', methods=['GET'], auth='public', csrf=False)
    @hlog_api()
    def api_codegclot_generate(self, **kw):
        # Extraer los parámetros 'codegc' y 'qty' del URL como parámetros de consulta
        codegc = sy.Api.prmStr('codegc', None, True)
        qty = sy.Api.prmInt('qty', 1)
        moreinfo = sy.Api.prmBool('moreinfo', False)

        # Llamar al método para generar el código de lote
        is_success, codegclot = sz.Odoo_CodegcLot.Generate(env=request.env, codegc=codegc, qty=qty, moreinfo=moreinfo)
        return sy.Api.ApiResponse(is_success=is_success,data=codegclot,message_error=f'{codegclot}')
        
    @http.route('/api/codegclot/ensure/data', type='http', methods=['POST'], auth='public', csrf=False)
    @hlog_api()
    def api_codegclot_ensure_data(self, **kw):
        # Asegurar la extracción de los datos
        data = json.loads(request.httprequest.data)
        
        # Extraer 'entries', 'joinProduct' y 'joinLot' del cuerpo de la solicitud JSON
        entries = data.get('entries', [])
        joinProduct = data.get('joinProduct', {})
        joinLot = data.get('joinLot', {})

        is_success, to_return = sz.Odoo_CodegcLot.EnsureData(env=request.env, entries=entries, joinProduct=joinProduct, joinLot=joinLot)
        return sy.Api.ApiResponse(is_success=is_success,data=to_return,message_error=f'{to_return}')



    def enviar_solicitud(url, body):
        # Headers para especificar que el contenido es JSON
        headers = {'Content-Type': 'application/json'}
        
        # Realizar solicitud POST
        response = requests.post(url, json=body, headers=headers)
        
        # Verificar el estado de la respuesta
        if response.status_code == 200:
            print("Solicitud exitosa.")
            # Procesar la respuesta si es necesario
            return response.json()  # O `response.text` si esperas texto plano
        else:
            print(f"Error en la solicitud: {response.status_code}")
            return None