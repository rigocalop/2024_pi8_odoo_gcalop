import json
import traceback
from .zlogger_formatter import *
from .zlogger import ZLogger
import traceback as tb

class ApiException(Exception):
    """Exception raised when API are invalid."""
    def __init__(self, message="Invalid parameter"):
        self.message = message
        super().__init__(self.message)
        
class ZLoggerException(Exception):
    """ Excepción específica para ZLogger. """
    pass


def log_init(_logger, log_prefix, func, args, kwargs, log_level):
    log_title = f'{log_prefix}: ({func.__name__}) . {func.__module__}'
    ZLogger.log_common_init(_logger, log_level, log_title, *args, **kwargs)
    return log_title

def log_return(_logger, log_title, result, log_level):
    _logger.returns(log_title, to_return_function=result)
    ZLogger.log_common(_logger, log_level, log_title, 0)

def handle_error(_logger, e, log_prefix, func, original_log_level, run_level, default_error):
    error_message = f'{log_prefix}: ({func.__name__}). {func.__module__} **{default_error if default_error else "Error"}**: {str(e)}'
    error_message = f'Atomic ERROR: {error_message}'
    response_content = json.dumps({'error': str(e)})
    _logger.setLevel(original_log_level)
    _logger.error(error_message)
    ZLogger_Vars.RUN_LEVEL = run_level - 1
    raise ZLoggerException(response_content)

def execute_function(func, args, kwargs, _logger, original_log_level, demo_return):
    if demo_return:
        _logger.info(f"Demo Return: {demo_return}")
        return demo_return
    else:
        _logger.setLevel(1)
        result = func(*args, **kwargs)
        _logger.setLevel(original_log_level)
        return result

def log_api_init(_logger, func, api_params, api_headers):
    log_title = f'API ejecutada: {request.httprequest.path} => {func.__module__} . {func.__name__}'
    _logger.api_ini(log_title,
                    api_url=request.httprequest.url, 
                    api_header=api_headers, 
                    api_params=api_params, 
                    api_body=request.httprequest.data)
    return log_title

def log_api_end(_logger, func, response_content, to_return):
    _logger.returns(f'API ejecutada: {request.httprequest.path} => {func.__module__} . {func.__name__}', 
                    to_return_api=response_content, 
                    to_response_api=to_return)
    _logger.api_end(f'API ejecutada: {request.httprequest.path} => {func.__module__} . {func.__name__}')


def base_execute_and_log(func, args, kwargs, enable, compact, resalt, demo_return, log_prefix, const_LOG_INI, const_LOG_END, default_error=None, typeFunction=TypeFunction.Function, fcomment = None):
    _logger = ZLogger.get_logger()
    ZLogger_Vars.RUN_LEVEL += 1  
    run_level = ZLogger_Vars.RUN_LEVEL
    original_log_level = _logger.level
    was_inspect_mode = False  # Añadido para rastrear si se activó el modo de inspección
    was_inspect_hide_mode = False  # Añadido para rastrear si se activó el modo de inspección
    
    try:
        show_info_level = evaluate_showInfoLogger(typeFunction)
        
        if func.__name__ == ZLogger_Vars.INSPECT_FUNCTION:
            was_inspect_mode = True
            show_info_level=2
            enable = True
            compact = False
            activate_inspect_mode(func.__name__)
            _logger.warning(f'Activando modo de inspección para la función: {func.__name__}')
        
        
        # Verificar si la función debe ser ocultada según INSPECT_FUNCTION_HIDE
        if (ZLogger_Vars.FLAG_INSPECT == 1) and (func.__name__ in ZLogger_Vars.INSPECT_FUNCTION_HIDE):
            was_inspect_hide_mode = True
            ZLogger_Vars.FLAG_INSPECT_HIDE = True
            
                # Verificar si la función debe ser ocultada según INSPECT_FUNCTION_HIDE
        if (ZLogger_Vars.FLAG_INSPECT == 1) and (func.__name__ in ZLogger_Vars.INSPECT_FUNCTION_RESALT):
            resalt = True

            
        if ZLogger_Vars.FLAG_INSPECT_HIDE == True:
            show_info_level = 0
        
        
        # Evaluar si se debe ejecutar la función
        if show_info_level == 2:
            enable = True
            compact = False
        elif not enable or show_info_level == 0:
            return func(*args, **kwargs)
        elif compact and show_info_level == 1:
            # Ejecución y logging en modo compacto
            result = func(*args, **kwargs)
            _logger.info(f'{log_prefix}: {result} <=> {args[1:]}{kwargs} [{func.__name__}].[{func.__module__}]')
            return result

        # Ejecución y logging completo
        if (fcomment != None): _logger.log_common(LOG_LEVEL_DEBUG, fcomment)
        if (typeFunction == TypeFunction.Api): 
            log_title = log_api_init(_logger, func, request.httprequest.args, request.httprequest.headers)
        else: 
            log_title = log_init(_logger, log_prefix, func, args, kwargs, const_LOG_INI if not resalt else LOG_LEVEL_FINI_RESALT)
        
        
        result = execute_function(func, args, kwargs, _logger, original_log_level, demo_return)
        log_return(_logger, log_title, result, const_LOG_END if not resalt else LOG_LEVEL_FEND_RESALT)
        return result

    except ZLoggerException as zle:
        raise ZLoggerException("ZLoggerException capturada")
    except ApiException as apie:
        response_content = json.dumps({ "status": "ApiException", "message": apie.message })
        return Response(response_content, content_type='application/json', status=400)
    except Exception as e:
        log_title = log_init(_logger, log_prefix, func, args, kwargs, const_LOG_INI if not resalt else LOG_LEVEL_FINI_RESALT)
        handle_error(_logger, e, log_prefix, func, original_log_level, run_level, default_error)
    finally:
        ZLogger_Vars.RUN_LEVEL = run_level - 1
        if was_inspect_mode:
            # Desactivar el modo de inspección si fue activado para esta función
            activate_inspect_mode(None)
            _logger.warning(f'Desactivando modo de inspección para la función: {func.__name__}')
            
        if was_inspect_hide_mode:
            # Desactivar el modo de inspección si fue activado para esta función
            ZLogger_Vars.FLAG_INSPECT_HIDE = False
            was_inspect_hide_mode = False
                        
        _logger.setLevel(original_log_level)






