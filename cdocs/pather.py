import abc
import os
from cdocs.contextual_docs import DocPath, FilePath
from typing import Optional

class Pather(metaclass=abc.ABCMeta):
    """
    Pather handles converting DocPath to FilePath. In other words, it
    knows how to take an abstract Cdocs path and turn it into a
    physical path, by default in the local filesystem.
    """

    @abc.abstractmethod
    def get_full_file_path(self, path:DocPath) -> FilePath:
        pass

    @abc.abstractmethod
    def get_full_file_path_for_root(self, path:DocPath, root:FilePath) -> FilePath:
        pass

    @abc.abstractmethod
    def get_filename(self, path:str) -> Optional[str]:
        pass

