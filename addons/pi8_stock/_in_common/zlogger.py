import logging
from odoo.http import request, Response
from werkzeug.exceptions import BadRequest, NotFound
import json
import traceback
import functools
from .zlogger_formatter import *

    
class ZLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    zlog = None
    @staticmethod
    def get_logger():
        logger = logging.getLogger("testLogger")
        return logger
    
    @staticmethod
    def configure_logger():
        logging.setLoggerClass(ZLogger)

        logger = logging.getLogger("testLogger")
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers[:]:  # Hacer una copia de la lista para iterar
            logger.removeHandler(handler)

        # Establecer el formatter personalizado y agregar el nuevo handler
        ch = logging.StreamHandler()
        ch.setFormatter(ZLogger_CustomFormatter())
        logger.addHandler(ch)
        
    @staticmethod
    def disable_root_logger():
        root_logger = logging.getLogger()
        ZLogger._original_root_level = root_logger.level  # Guardar el nivel original del logger
        root_logger.setLevel(logging.CRITICAL + 1)  # Desactivar el logger raíz

        # Desactivar también todos los handlers del logger raíz
        for handler in root_logger.handlers:
            handler.setLevel(logging.CRITICAL + 1)


    @staticmethod
    def enable_root_logger():
        root_logger = logging.getLogger()
        root_logger.setLevel(ZLogger._original_root_level)  # Restaurar el nivel original del logger

        # Restaurar el nivel de cada handler al nivel del logger
        for handler in root_logger.handlers:
            handler.setLevel(ZLogger._original_root_level)
    
    def log_common(self, level, msg, modify_run_level = 0, *args, **kwargs):
        ZLogger.disable_root_logger()   # Desactivar el logger raíz
        ZLogger_CustomFormatter.RUN_LEVEL += modify_run_level  # Modificar RUN_LEVEL_TEST según sea necesario
        if self.isEnabledFor(level): # Log si el nivel es habilitado
            self._log(level, msg, (),{})
        
        if (args != None): ZLogger_CustomFormatter.log_common__args(self, *args)
        if (kwargs != None): ZLogger_CustomFormatter.log_common__fkwargs(self, **kwargs)
        ZLogger.enable_root_logger()   # Desactivar el logger raíz
        
#region "Metodos de log"
    def func_ini(self, msg, resalt=False, *args, **kwargs):
        if (resalt): self.log_common(LOG_LEVEL_FINI_RESALT, msg, 0, *args, **kwargs)
        else: self.log_common(LOG_LEVEL_FINI, msg, 0, *args, **kwargs)
    def func_end(self, msg, resalt=False, *args, **kwargs):
        if (resalt): self.log_common(LOG_LEVEL_FEND_RESALT, msg, 0, *args, **kwargs)
        else: self.log_common(LOG_LEVEL_FEND, msg, 0, *args, **kwargs)
    def superfunc_ini(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_FINI_SUPER, msg, 0, *args, **kwargs)
    def superfunc_end(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_FEND_SUPER, msg, 0, *args, **kwargs)        
    def test_ini(self, msg, resalt=False):
        if (resalt): self.log_common(LOG_LEVEL_FINI_RESALT, msg)
        else: self.log_common(LOG_LEVEL_FINI_TEST, msg, 0)        
    def test_end(self, msg, resalt=False):
        if (resalt): self.log_common(LOG_LEVEL_FEND_RESALT, msg)
        else: self.log_common(LOG_LEVEL_FEND_TEST, msg, 0)        
    def api_ini(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_FINI_API, msg, 0, args, **kwargs)
    def api_end(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_FEND_API, msg, 0, *args, **kwargs)
    def info(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_INFO, msg, 0, *args, **kwargs)
    def warning(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_WARNING, msg, 0, *args, **kwargs)
    def error(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_ERROR, msg, 0, *args, **kwargs)
    def debug(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_DEBUG, msg, 0, *args, **kwargs)                
    def returns(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_RETURNS, msg, 0, *args, **kwargs)                
    def fvalue(self, msg, *args, **kwargs):
        if self.isEnabledFor(LOG_LEVEL_VALUE):
            self._log(LOG_LEVEL_VALUE, msg, args, **kwargs)
    def mark(self, msg, *args, **kwargs):
        if self.level == 1:
            self._log(LOG_LEVEL_MARK, msg, args, **kwargs)            
#endregion

