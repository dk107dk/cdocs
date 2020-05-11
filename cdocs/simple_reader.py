import abc
from cdocs.contextual_docs import Doc, FilePath
from cdocs.reader import Reader, ReadMetaData
import logging


class SimpleReader(Reader):

    def read(self, filepath:FilePath, meta:ReadMetaData=None) -> Doc:
        try:
            with open(filepath) as f:
                return Doc(f.read())
        except FileNotFoundError as fnfe:
            logging.error(f'SimpleReader.read: cannot read: {fnfe}')
            raise DocNotFoundException(f"unreadable path: {filepath}")



