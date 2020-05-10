from configparser import ConfigParser
import os
from typing import Optional

class Config:

    def __init__(self, path:Optional[str]=None):
        if path is None:
            print(f"WARNING: cdocs config init without config path. using default: {os.getcwd()}/config/config.ini")
            self._path = 'config/config.ini'
        else:
            self._path = path
        self._parser = ConfigParser()
        self._parser.read(self._path)

    def get_with_default(self, group, name, default:Optional[str]=None) -> str:
        val = self.get(group, name)
        if val is None:
            val = default
        return val

    def get(self, group, name) -> str:
        try:
            return self._parser.get(group, name)
        except Exception as e:
            print(f"Unable to get [{group}][{name}]: {e}")
            return None


