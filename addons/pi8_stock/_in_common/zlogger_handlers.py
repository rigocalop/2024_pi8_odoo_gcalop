import json
import traceback
from .zlogger_formatter import *
from .zlogger import ZLogger
import traceback as tb
#region "LOG LEVELS TIPO A"
def base_execute_and_log(func, args, kwargs, enable, compact, resalt, demo_return, log_prefix, const_LOG_INI, const_LOG_END):
    _logger = ZLogger.get_logger()
    ZLogger_CustomFormatter.RUN_LEVEL += 1  
    run_level = ZLogger_CustomFormatter.RUN_LEVEL
    original_log_level = _logger.level
    log_title = f'{log_prefix}: ({func.__name__}) . {func.__module__}'
    try:
        if not enable:
            result = func(*args, **kwargs)
        else:
            if compact:
                result = func(*args, **kwargs)
                _logger.info(f'{log_prefix}: {result} <=> {args[1:]} [{func.__name__}].[{func.__module__}]')
            else:
                if (resalt): ZLogger.log_common(_logger, LOG_LEVEL_FINI_RESALT, log_title, 0, *args, **kwargs)
                else: ZLogger.log_common(_logger, const_LOG_INI, log_title, 0, *args, **kwargs)

                if demo_return:
                    _logger.info(f"{log_prefix}: Demo Return: {demo_return}")
                    result = demo_return
                else:
                    _logger.setLevel(1)
                    result = func(*args, **kwargs)
                    _logger.setLevel(original_log_level)
                    _logger.returns(log_title, to_return_function=result)
                    if (resalt): ZLogger.log_common(_logger, LOG_LEVEL_FEND_RESALT, log_title, 0)
                    else: ZLogger.log_common(_logger, const_LOG_END, log_title, 0, *args, **kwargs)
        return result
    except Exception as e:
        error_message = f'Atomic ERROR: ({func.__name__}). {func.__module__} Error durante la ejecución de la función: {str(e)}'
        # if traceback:
        #     error_traceback = tb.format_exc()
        #     error_message += f"\n{error_traceback}"
        #     response_content = json.dumps({'error': str(e), 'traceback': error_traceback})
        # else:
        response_content = json.dumps({'error': str(e)})
        if enable:
            _logger.setLevel(original_log_level)
            _logger.error(error_message)
        ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
        raise Exception(response_content)
    finally:
        ZLogger_CustomFormatter.RUN_LEVEL = run_level - 1
        if enable:
            _logger.setLevel(original_log_level)

def hlog_test(enable=True, compact=False, resalt=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return base_execute_and_log(func, args, kwargs, enable, compact, resalt, None, "Test: ", LOG_LEVEL_FINI_TEST, LOG_LEVEL_FEND_TEST)
        return wrapper
    return decorator


def hlog_test_api(auth_user=None, auth_password=None, enable=True, compact=False, resalt=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            if auth_user:
                self.authenticate(auth_user, auth_password)
            self.headers = {
                'Content-Type': 'application/json',
            }            
            return base_execute_and_log(func, args, kwargs, enable, compact, resalt, None, "Test API: ", LOG_LEVEL_FINI_API, LOG_LEVEL_FEND_API)
        return wrapper
    return decorator


def hlog_atomic(enable=False, traceback=False, compact=True, resalt=False, demo_return=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return base_execute_and_log(func, args, kwargs, enable, compact, resalt, demo_return, "Atomic: ", LOG_LEVEL_FINI, LOG_LEVEL_FEND)
        return wrapper
    return decorator

def hlog_function(enable=True, traceback=False, compact=False, resalt=False, demo_return=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return base_execute_and_log(func, args, kwargs, enable, compact, resalt, demo_return, "Function: ", LOG_LEVEL_FINI, LOG_LEVEL_FEND)
        return wrapper
    return decorator

def hlog_superfunc(enable=True, traceback=False, compact=False, resalt=False, demo_return=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return base_execute_and_log(func, args, kwargs, enable, compact, resalt, demo_return, "SuperFunction: ", LOG_LEVEL_FINI_SUPER, LOG_LEVEL_FEND_SUPER)
        return wrapper
    return decorator

#endregion

#
def hlog_api(func):
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
                response_content = json.dumps(result.description)
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

