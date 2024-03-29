import logging
from odoo.http import request, Response
from werkzeug.exceptions import BadRequest, NotFound
import json
import inspect

# Definir nuevos niveles de log
LOG_LEVEL_MARK = 1
LOG_LEVEL_FINI = 11
LOG_LEVEL_FEND = 12
LOG_LEVEL_FARG = 13
LOG_LEVEL_FKWARG = 14
LOG_LEVEL_RETURNS = 15
LOG_LEVEL_VALUE = 16
LOG_LEVEL_FINI_SUPER = 21
LOG_LEVEL_FEND_SUPER = 122
LOG_LEVEL_FINI_API = 23
LOG_LEVEL_FEND_API = 24
LOG_LEVEL_FINI_TEST = 25
LOG_LEVEL_FEND_TEST = 26
LOG_LEVEL_FINI_RESALT = 31
LOG_LEVEL_FEND_RESALT = 32





LOG_LEVEL_INFO = logging.INFO
LOG_LEVEL_DEBUG = logging.DEBUG
LOG_LEVEL_WARNING = logging.WARNING
LOG_LEVEL_ERROR = logging.ERROR
LOG_LEVEL_CRITICAL = logging.CRITICAL
LOG_LEVEL_NOTSET = logging.NOTSET

FORMAT_INDENT_SIZE = 4
FORMAT_ASCTIME_LENGTH = 12
FORMAT_PROCESS_LENGTH = 5

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

logging.addLevelName(LOG_LEVEL_MARK, 'FINI.TEST')
logging.addLevelName(LOG_LEVEL_FINI_TEST, 'FINI.TEST')
logging.addLevelName(LOG_LEVEL_FEND_TEST, 'FEND.TEST')
logging.addLevelName(LOG_LEVEL_FINI_API, 'FINI.API')
logging.addLevelName(LOG_LEVEL_FEND_API, 'FEND.API')
logging.addLevelName(LOG_LEVEL_FINI, 'FINI')
logging.addLevelName(LOG_LEVEL_FEND, 'FEND')
logging.addLevelName(LOG_LEVEL_FINI_RESALT, 'FINI.RESALT')
logging.addLevelName(LOG_LEVEL_FEND_RESALT, 'FEND.RESALT')
logging.addLevelName(LOG_LEVEL_VALUE, 'FVALUE')
logging.addLevelName(LOG_LEVEL_INFO, 'DEBUG')
logging.addLevelName(LOG_LEVEL_INFO, 'INFO')
logging.addLevelName(LOG_LEVEL_ERROR, 'WARINNG')
logging.addLevelName(LOG_LEVEL_ERROR, 'ERROR')
logging.addLevelName(LOG_LEVEL_MARK, 'MARK')

class TypeModeRun:
    Normal = "Normal"   # Modo normal
    FullExpand = "FullExpand" # Modo de expansión completa
    Inspect = "Inspect" # Modo de inspección de una especifica funcion para ver su comportamiento

class TypeModeRunInspect:
    Normal = "Normal"   # Modo Normal
    Direct = "Direct"   # Mode Directo
    
    
    FullExpand = "FullExpand" # Modo de expansión completa
    Inspect = "Inspect" # Modo de inspección de una especifica funcion para ver su comportamiento


class TypeFunction:
    Test = 0        # Función de prueba
    Api = 1     # Función de API
    SuperFunction = 2   # Función de super funcion importante y principal
    Function = 3        # Es una funcion esencial, per menos importante que la superfuncion
    Atomic = 4      # Es una funcion atómica, es decir, que no se puede dividir en funciones más pequeñas. O funcones de usu general.
    


class ModeShowLogger:
    Hide = 0        # Ocultar el logger
    Compact = 1     # Mostrar el logger de forma compacta
    ShowAll = 2     # Mostrar el logger completo

