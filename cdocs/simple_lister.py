from typing import List
from cdocs.contextual_docs import Doc, DocPath
from cdocs.lister import Lister
import os
import logging

class SimpleLister(Lister):

    def __init__(self, cdocs):
        self._cdocs = cdocs

    def list_docs(self, path:DocPath) -> List[Doc]:
        logging.info(f"SimpleLister.list_docs: path: {path}")
        root_path = self._cdocs.get_doc_root()
        logging.info(f"SimpleLister.list_docs: root: {root_path}")
        if path[0:1] == '/':
            path = path[1:]
        the_path = os.path.join(root_path, path)
        logging.info(f"SimpleLister.list_docs: the_path: {the_path}")
        files = os.listdir(the_path)
        logging.info(f"SimpleLister.list_docs: files: {files}")
        files = [f for f in files if f[0:1] != '.' and os.path.isfile(os.path.join(the_path, f))]
        logging.info(f"SimpleLister.list_docs: returning: {files}")
        return files