def hlog_test(enable=True, compact=False, resalt=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return base_execute_and_log(func, args, kwargs, enable, compact, resalt, None, "Test: ", LOG_LEVEL_FINI_TEST, LOG_LEVEL_FEND_TEST)
        return wrapper
    return decorator

def hlog_test_api(auth_user=None, auth_password=None, enable=True, compact=False, resalt=False, default_error=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            if auth_user:
                self.authenticate(auth_user, auth_password)
            self.headers = {
                'Content-Type': 'application/json',
            }            
            return base_execute_and_log(func=func, args=args, kwargs=kwargs,enable=enable, compact=compact, resalt=resalt,log_prefix="Test API: ", const_LOG_INI=LOG_LEVEL_FINI_API, const_LOG_END=LOG_LEVEL_FEND_API, typeFunction=TypeFunction.Test, default_error=default_error, demo_return=None)
        return wrapper
    return decorator

def hlog_atomic(enable=False, compact=True, resalt=False, demo_return=None, default_error = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return base_execute_and_log(func=func, args=args, kwargs=kwargs, enable=enable, compact=compact, resalt=resalt, default_error=default_error,
                                        log_prefix="Atomic: ", const_LOG_INI=LOG_LEVEL_FINI, const_LOG_END=LOG_LEVEL_FEND, demo_return=demo_return)
        return wrapper
    return decorator

def hlog_function(enable=True, compact=False, resalt=False, demo_return=None, default_error = None, fcomment=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return base_execute_and_log(func, args, kwargs, enable, compact, resalt, demo_return, "Function: ", LOG_LEVEL_FINI, LOG_LEVEL_FEND, default_error)
        return wrapper
    return decorator

def hlog_superfunc(enable=True, compact=False, resalt=False, demo_return=None, default_error = None, fcomment=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return base_execute_and_log(func=func, args=args, kwargs=kwargs,enable=enable, compact=compact, resalt=resalt,log_prefix="SuperFunction: ", const_LOG_INI=LOG_LEVEL_FINI_SUPER, const_LOG_END=LOG_LEVEL_FEND_SUPER, typeFunction=TypeFunction.SuperFunction, default_error=default_error, demo_return=demo_return)
            #return base_execute_and_log(func, args, kwargs, enable, compact, resalt, demo_return, "SuperFunction: ", LOG_LEVEL_FINI_SUPER, LOG_LEVEL_FEND_SUPER, default_error)
        return wrapper
    return decorator



def hlog_api(enable=True, compact=False, resalt=False, demo_return=None, default_error = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            to_return = base_execute_and_log(func=func, args=args, kwargs=kwargs, enable=enable, compact=compact, resalt=resalt, log_prefix="API ejecutada: ", const_LOG_INI=LOG_LEVEL_FINI_API, const_LOG_END=LOG_LEVEL_FEND_API, typeFunction=TypeFunction.Api, default_error=default_error, demo_return=demo_return)
            
            # Si 'to_return' no es una instancia de Response, crea una nueva respuesta HTTP
            if not isinstance(to_return, Response):
                to_return = Response(json.dumps(to_return), content_type='application/json', status=200)

            return to_return
        return wrapper
    return decorator

