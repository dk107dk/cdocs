import abc
import os.path
from .contextual_docs import Doc, FilePath
from cdocs.reader import Reader
import logging
import traceback

class SimpleReader(Reader):

    def __init__(self, cdocs):
        self._cdocs = cdocs

    def read(self, filepath:FilePath) -> Doc:
        try:
            with open(filepath, 'rb') as f:
                doc = Doc(f.read())
                #print(f"SimpleReader.read: doc is {doc} of type {type(doc)}")
                return doc
        except FileNotFoundError as fnfe:
            logging.warning(f'SimpleReader.read: cannot read: {fnfe}')
            # raise error?
            return None


    def is_available(self, filepath:FilePath) -> bool:
        if filepath is None:
            logging.warning(f"SimpleReader.is_available: filepath is None")
            #traceback.print_stack(limit=7)
            return False
        return os.path.isfile(filepath)


