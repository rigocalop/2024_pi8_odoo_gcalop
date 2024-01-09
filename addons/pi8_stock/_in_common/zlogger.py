import logging
import colorama
from odoo.http import request, Response
from werkzeug.exceptions import BadRequest, NotFound
import json
# from .zlogger_formatter import ZLogger_CustomFormatter


colorama.init()
# Definir nuevos niveles de log
LOG_LEVEL_FARG = 9
LOG_LEVEL_FKWARG = 10
LOG_LEVEL_FINI = 15
LOG_LEVEL_FEND = 25
LOG_LEVEL_FINI_TEST = 14
LOG_LEVEL_RETURNS = 23
LOG_LEVEL_FEND_TEST = 24
LOG_LEVEL_VALUE = 35
LOG_LEVEL_INFO = logging.INFO
LOG_LEVEL_DEBUG = logging.DEBUG
LOG_LEVEL_WARNING = logging.WARNING
LOG_LEVEL_ERROR = logging.ERROR
LOG_LEVEL_CRITICAL = logging.CRITICAL
LOG_LEVEL_NOTSET = logging.NOTSET




INDENT_SIZE = 4
ASCTIME_LENGTH = 12
PROCESS_LENGTH = 5

ANSI_GREEN = "\033[32m"
ANSI_RED = "\033[31m"
ANSI_BLUE = "\033[34m"
ANSI_YELLOW = "\u001b[33m"
ANSI_CYAN = "\033[36m"
ANSI_MAGENTA = "\033[35m"
ANSI_BLACK = "\033[30m"
ANSI_WHITE = "\033[37m"
ANSI_RESET = "\033[0m"



ANSI_GREEN_BRIGHT = "\033[92m"
ANSI_RED_BRIGHT = "\033[91m"
ANSI_BLUE_BRIGHT = "\033[94m"
ANSI_YELLOW_BRIGHT = "\u001b[93m"
ANSI_CYAN_BRIGHT = "\033[96m"
ANSI_MAGENTA_BRIGHT = "\033[95m"
ANSI_BLACK_BRIGHT = "\033[90m"
ANSI_WHITE_BRIGHT = "\033[97m"
ANSI_RESET_BRIGHT = "\033[0m"

ANSI_BLACK_BACKGROUND = "\u001b[40m"
ANSI_RED_BACKGROUND = "\u001b[41m"
ANSI_YELLOW_BACKGROUND = "\u001b[43m"
ANSI_BLUE_BACKGROUND = "\u001b[44m"
ANSI_MAGENTA_BACKGROUND = "\u001b[45m"
ANSI_CYAN_BACKGROUND = "\u001b[46m"
ANSI_WHITE_BACKGROUND = "\u001b[47m"
ANSI_GREEN_BACKGROUND = "\u001b[42m"
ANSI_RESET_BACKGROUND = "\u001b[49m"



logging.addLevelName(LOG_LEVEL_FINI_TEST, 'FINI.TEST')
logging.addLevelName(LOG_LEVEL_FEND_TEST, 'FEND.TEST')
logging.addLevelName(LOG_LEVEL_FINI, 'FINI')
logging.addLevelName(LOG_LEVEL_FEND, 'FEND')
logging.addLevelName(LOG_LEVEL_VALUE, 'FVALUE')
logging.addLevelName(LOG_LEVEL_INFO, 'DEBUG')
logging.addLevelName(LOG_LEVEL_INFO, 'INFO')
logging.addLevelName(LOG_LEVEL_ERROR, 'WARINNG')
logging.addLevelName(LOG_LEVEL_ERROR, 'ERROR')
logging.addLevelName(LOG_LEVEL_ERROR, 'CRITICAL')

class ZLogger_CustomFormatter(logging.Formatter):
    # Códigos de escape ANSI para colores
    print("\u001b[45m\u001b[30mEste texto tiene fondo magenta y texto amarillo.\u001b[0m")
    print("\u001b[45m\u001b[33mEste texto tiene fondo magenta y texto amarillo.\u001b[0m")
    print("\u001b[45m\u001b[97mEste texto tiene fondo magenta y texto amarillo.\u001b[0m")
    print("\u001b[33mEste texto será amarillo.\u001b[0m")
    print("\u001b[44m\u001b[33mEste texto tiene fondo azul y texto amarillo.\u001b[0m")
    print("\u001b[41m\u001b[33mEste texto tiene fondo rojo y texto amarillo.\u001b[0m")

    @staticmethod
    def create_format(levelno):
