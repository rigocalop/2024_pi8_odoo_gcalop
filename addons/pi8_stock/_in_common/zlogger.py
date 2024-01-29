import logging
from .zlogger_formatter import *
    
class ZLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        
    ModeRun = "Normal"
    
    

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
    
    def log_common_init(self, level, msg, *args, **kwargs):
        ZLogger.disable_root_logger()   # Desactivar el logger raíz
        ZLogger_Vars.RUN_COUNTER +=1
        if self.isEnabledFor(level): # Log si el nivel es habilitado
            self._log(level, msg, (),{})
        
        if (args != None): ZLogger_CustomFormatter.log_common__args(self, *args)
        if (kwargs != None): ZLogger_CustomFormatter.log_common__fkwargs(self, **kwargs)
        ZLogger.enable_root_logger()   # Desactivar el logger raíz
    
    def log_common(self, level, msg, *args, **kwargs):
        ZLogger.disable_root_logger()   # Desactivar el logger raíz
        ZLogger_Vars.RUN_COUNTER +=1
        if self.isEnabledFor(level): # Log si el nivel es habilitado
            self._log(level, msg, (),{})
        
        if (args != None): ZLogger_CustomFormatter.log_common__args(self, *args)
        if (kwargs != None): ZLogger_CustomFormatter.log_common__fkwargs(self, **kwargs)
        ZLogger.enable_root_logger()   # Desactivar el logger raíz
        
#region "Metodos de log"
    def func_ini(self, msg, resalt=False, *args, **kwargs):
        if (resalt): self.log_common(LOG_LEVEL_FINI_RESALT, msg, *args, **kwargs)
        else: self.log_common(LOG_LEVEL_FINI, msg, *args, **kwargs)
    def func_end(self, msg, resalt=False, *args, **kwargs):
        if (resalt): self.log_common(LOG_LEVEL_FEND_RESALT, msg, *args, **kwargs)
        else: self.log_common(LOG_LEVEL_FEND, msg, *args, **kwargs)
    def superfunc_ini(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_FINI_SUPER, msg, *args, **kwargs)
    def superfunc_end(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_FEND_SUPER, msg, *args, **kwargs)        
    def test_ini(self, msg, resalt=False):
        if (resalt): self.log_common(LOG_LEVEL_FINI_RESALT, msg)
        else: self.log_common(LOG_LEVEL_FINI_TEST, msg)        
    def test_end(self, msg, resalt=False):
        if (resalt): self.log_common(LOG_LEVEL_FEND_RESALT, msg)
        else: self.log_common(LOG_LEVEL_FEND_TEST, msg)        
    def api_ini(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_FINI_API, msg, args, **kwargs)
    def api_end(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_FEND_API, msg, *args, **kwargs)
    def info(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_INFO, msg, *args, **kwargs)
    def warning(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_WARNING, msg, *args, **kwargs)
    def error(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_ERROR, msg, *args, **kwargs)
    def debug(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_DEBUG, msg, *args, **kwargs)                
    def returns(self, msg, *args, **kwargs):
        self.log_common(LOG_LEVEL_RETURNS, msg, *args, **kwargs)                
    def fvalue(self, msg, *args, **kwargs):
        if self.isEnabledFor(LOG_LEVEL_VALUE):
            self._log(LOG_LEVEL_VALUE, msg, args, **kwargs)
    def mark(self, msg, *args, **kwargs):
        if self.level == 1:
            self._log(LOG_LEVEL_MARK, msg, args, **kwargs)            
    def basic(self, msg, *args, **kwargs):
            self._log(LOG_LEVEL_MARK, msg, args, **kwargs)    
#endregion
