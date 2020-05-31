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
        self._rootname = cfg.get_matching_key_for_value("docs", docspath)
        logging.info(f"SimplePather.__init__: docspath: {docspath}, rootname: {self._rootname}")
        ext = cfg.get_with_default("formats", "ext", "xml")
        ext = cfg.get_with_default("formats", self._rootname, ext)
        logging.info(f"SinplePather.__init__: ext: {ext}")
        if ext.find(",") > -1:
            self._exts = ext.split(",")
        else:
            self._exts = [ext]
        logging.info(f"SimplePather.__init__: exts: {self._exts}")

    def get_full_file_path(self, path:DocPath) -> FilePath:
        return self.get_full_file_path_for_root(path, self._docs_path)

    def get_full_file_path_for_root(self, path:DocPath, root:FilePath) -> FilePath:
        logging.info(f"SimplePather.get_full_file_path_for_root: path: {path}, root: {root}")
        path = path.strip('/\\')
        if path == '':
            return root
        filename = self.get_filename(path)
        logging.info(f"SimplePather.get_full_file_path_for_root: filename: {filename}, root: {root}")
        if filename is None:
            pass
        else:
            path = path[0:path.find(self._hashmark)]
        root = self._docs_path
        path = os.path.join(root, path)
        apath = path
        logging.info(f"SimplePather.get_full_file_path_for_root: apath: {apath}")
        if filename is None and path.find(".") == -1:
            logging.info(f"SimplePather.get_full_file_path_for_root: filename is None and no '.'")
            apath = self._find_path(apath)
        elif filename is None:
            logging.info(f"SimplePather.get_full_file_path_for_root: filename is None")
            pass
        else:
            logging.info(f"SimplePather.get_full_file_path_for_root: filename: {filename}")
            apath = apath + os.path.sep + filename
            apath = self._find_path(apath)
        if apath is None:
            logging.info(f"SimplePather.get_full_file_path_for_root: apath is None! from: {self._rootname}->{apath}")
        return FilePath(apath)

    def _find_path(self, path) -> Optional[FilePath]:
        logging.info(f"SimplePather._find_path: path: {path}")
        for ext in self._exts:
            apath = path + "." + ext
            logging.info(f"SimplePather._find_path: checking: apath: {apath}")
            if os.path.exists(apath):
                return apath
        return None

    def get_filename(self, path:str) -> Optional[str]:
        logging.info(f"SimplePather.get_filename: path: {path}")
        filename = None
        hashmark = path.find(self._hashmark)
        if hashmark > -1:
            filename = path[hashmark+1:]
        logging.info(f"SimplePather.get_filename: returning filename: {filename}")
        return filename