def api_handler(func):
    def wrapper(*args, **kwargs):
        ZLogger_CustomFormatter.RUN_LEVEL += 1  
        run_level = ZLogger_CustomFormatter.RUN_LEVEL
        to_return = None
        try:
            _logger = ZLogger.get_logger()
            api_params = {key: request.httprequest.args.getlist(key) for key in request.httprequest.args}
            api_headers = {key: value for key, value in request.httprequest.headers.items()}

            # api_headers = {key: request.httprequest.headers.getlist(key) for key in request.httprequest.headers}
            _logger.api_ini(f'API ejecutada: {request.httprequest.path} => {func.__module__} . {func.__name__}', api_url=request.httprequest.url, api_header=api_headers, api_params=api_params, api_body = request.httprequest.data)
            result = func(*args, **kwargs)
            response_content = None
            status = 200
            if isinstance(result, BadRequest):
                response_content = result.description
                status = 400
            else: 
                response_content = json.dumps(result)
            
            to_return = request.make_response(response_content, headers=[('Content-Type', 'application/json')], status=status)                
            ZLogger_CustomFormatter.RUN_LEVEL = run_level
            _logger.returns(f'API ejecutada: {request.httprequest.path} => {func.__module__} . {func.__name__}', to_return_api=response_content, to_response_api=to_return)
            _logger.api_end(f'API ejecutada: {request.httprequest.path} => {func.__module__} . {func.__name__}')
            ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
            return to_return
        except Exception as e:
            _logger.error(f'Error durante la ejecución de la API: {str(e)}')
            response_content = json.dumps({'error': str(e)})
            ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
            return request.make_response(response_content, headers=[('Content-Type', 'application/json')], status=500)
    return wrapper

def hlog_function(func):
    def wrapper(*args, **kwargs):
        ZLogger_CustomFormatter.RUN_LEVEL += 1  
        run_level = ZLogger_CustomFormatter.RUN_LEVEL
        try:
                _logger = ZLogger.get_logger()
                _logger.func_ini(f'Function: ({func.__name__}). {func.__module__}', False, *args, **kwargs)
                result = func(*args, **kwargs)
                ZLogger_CustomFormatter.RUN_LEVEL = run_level
                _logger.returns(f'Function: {func.__module__} . {func.__name__}', to_return_function=result)
                _logger.func_end(f'Function: ({func.__name__}). {func.__module__}')
                ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
                return result
        except Exception as e:
            ZLogger_CustomFormatter.RUN_LEVEL = run_level
            error_message = f'Function ERROR: ({func.__name__}). {func.__module__} Error durante la ejecución de la función: {str(e)}'
            show_traceback=False
            if show_traceback:
                error_traceback = traceback.format_exc()
                error_message += f"\n{error_traceback}"
                response_content = json.dumps({'error': str(e), 'traceback': error_traceback})
            else:
                response_content = json.dumps({'error': str(e)})
                _logger.error(error_message)
                ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
            raise Exception(response_content)
    return wrapper

def hlog_superfunc(func):
    def wrapper(*args, **kwargs):
        ZLogger_CustomFormatter.RUN_LEVEL += 1  
        run_level = ZLogger_CustomFormatter.RUN_LEVEL
        to_return = None
        try:
            _logger = ZLogger.get_logger()
            _logger.superfunc_ini(f'SuperFunction: ({func.__name__}). {func.__module__}', *args, **kwargs)
            result = func(*args, **kwargs)
            ZLogger_CustomFormatter.RUN_LEVEL = run_level
            _logger.returns(f'Function: {func.__module__} . {func.__name__}', to_return_function=result)
            _logger.superfunc_end(f'SuperFunction: ({func.__name__}). {func.__module__}')
            ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
            return result
        except Exception as e:
            ZLogger_CustomFormatter.RUN_LEVEL = run_level
            _logger.error(f'Error durante la ejecución de la API: {str(e)}')
            response_content = json.dumps({'error': str(e)})
            ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
            raise Exception(response_content)
    return wrapper

def hlog_test(func):
    def wrapper(*args, **kwargs):
        ZLogger_CustomFormatter.RUN_LEVEL += 1  
        run_level = ZLogger_CustomFormatter.RUN_LEVEL
        to_return = None
        try:
            _logger = ZLogger.get_logger()
            _logger.test_ini(f'TEST ejecutada: ({func.__name__}) . {func.__module__}')
            result = func(*args, **kwargs)
            
            ZLogger_CustomFormatter.RUN_LEVEL = run_level
            _logger.returns(f'TEST ejecutada: {func.__module__} . {func.__name__}', to_return_test=result)
            _logger.test_end(f'TEST ejecutada: ({func.__name__}) . {func.__module__}')
            ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
            return result
        except Exception as e:
            ZLogger_CustomFormatter.RUN_LEVEL = run_level
            _logger.error(f'Error durante la ejecución de la API: {str(e)}')
            response_content = json.dumps({'error': str(e)})
            ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
            raise Exception(response_content)
    return wrapper

