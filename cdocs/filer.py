import abc
from typing import Union
from cdocs.contextual_docs import DocPath, FilePath

class Filer(metaclass=abc.ABCMeta):
    """
    Filer recognizes file types.
    """

    @abc.abstractmethod
    def get_filetype( self, path:Union[DocPath,FilePath]) -> str:
        pass

    @abc.abstractmethod
    def is_probably_not_binary(self, path:Union[DocPath,FilePath] ) -> bool:
        pass

