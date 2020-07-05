import abc
from typing import Optional, List, Tuple
from cdocs.physical import Physical

class ConfigException(Exception):
    pass


class Config(Physical, metaclass=abc.ABCMeta):
    """
    Config is a sectioned key-value store interface that follows configparser
    """

    @abc.abstractmethod
    def get_config_path(self):
        pass

    @abc.abstractmethod
    def get(self, group:str, name:str, default:Optional[str]=None) -> str:
        pass

    @abc.abstractmethod
    def get_items(self, group:str, exceptnot:List[str]=None) -> List[Tuple[str, str]]:
        pass

    @abc.abstractmethod
    def get_matching_key_for_value(self, group:str, value:str) -> Optional[str]:
        pass