#personalizacion
        run_level = ZLogger.RUN_LEVEL
        level_name = ""
        color_fore = ANSI_RESET
        color_back = ANSI_RESET_BACKGROUND
        is_empty_root = False
        is_partial_format = True
        is_argument = False
        
        prefix = "  "
        if levelno == LOG_LEVEL_FINI:
            level_name = "FINI"
            color_fore = ANSI_CYAN_BRIGHT
            color_back = ANSI_RESET_BACKGROUND
            is_partial_format = False
            prefix = "=>"
        elif levelno == LOG_LEVEL_FEND:
            level_name = "FEND"
            color_fore = ANSI_BLACK_BRIGHT
            color_back = ANSI_RESET_BACKGROUND
            prefix = "<="
            run_level+=1
        if levelno == LOG_LEVEL_FINI_TEST:
            level_name = "FINI.TEST"
            color_fore = ANSI_WHITE
            color_back = ANSI_MAGENTA_BACKGROUND
            is_partial_format = False
            prefix = "=>"
        elif levelno == LOG_LEVEL_FEND_TEST:
            level_name = "FEND.TEST"
            color_fore = ANSI_WHITE
            color_back = ANSI_MAGENTA_BACKGROUND
            prefix = "<="
        elif levelno == LOG_LEVEL_RETURNS:
            level_name = "FEND.RETURNS"
            color_fore = ANSI_BLACK
            color_back = ANSI_MAGENTA_BACKGROUND
            prefix = "=="
            run_level+=1
        elif levelno == LOG_LEVEL_FKWARG:
            color_fore = ANSI_RESET
            level_name = "FKWARG"
            is_empty_root = True
            is_argument = True
        elif levelno == LOG_LEVEL_FARG:
            color_fore = ANSI_RESET
            level_name = "FARG"
            is_empty_root = True
            is_argument = True
        elif levelno == LOG_LEVEL_ERROR:
            color_fore = ANSI_RED
            level_name = "ERROR"
            is_empty_root = False
        elif levelno == LOG_LEVEL_DEBUG:
            color_fore = ANSI_RED
            level_name = "ERROR"
            is_empty_root = False
        elif levelno == LOG_LEVEL_INFO:
            level_name = "INFO"
            is_empty_root = False
        elif levelno == LOG_LEVEL_WARNING:
            color_fore = ANSI_YELLOW_BRIGHT
            color_back = ANSI_RESET_BACKGROUND
            level_name = "WARNING"
            is_empty_root = True


#procesaimento        
        color_format = f"{color_back}{color_fore}"
        if is_empty_root:
            base_format = f"{'.' * (ASCTIME_LENGTH + 12)}"
        else:
            # Formato normal incluyendo asctime y process
            base_format = f"{{:<{ASCTIME_LENGTH}}}".format("%(asctime)s")

        # formatear nivel y run_level
        formatted_level_name = "*{:9}".format(level_name[:9])
        formatted_run_level = "{:02d}".format(run_level)
        formatted_indent = ' ' * (INDENT_SIZE * (run_level - 1))
        
        # construccion de la linea
        base_format += f" {formatted_level_name} [{formatted_run_level}]"
        if is_partial_format: base_format += f"{color_format}{formatted_indent}{prefix} %(message)s{ANSI_RESET}"
        else: base_format = f"{color_format}{base_format}{formatted_indent}{prefix} %(message)s{ANSI_RESET}"
        return base_format

    def format(self, record):
        original_format = self._style._fmt
        self._style._fmt = self.create_format(record.levelno)
        result = super().format(record)
        self._style._fmt = original_format  # Reset to original to maintain thread safety
        return result
    
    
    
    
class ZLogger(logging.Logger):
    RUN_LEVEL = 0

    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
