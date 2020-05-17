import os
import logging
from cdocs.contextual_docs import DocPath, FilePath
from cdocs.simple_config import SimpleConfig
from cdocs.pather import Pather
from typing import Optional

class SimplePather(Pather):

    def __init__(self, docspath:FilePath, config:FilePath=None):
        cfg = SimpleConfig(config)
        self._hashmark:str  = cfg.get_with_default("filenames", "hashmark", "#")
        self._docs_path:str = docspath
        self._ext:str  = cfg.get_with_default("formats", "ext", "xml")

    def get_full_file_path(self, path:DocPath) -> FilePath:
        return self.get_full_file_path_for_root(path, self._docs_path)

    def get_full_file_path_for_root(self, path:DocPath, root:FilePath) -> FilePath:
        path = path.strip('/\\')
        filename = self.get_filename(path)
        if filename is None:
            pass
        else:
            path = path[0:path.find(self._hashmark)]
        root = self._docs_path
        path = os.path.join(root, path)
        if filename is None and path.find(".") == -1:
            path = path + "." + self._ext
        elif filename is None:
            pass
        else:
            path = path + os.path.sep + filename + '.' + self._ext
        return FilePath(path)

    def get_filename(self, path:str) -> Optional[str]:
        filename = None
        hashmark = path.find(self._hashmark)
        if hashmark > -1:
            filename = path[hashmark+1:]
        return filename

