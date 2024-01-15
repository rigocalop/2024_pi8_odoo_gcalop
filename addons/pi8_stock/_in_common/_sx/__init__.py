# -*- coding: utf-8 -*-
from .sx_convert_BaseConverter import sx_Base36Converter
from .sx_convert_BaseConverter import sx_Base62Converter
from .sx_convert_BaseConverter import sx_Base16Converter

class lib_sx:
    base16 = sx_Base16Converter
    base36 = sx_Base36Converter
    base62 = sx_Base62Converter


