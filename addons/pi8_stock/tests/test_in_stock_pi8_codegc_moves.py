from odoo.tests.common import TransactionCase
from odoo.tests import HttpCase, tagged
import json
from ..pi8 import zlog, sy, sx, hlog
from .._in_common.zlogger_formatter import TypeModeRun, TypeModeRunInspect

@tagged('-at_install', 'post_install')
class test_in_stock_pi8_codegc_moves(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(test_in_stock_pi8_codegc_moves, cls).setUpClass()

    

@tagged('-at_install', 'post_install')
class test_in_stock_pi8_codegc_moves_controller(HttpCase):
    @hlog.hlog_test
    def test_indev(self):
        data = json.dumps([ "0A214584$1cQxKP404T", "0A214584$jiGsiDm446", "0A214584$S2bHzUPR4l"])
        zlog.ZLogger_Vars.MODE_RUN_INSPECT = TypeModeRunInspect.Inspect
        zlog.ZLogger_Vars.MODE_RUN = TypeModeRun.FullExpand
        zlog.ZLogger_Vars.INSPECT_FUNCTION =""
        zlog.ZLogger_Vars.INSPECT_FUNCTION_HIDE=[""]
        zlog.ZLogger_Vars.INSPECT_FUNCTION_RESALT = [ "" ]
        path = "/api/codegclot/ensure"
        response = self.url_open(path, data=data, headers=self.headers, timeout=60) 
    
    @hlog.hlog_test_api(resalt=False, auth_user='admin',auth_password='admin') 
    def test_api_indev(self):
        data = json.dumps([ "0A214584$1cQxKP404T", "0A214584$jiGsiDm446", "0A214584$S2bHzUPR4l"])
        zlog.ZLogger_Vars.MODE_RUN_INSPECT = TypeModeRunInspect.FullExpand
        zlog.ZLogger_Vars.MODE_RUN = TypeModeRun.FullExpand
        zlog.ZLogger_Vars.INSPECT_FUNCTION =""
        zlog.ZLogger_Vars.INSPECT_FUNCTION_HIDE=[""]
        zlog.ZLogger_Vars.INSPECT_FUNCTION_RESALT = [ "" ]
        path = "/api/codegclot/ensure"
        response = self.url_open(path, data=data, headers=self.headers, timeout=60) 

    # @hlog.hlog_test_api(resalt=False, auth_user='admin',auth_password='admin')  
    # def test_superapi_codegc_moves__from_text_codes(self):
    #     # Preparar datos de prueba
    #     codegc = '0A21459'

    #     zlog.ZLogger_Vars.MODE_RUN_INSPECT = TypeModeRunInspect.Inspect
    #     zlog.ZLogger_Vars.MODE_RUN = TypeModeRun.Normal
    #     zlog.ZLogger_Vars.INSPECT_FUNCTION ="SelectDistinct"
    #     zlog.ZLogger_Vars.INSPECT_FUNCTION_HIDE=[""]
    #     zlog.ZLogger_Vars.INSPECT_FUNCTION_RESALT=[""]
    #     path = "/api/codegclot/generate/simple"
    #     response = self.url_open(path, headers=self.headers, timeout=60) 

    @hlog.hlog_test_api(resalt=False, auth_user='admin',auth_password='admin')
    def test_api_codegclot_ensure(self):
        data = json.dumps([ "0A214584$1cQxKP404T", "0A214584$jiGsiDm446", "0A214584$S2bHzUPR4l"])
        zlog.ZLogger_Vars.MODE_RUN_INSPECT = TypeModeRunInspect.Inspect
        zlog.ZLogger_Vars.MODE_RUN = TypeModeRun.Normal
        zlog.ZLogger_Vars.INSPECT_FUNCTION ="SelectDistinct"
        zlog.ZLogger_Vars.INSPECT_FUNCTION_HIDE=[""]
        zlog.ZLogger_Vars.INSPECT_FUNCTION_RESALT = [ "" ]
        path = "/api/codegclot/ensure"
        response = self.url_open(path, data=data, headers=self.headers, timeout=60)        