#region "procedimientos comunes"
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

    def _log_common__fkwargs(self, **kwargs):
        # Procesar cada argumento de palabras clave y llamar a fvalue
        for index, value in kwargs.items():
            formatted_msg = f"{ANSI_RESET_BACKGROUND}{ANSI_GREEN_BRIGHT}{index}:{ANSI_RESET} {ANSI_RESET_BACKGROUND}{ANSI_RESET}{value}{ANSI_RESET}"
            self._log(LOG_LEVEL_FKWARG, formatted_msg, (), {})
    
    def _log_common__args(self, *args):
        if not args:
            return
        if len(args) == 1 and not args[0]:
            return
        
        index = -1
        count = len(args)
        for value in args:
            index += 1
            formatted_msg = f"{ANSI_RESET_BACKGROUND}{ANSI_GREEN_BRIGHT}{index}:{ANSI_RESET} {ANSI_RESET_BACKGROUND}{ANSI_BLACK}{value}{ANSI_RESET}"
            self._log(LOG_LEVEL_FARG, formatted_msg, (), {})
            
    
    def log_common__args(self, *args, back_color_name, fore_color_name, back_color_value, fore_color_value):
        if not args:
            return
        if len(args) == 1 and not args[0]:
            return
        
        index = -1
        count = len(args)
        for value in args:
            index += 1
            formatted_msg = f"{back_color_name}{fore_color_name}{index}:{ANSI_RESET} {back_color_value}{fore_color_value}{value}{ANSI_RESET}"
            self._log(LOG_LEVEL_FARG, formatted_msg, (), {})
                    
    
    # def log_common__args_API_PARAMS(self, *args):
    #     self.log_common__args(*args, ANSI_GREEN_BRIGHT, ANSI_RESET, ANSI_RESET_BACKGROUND, ANSI_BLACK) 
    
    def log_common(self, level, msg, modify_run_level, *args, **kwargs):
        ZLogger.disable_root_logger()   # Desactivar el logger raíz
        ZLogger.RUN_LEVEL += modify_run_level  # Modificar RUN_LEVEL_TEST según sea necesario
        if self.isEnabledFor(level): # Log si el nivel es habilitado
            self._log(level, msg, (),{})
        
        self._log_common__args(*args)
        self._log_common__fkwargs(**kwargs)
        ZLogger.enable_root_logger()         # Reactivar el logger raíz
    
    
    #endregion
    def fini(self, msg, *args, **kwargs):
        to_return = ZLogger.RUN_LEVEL
        self.log_common(LOG_LEVEL_FINI, msg, 1, args, **kwargs)
        return to_return
        

    def fend(self, msg, *args, **kwargs):
        if 'run_level' in kwargs: ZLogger.RUN_LEVEL = kwargs['run_level']
        self.log_common(LOG_LEVEL_FEND, msg, -1, *args, **kwargs)
    
    def tini(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_FINI_TEST, msg, 1, args, **kwargs)
        if 'run_level' in kwargs: ZLogger.RUN_LEVEL = kwargs['run_level']
        

    def tend(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_FEND_TEST, msg, -1, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_INFO, msg, 0, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_WARNING, msg, 0, *args, **kwargs)
        
    def error(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_ERROR, msg, 0, *args, **kwargs)
        if 'run_level' in kwargs: ZLogger.RUN_LEVEL = kwargs['run_level']

    def debug(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_DEBUG, msg, 0, *args, **kwargs)                
    def returns(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_RETURNS, msg, 0, *args, **kwargs)                
        
    def fvalue(self, msg, *args, **kwargs):
        if self.isEnabledFor(LOG_LEVEL_VALUE):
            self._log(LOG_LEVEL_VALUE, msg, args, **kwargs)

def api_response_handler(func):
    def wrapper(*args, **kwargs):
        run_level = ZLogger.RUN_LEVEL
        to_return = None
        try:
            _logger = ZLogger.get_logger()
            api_params = {key: request.httprequest.args.getlist(key) for key in request.httprequest.args}
            _logger.tini(f'API ejecutada: {request.httprequest.path} => {func.__module__}{func.__name__}', **api_params, api_data = request.httprequest.data)
            result = func(*args, **kwargs)
            response_content = None
            status = 200
            if isinstance(result, BadRequest):
                response_content = result.description
                status = 400
            else: 
                response_content = json.dumps(result)
            
            to_return = request.make_response(response_content, headers=[('Content-Type', 'application/json')], status=status)                
            _logger.returns(f'API ejecutada: {request.httprequest.path} => {func.__module__}{func.__name__}', response_content=response_content, response=to_return)
            _logger.tend(f'API ejecutada: {request.httprequest.path} => {func.__module__}{func.__name__}')
            ZLogger.RUN_LEVEL = run_level    
            return to_return
        except Exception as e:
            ZLogger.error(f'Error durante la ejecución de la API: {str(e)}')
            response_content = json.dumps({'error': str(e)})
            ZLogger.RUN_LEVEL = run_level    
            return request.make_response(response_content, headers=[('Content-Type', 'application/json')], status=500)
    return wrapper
