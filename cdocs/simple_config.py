from configparser import ConfigParser, NoSectionError
import os
from typing import Optional, List, Tuple
import logging
from cdocs.config import Config

class SimpleConfig(Config):

    def __init__(self, path:Optional[str]=None):
        super().__init__()
        if path is None:
            logging.debug(f"cdocs Config.__init__ without config path. using default: {os.getcwd()}/config/config.ini")
            self._path = 'config/config.ini'
        else:
            self._path = path
        self._parser = ConfigParser()
        self._parser.read(self._path)

    @property
    def parser(self) -> ConfigParser:
        return self._parser

    def get_config_path(self):
        return self._path

    def get_with_default(self, group, name, default:Optional[str]=None) -> str:
        val = self.get(group, name)
        if val is None:
            val = default
        return val

    def get(self, group:str, name:str) -> str:
        try:
            return self._parser.get(group, name)
        except Exception as e:
            logging.info(f"Cdocs Config.get: unable to get [{group}][{name}]: {e}. returning None.")
            return None

    def get_items(self, group:str, exceptnot:List[str]=None) -> List[Tuple[str, str]]:
        items = None
        try:
            items = self._parser.items(group)
        except (KeyError, NoSectionError):
            logging.info("Cdocs Config.get_items: no such group {group}. returning [].")
            items = []
        if exceptnot is not None:
            items = [ _ for _ in items if _[0] not in exceptnot]
        return items

