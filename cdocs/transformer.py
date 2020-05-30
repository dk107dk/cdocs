import abc
from cdocs.contextual_docs import DocPath
from typing import Optional, Dict

class Transformer(metaclass=abc.ABCMeta):
    """
    Transformer knows how to convert a string to its final form
    """

    @abc.abstractmethod
    def transform(self, content:str, path:DocPath=None, \
                   tokens:Optional[Dict[str,str]]=None, transform_labels=True) -> str:
        pass