class ZLogger_Vars:
    RUN_LEVEL = 0           # Nivel de ejecución
    RUN_COUNTER = 0         # Contador de ejecuciones
    FLAG_COMPACT = 0   #FLAG DE OCULTAR NIVELES INFERIORES MIENTRAS SE EJECUTE.
    FLAG_INSPECT = 0    #EVALUA QUE SI SE ESTA EJECUTANDO UN PROCESO DE INSPECT
    FLAG_INSPECT_HIDE = False    #EVALUA QUE SI SE ESTA EJECUTANDO UN PROCESO DE INSPECT
    
    MAX_LEVEL = 3 # Nivel máximo de ejecución para mostrar el logger
    MODE_RUN = TypeModeRun.Normal    # Modo de ejecución del logger
    MODE_RUN_INSPECT = TypeModeRunInspect.Direct    # Modo de ejecución del logger
    INSPECT_FUNCTION = "CreateProducts_FromCodeValues"
    INSPECT_FUNCTION_HIDE = ["expandEntryTextCode"]
    INSPECT_FUNCTION_RESALT = ["expandEntryTextCode"]
    INSPECT_FULLEXPAND = ["expandEntryTextCode"]


def evaluate_normal_mode(typeFunction):
    if typeFunction == TypeFunction.Atomic:
        return 0
    elif typeFunction == TypeFunction.Function:
        return 2 if ZLogger_Vars.MAX_LEVEL >= ZLogger_Vars.RUN_LEVEL else 0
    else:
        return 2

def activate_inspect_mode(func_name):
    if func_name == ZLogger_Vars.INSPECT_FUNCTION:
        ZLogger_Vars.FLAG_INSPECT = 1
    else:
        ZLogger_Vars.FLAG_INSPECT = 0
    
def evaluate_showInfoLogger(typeFunction):
    if ZLogger_Vars.MODE_RUN == TypeModeRun.Normal:
        return evaluate_normal_mode(typeFunction)
    elif ZLogger_Vars.MODE_RUN == TypeModeRun.FullExpand:
        return 2
    elif ZLogger_Vars.MODE_RUN == TypeModeRun.Inspect:
        if ZLogger_Vars.FLAG_INSPECT == 1:
            return 2 # CONFIGURAR EJECUCION
        else:
            if (ZLogger_Vars.MODE_RUN_INSPECT==TypeModeRunInspect.Direct):
                return 0
            else: 
                return evaluate_normal_mode(typeFunction)

# def evaluate_showInfoLogger(typeFunction):
#     if ZLogger.ModeRun == TypeModeRun.Normal:
#         if (typeFunction == TypeFunction.Atomic):
#             return 0
#         else:
#             return 1
#     elif ZLogger.ModeRun == TypeModeRun.FullExpand:
#         if (typeFunction == TypeFunction.Function):
#             return 1
#         else:
#             return 0   
    
    

