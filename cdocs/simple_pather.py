import os
import logging
from cdocs.contextual_docs import DocPath, FilePath
from cdocs.simple_config import SimpleConfig
from cdocs.pather import Pather
from typing import Optional

class SimplePather(Pather):

    def __init__(self, metadata, cdocs): #docspath:FilePath, config:FilePath=None):
        logging.info(f"SimplePather.__init__: starting with metadata: {metadata} and cdocs: {cdocs}")
        cfg = metadata.config
        logging.info(f"SimplePather.__init__: cfg: {cfg}")
        self._hashmark:str  = cfg.get("filenames", "hashmark", "#")
        logging.info(f"SimplePather.__init__: hashmark: {self._hashmark}")
        self._docs_path:str = cdocs.get_doc_root()
        self._rootname = cfg.get_matching_key_for_value("docs", cdocs.get_doc_root())
        logging.info(f"SimplePather.__init__: docspath: {cdocs.get_doc_root()}, rootname: {self._rootname}")
        ext = cfg.get("defaults", "ext", "xml")
        ext = cfg.get("formats", self._rootname, ext)
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
            logging.info(f"SimplePather.get_full_file_path_for_root: path points to root. returning root.")
            return root
        logging.info(f"SimplePather.get_full_file_path_for_root: getting filename for {path}")
        filename = self.get_filename(path)
        logging.info(f"SimplePather.get_full_file_path_for_root: path: {path}, filename: {filename}, root: {root}")
        if filename is None:
            pass
        else:
            path = path[0:path.find(self._hashmark)]
        #
        # why do we change out root here?  seems to do no harm, but...
        #
        #logging.info(f"SimplePather.get_full_file_path_for_root: root: {root}, _docs_path: {self._docs_path}")
        #root = self._docs_path
        #
        # if path were None we'd never get here!
        #
        #if path is None:
        #    logging.error(f"SimplePather.get_full_file_path_for_root: path is None")
        path = os.path.join(root, path)
        apath = path
        logging.info(f"SimplePather.get_full_file_path_for_root: joined root: {root} with path to get: {apath}")
        i = path.find(".")
        logging.info(f"SimplePather.get_full_file_path_for_root: index of '.': {i}")
        if filename is None and i <= len(root):
            logging.info(f"SimplePather.get_full_file_path_for_root: filename is None and no '.'")
            apath = self._find_path(apath)
        elif filename is None:
            logging.info(f"SimplePather.get_full_file_path_for_root: filename is None and there is a '.'")
            pass
        else:
            logging.info(f"SimplePather.get_full_file_path_for_root: apath: {apath}, last char: {apath[-1:]}, filename: {filename}")
            apath = apath + ('' if apath[-1:] == '/' else os.path.sep )+ filename
            apath = self._find_path(apath)
        if apath is None:
            logging.info(f"SimplePather.get_full_file_path_for_root: apath is None! from: {self._rootname}->{apath}")
        return FilePath(apath)

    #
    # 1. doesn't seem to look specifically for cdocs paths?
    # 2. see notes below
    #
    def _find_path(self, path) -> Optional[FilePath]:
        logging.info(f"SimplePather._find_path: starting path: {path}")
        logging.info(f"SimplePather._find_path: looking for path using exts in {self._exts}")
        for ext in self._exts:
            apath = None
            anext = path[-1*len(ext):]
            logging.info(f"SimplePather._find_path: checking if path's anext: {anext} matches ext: {ext}")
            if anext == ext:
                apath = path
            else:
                apath = path + "." + ext
            logging.info(f"SimplePather._find_path: checking for a simple file: apath: {apath}")
            if os.path.exists(apath):
                logging.info(f"SimplePather._find_path: apath exists. returning: {apath}")
                return apath
        if len(self._exts) == 1:
            logging.info(f"SimplePather._find_path: no file. just one ext. we assume name + '.' + ext")
            return path + "." + self._exts[0]
        elif len(self._exts) > 1:
            #
            # if any of the paths exists is knowable. shouldn't we check?
            #
            logging.info(f"SimplePather._find_path: on file. there are {len(self._exts)} exts, so we guess the first one, but check for actual files -- keep in mind, if the file exists or not is not a pather's problem.")
            presumedpath = path + "." + self._exts[0]
            logging.info(f"SimplePather._find_path: presumed path is {presumedpath}. now checking alternatives.")
            for _ in self._exts:
                apath = path + "." + _
                logging.info(f"SimplePather._find_path: checking if {apath} exists")
                if os.path.exists(apath):
                    logging.info(f"SimplePather._find_path: {apath} exists! returning it.")
                    return apath
            logging.info(f"SimplePather._find_path: no path exists. returning presumed path: {presumedpath}")
            return presumedpath
        else:
            logging.warning("SimplePather._find_path: no exts! you should fix this.")
        return None

    def get_filename(self, path:str) -> Optional[str]:
        logging.info(f"SimplePather.get_filename: path: {path}. if a hashmark is found it marks a filename. if no hashmark we return none.")
        filename = None
        hashmark = path.find(self._hashmark)
        if hashmark > -1:
            filename = path[hashmark+1:]
        logging.info(f"SimplePather.get_filename: returning: {filename if filename is not None else 'intentionally returning no filename'}")
        return filename

