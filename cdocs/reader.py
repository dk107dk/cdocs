import abc
from cdocs.contextual_docs import Doc, DocPath, FilePath


class Reader(metaclass=abc.ABCMeta):
    """
    Reader knows how to get bytes pointed to by a FilePath. By
    default the FilePath will be on the local filesystem.
    """

    @abc.abstractmethod
    def is_available(self, filepath:FilePath) -> bool:
        pass

    @abc.abstractmethod
    def read(self, filepath:FilePath) -> Doc:
        pass