def hlog_atomic(enable=False, traceback=False, resalt = False, demo_return=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # ZLogger.disable_root_logger()
            _logger = ZLogger.get_logger()
            ZLogger_CustomFormatter.RUN_LEVEL += 1  
            run_level = ZLogger_CustomFormatter.RUN_LEVEL
            original_log_level = _logger.level  # Guardar el nivel de log original
            try:
                # # if enable:
                # #     _logger.setLevel(0)  # Desactivar el logger raíz
                # #     _logger.func_ini(f'Atomic: ({func.__name__}). {func.__module__}', resalt, *args, **kwargs)
                
                # # if enable and demo_return:
                # #     _logger.info(f"Demo Return: {demo_return}")
                # #     result = demo_return
                # # else:
                # #     result = func(*args, **kwargs)
                    
                # _logger.func_ini(f'Atomic: ({func.__name__}). {func.__module__}', resalt, *args, **kwargs)
                # result = func(*args, **kwargs)
                # _logger.returns(f'Atomic: {func.__module__} . {func.__name__}', to_return_function=result)
                # _logger.func_end(f'Atomic: ({func.__name__}). {func.__module__}', resalt)

                # # ZLogger_CustomFormatter.RUN_LEVEL = run_level
                # # if enable:
                # #     _logger.setLevel(original_log_level)  # Desactivar el logger raíz
                # #     _logger.returns(f'Atomic: {func.__module__} . {func.__name__}', to_return_function=result)
                # #     _logger.func_end(f'Atomic: ({func.__name__}). {func.__module__}', resalt)
                # ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
                # return result
            
                if enable:
                    
                    _logger.test_ini(f'Atomic: ({func.__name__}) . {func.__module__}', resalt)
                if enable and demo_return:
                    _logger.info(f"Demo Return: {demo_return}")
                    result = demo_return
                else:
                    if enable: _logger.setLevel(1)  
                    result = func(*args, **kwargs)
                    if enable: _logger.setLevel(original_log_level) 
                ZLogger_CustomFormatter.RUN_LEVEL = run_level
                if enable:
                    _logger.returns(f'Atomic: {func.__module__} . {func.__name__}', to_return_function=result)
                    _logger.test_end(f'Atomic: ({func.__name__}) . {func.__module__}', resalt)
                ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
                return result
            except Exception as e:
                ZLogger_CustomFormatter.RUN_LEVEL = run_level
                error_message = f'Atomic ERROR: ({func.__name__}). {func.__module__} Error durante la ejecución de la función: {str(e)}'
                if traceback:
                    error_traceback = traceback.format_exc()
                    error_message += f"\n{error_traceback}"
                    response_content = json.dumps({'error': str(e), 'traceback': error_traceback})
                else:
                    response_content = json.dumps({'error': str(e)})
                    if enable:
                        _logger.setLevel(original_log_level)  # Desactivar el logger raíz
                        _logger.error(error_message)
                    ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
                raise Exception(response_content)
        return wrapper
    return decorator

        
def hlog_test_api(auth_user=None, auth_password=None, resalt = False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            if auth_user:
                self.authenticate(auth_user, auth_password)
            self.headers = {
                'Content-Type': 'application/json',
            }
            
            ZLogger_CustomFormatter.RUN_LEVEL += 1  
            run_level = ZLogger_CustomFormatter.RUN_LEVEL
            to_return = None
            try:
                _logger = ZLogger.get_logger()
                _logger.test_ini(f'TEST.API ejecutada: ({func.__name__}) . {func.__module__}', resalt)
                result = func(*args, **kwargs)
                
                ZLogger_CustomFormatter.RUN_LEVEL = run_level
                _logger.test_end(f'TEST.API ejecutada: ({func.__name__}) . {func.__module__}', resalt)
                ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
                return result
            except Exception as e:
                ZLogger_CustomFormatter.RUN_LEVEL = run_level
                _logger.error(f'Error durante la ejecución de la API: {str(e)}')
                response_content = json.dumps({'error': str(e)})
                ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
                raise Exception(response_content)
        return wrapper
    return decorator
