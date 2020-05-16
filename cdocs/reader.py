import abc
from cdocs.contextual_docs import Doc, DocPath, FilePath, DocsVersion, DocsName

class ReadMetaData(object):


    def __init__(self, \
            docpath:DocPath,
            docversion:DocsVersion, \
            public_root:FilePath, \
            internal_root:FilePath, \
            docsname:DocsName
    ):
        self._docpath = docpath
        self._docversion = docversion
        self._public_root = public_root
        self._internal_root = internal_root
        self._docsname = docsname


class Reader(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def is_available(self, filepath:FilePath, meta:ReadMetaData=None) -> bool:
        pass

    @abc.abstractmethod
    def read(self, filepath:FilePath, meta:ReadMetaData=None) -> Doc:
        pass


