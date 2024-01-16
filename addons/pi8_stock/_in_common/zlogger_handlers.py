import json
import traceback
from .zlogger_formatter import *
from .zlogger import ZLogger


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

def hlog_atomic(enable=False, traceback=False, basic=True, resalt = False, demo_return=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # ZLogger.disable_root_logger()
            _logger = ZLogger.get_logger()
            ZLogger_CustomFormatter.RUN_LEVEL += 1  
            run_level = ZLogger_CustomFormatter.RUN_LEVEL
            original_log_level = _logger.level  # Guardar el nivel de log original
            try:
                if not enable:
                    result = func(*args, **kwargs)
                else:
                    if basic:
                        result = func(*args, **kwargs)
                        _logger.info(f'{result} <=> {args[1:]} [{func.__name__}].[{func.__module__}]')
                    else:
                        _logger.test_ini(f'Atomic: ({func.__name__}) . {func.__module__}', resalt) 
                        if demo_return:
                            _logger.info(f"Demo Return: {demo_return}")
                            result = demo_return
                        else:
                            _logger.setLevel(1)  
                            result = func(*args, **kwargs)
                            _logger.setLevel(original_log_level)
                            ZLogger_CustomFormatter.RUN_LEVEL = run_level
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
