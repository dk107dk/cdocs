from configparser import SafeConfigParser
from typing import Optional

class Config:

    def __init__(self, path:Optional[str]=None):
        if path is None:
            print("WARNING: config init without path. using default: config/config.ini")
            self._path = 'config/config.ini'
        else:
            self._path = path
        self._parser = SafeConfigParser()
        self._parser.read(self._path)

    def get(self, group, name) -> str:
        return self._parser.get(group, name)


