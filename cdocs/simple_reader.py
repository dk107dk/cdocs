import abc
import os.path
from .contextual_docs import Doc, FilePath
from cdocs.reader import Reader, ReadMetaData
import logging


class SimpleReader(Reader):

    def read(self, filepath:FilePath, meta:ReadMetaData=None) -> Doc:
        try:
            with open(filepath) as f:
                return Doc(f.read())
        except FileNotFoundError as fnfe:
            logging.warning(f'SimpleReader.read: cannot read: {fnfe}')
            # raise error?
            return None


    def is_available(self, filepath:FilePath, meta:ReadMetaData=None) -> bool:
        return os.path.isfile(filepath)