class ZLogger_CustomFormatter(logging.Formatter):
    @staticmethod
    def create_format(levelno):
        run_level = ZLogger_Vars.RUN_LEVEL
        level_name = ""
        color_fore = ANSI_RESET
        color_back = ANSI_RESET_BACKGROUND
        is_empty_root = False
        is_partial_format = True
        prefix = "  "
        if levelno == LOG_LEVEL_FINI:
            level_name = "FINI"
            color_fore = ANSI_CYAN_BRIGHT
            color_back = ANSI_RESET_BACKGROUND
            is_partial_format = False
            prefix = "=>"
        elif levelno == LOG_LEVEL_FEND:
            level_name = "FEND"
            color_fore = ANSI_CYAN_BRIGHT
            color_back = ANSI_RESET_BACKGROUND
            prefix = "<="
            
        if levelno == LOG_LEVEL_FINI_RESALT:
            level_name = "FINI.RESALT"
            color_fore = ANSI_BLACK
            color_back = ANSI_YELLOW_BACKGROUND
            is_partial_format = False
            prefix = "=>"
        elif levelno == LOG_LEVEL_FEND_RESALT:
            level_name = "FEND.RESALT"
            color_fore = ANSI_BLACK
            color_back = ANSI_YELLOW_BACKGROUND
            prefix = "<="
            
        if levelno == LOG_LEVEL_FINI_SUPER:
            level_name = "FINI.SUPER"
            color_fore = ANSI_WHITE_BRIGHT
            color_back = ANSI_BLUE_BACKGROUND
            is_partial_format = False
            prefix = "=>"
        elif levelno == LOG_LEVEL_FEND_SUPER:
            level_name = "FEND.SUPER"
            color_fore = ANSI_WHITE_BRIGHT
            color_back = ANSI_BLUE_BACKGROUND
            prefix = "<="            
        if levelno == LOG_LEVEL_FINI_TEST:
            level_name = "FINI.TEST"
            color_fore = ANSI_WHITE_BRIGHT
            color_back = ANSI_GREEN_BACKGROUND
            is_partial_format = False
            prefix = "=>"
        elif levelno == LOG_LEVEL_FEND_TEST:
            level_name = "FEND.TEST"
            color_fore = ANSI_WHITE_BRIGHT
            color_back = ANSI_GREEN_BACKGROUND
            prefix = "<="
        if levelno == LOG_LEVEL_FINI_API:
            level_name = "FINI.API"
            color_fore = ANSI_WHITE
            color_back = ANSI_MAGENTA_BACKGROUND
            is_partial_format = False
            prefix = "=>"
        elif levelno == LOG_LEVEL_FEND_API:
            level_name = "FEND.API"
            color_fore = ANSI_WHITE
            color_back = ANSI_MAGENTA_BACKGROUND
            prefix = "<="
        elif levelno == LOG_LEVEL_RETURNS:
            level_name = "FEND.RETURNS"
            color_fore = ANSI_BLACK
            color_back = ANSI_RESET_BACKGROUND
            prefix = "=="
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
            color_fore = ANSI_BLACK
            color_back = ANSI_WHITE_BACKGROUND
            level_name = "DEGUB"
            is_empty_root = False
        elif levelno == LOG_LEVEL_INFO:
            level_name = "INFO"
            is_empty_root = False
        elif levelno == LOG_LEVEL_WARNING:
            color_fore = ANSI_YELLOW_BRIGHT
            color_back = ANSI_RESET_BACKGROUND
            level_name = "WARNING"
            is_empty_root = True
        elif levelno == LOG_LEVEL_MARK:
            color_fore = ANSI_YELLOW_BRIGHT
            color_back = ANSI_RESET_BACKGROUND
            level_name = "WARNING"
            is_empty_root = True

        color_format = f"{color_back}{color_fore}"
        if is_empty_root:
            base_format = f"{'.' * (FORMAT_ASCTIME_LENGTH + 12)}"
        else:
            base_format = f"{{:<{FORMAT_ASCTIME_LENGTH}}}".format("%(asctime)s")

        # formatear nivel y run_level
        formatted_level_name = "*{:9}".format(level_name[:9])
        formatted_run_level = "{:02d}".format(run_level)
        formatted_run_counter = "{:04d}".format(ZLogger_Vars.RUN_COUNTER)
        formatted_indent = '+   ' * (run_level)
        
        # construccion de la linea
        logger = logging.getLogger("testLogger")
        base_format += f" {formatted_level_name} [{formatted_run_level}.{formatted_run_counter}.{logger.level}]"
        if is_partial_format: base_format += f"{color_format}{formatted_indent}{prefix} %(message)s{ANSI_RESET}"
        else: base_format = f"{color_format}{base_format}{formatted_indent}{prefix} %(message)s{ANSI_RESET}"
        return base_format

    def format(self, record):
        original_format = self._style._fmt
        self._style._fmt = self.create_format(record.levelno)
        result = super().format(record)
        self._style._fmt = original_format  # Reset to original to maintain thread safety
        return result
    
    @staticmethod
    def log_common__fkwargs(self, **kwargs):
        # Procesar cada argumento de palabras clave y llamar a fvalue
        for index, value in kwargs.items():
            formatted_msg = f"{ANSI_RESET_BACKGROUND}{ANSI_GREEN_BRIGHT}{index}:{ANSI_RESET} {ANSI_RESET_BACKGROUND}{ANSI_RESET}{value}{ANSI_RESET}"
            self._log(LOG_LEVEL_FKWARG, formatted_msg, (), {})
    
    @staticmethod
    def log_common__args(self, *args):
        if not args:
            return
        if len(args) == 1 and not args[0]:
            return
        
        index = -1
        count = len(args)
        for value in args:
            index += 1
            
            # Verificar si el argumento es una clase o un classmethod
            if inspect.isclass(value) or (inspect.ismethod(value) and value.__self__ is not None):
                continue  # I
            formatted_msg = f"{ANSI_RESET_BACKGROUND}{ANSI_GREEN_BRIGHT}{index}:{ANSI_RESET} {ANSI_RESET_BACKGROUND}{ANSI_BLACK}{value}{ANSI_RESET}"
            self._log(LOG_LEVEL_FARG, formatted_msg, (), {})