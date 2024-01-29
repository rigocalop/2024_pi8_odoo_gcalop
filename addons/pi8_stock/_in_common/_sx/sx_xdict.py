import json
from .._sx.sx_xlist import sx_XList

class sx_XDict:
    @classmethod
    def Select(cls, dict, fields):
        """
        Filtra un diccionario, dejando solo las claves especificadas en keys_list.
        """
        fields = sx_XList.ensure(fields)
        filtered_dict = {key: dict[key] for key in fields if key in dict}
        return filtered_dict    

class Dict(dict):
    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__(*args, **kwargs)
        self._dict = dict(*args, **kwargs)
        self._keys = list(self._dict.keys())
        self._values = list(self._dict.values())
        self._items = list(self._dict.items())
        self._len = len(self._dict)
        self._str = str(self._dict)
        self._repr = repr(self._dict)
        self._json = json.dumps(self._dict)
        self._json_pretty = json.dumps(self._dict, indent=4, sort_keys=True)
        self._json_pretty_html = json.dumps(self._dict, indent=4, sort_keys=True).replace('\n', '<br/>')
        self._json_pretty_html = self._json_pretty_html.replace(' ', '&nbsp;')
        self._json_pretty_html = self._json_pretty_html.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        self._json_pretty_html = self._json_pretty_html.replace('\"', '&quot;')
        self._json_pretty_html = self._json_pretty_html.replace('\'', '&apos;')
        self._json_pretty_html = self._json_pretty_html.replace('\r', '')
        self._json_pretty_html = self._json_pretty_html.replace('\n', '<br/>')
        self._json_pretty_html = self._json_pretty_html.replace(' ', '&nbsp;')
        self._json_pretty_html = self._json_pretty_html.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        self._json_pretty_html = self._json_pretty_html.replace('\"', '&quot;')
        self._json_pretty_html = self._json_pretty_html.replace('\'', '&apos;')
        self._json_pretty_html = self._json_pretty_html.replace('\r', '')
        self._json_pretty_html = self._json_pretty_html.replace('\n', '<br/>')
        self._json_pretty_html = self._json_pretty_html.replace(' ', '&nbsp;')
        self._json_pretty_html = self._json_pretty_html.replace('\t', '&nbsp;&nbsp;&')

    
    
    def Select(self, fields):
        """
        Filtra un diccionario, dejando solo las claves especificadas en keys_list.
        """
        return sx_XDict.Select(self, fields)
