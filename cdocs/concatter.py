import abc
from cdocs.contextual_docs import Doc, DocPath
from typing import List


class Concatter(metaclass=abc.ABCMeta):
    """
    Concatter knows how to string content together into a single string.
    """

    @abc.abstractmethod
    def concat(self, paths:List[DocPath]) -> Doc:
        path

