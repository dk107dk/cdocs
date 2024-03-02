from typing import Optional, List, Dict
from datetime import datetime
from jinja2 import Template
import logging
import os
from cdocs.contextual_docs import Doc, DocPath, FilePath, JsonDict, ContextualDocs
from cdocs.config import Config, ConfigException
from cdocs.pather import Pather
from cdocs.reader import Reader
from cdocs.lister import Lister
from cdocs.finder import Finder
from cdocs.filer import Filer
from cdocs.transformer import Transformer
from cdocs.concatter import Concatter
from cdocs.simple_transformer import SimpleTransformer
from cdocs.simple_concatter import SimpleConcatter
from cdocs.simple_config import SimpleConfig
from cdocs.simple_reader import SimpleReader
from cdocs.simple_lister import SimpleLister
from cdocs.simple_pather import SimplePather
from cdocs.simple_finder import SimpleFinder
from cdocs.simple_filer import SimpleFiler
from cdocs.physical import Physical
from cdocs.multi_context_docs import MultiContextDocs
from cdocs.context_metadata import ContextMetadata
from cdocs.changer import Changer


class DocNotFoundException(Exception):
    pass


class BadDocPath(Exception):
    pass


class BadFilePath(Exception):
    pass


class ComposeDocException(Exception):
    pass


class Cdocs(ContextualDocs, Physical, Changer):
    def __init__(
        self,
        docspath: str,
        config: Optional[Config] = None,
        context: Optional[MultiContextDocs] = None,
    ):
        super().__init__()
        cfg = SimpleConfig(None) if config is None else config
        self._config = cfg
        self._context: MultiContextDocs = context
        self._docs_path: FilePath = docspath
        logging.info(f"get_matching_key_for_value: {docspath}")
        self._rootname = cfg.get_matching_key_for_value("docs", docspath)
        if self._rootname is None:
            raise ConfigException(f"Cdocs.__init__: no rootname for {docspath}")
        self._set_ext()
        self._tokens_filename: str = cfg.get("filenames", "tokens", "tokens.json")
        self._labels_filename: str = cfg.get("filenames", "labels", "labels.json")
        self._hashmark: str = cfg.get("filenames", "hashmark", "#")
        self._plus: str = cfg.get("filenames", "plus", "+")
        self._accepts = None

        self._track_last_change = False
        self._last_change = None
        self._last_change = self.get_last_change()
        #
        # these helpers can be swapped in and out as needed
        #
        self._concatter = SimpleConcatter(self)
        self._lister = SimpleLister(self)
        self._filer = SimpleFiler(self)
        self._transformer = SimpleTransformer(self)
        self._reader = SimpleReader(self) if cfg.reader is None else cfg.reader
        self._finder = SimpleFinder(self) if cfg.finder is None else cfg.finder

        if cfg.pather is None:
            logging.info("Cdocs.__init__: config's pather is None: {cfg}")
            metadata = ContextMetadata(cfg)
            # metadata.config = cfg
            self._pather = SimplePather(metadata, self)
            pass
        else:
            self._pather = cfg.pather
        logging.info(f"Cdocs.__init__: completed init. Cdocs is:\n{str(self)}")

    def __str__(self):
        return (
            "Cdocs: type(self): "
            + f"path: {self._docs_path}, "
            + f"accepts: {self.accepts}, "
            + f"exts: {self._exts}, "
            + f"tokens: {self._tokens_filename}, "
            + f"labels: {self._labels_filename}, "
            + f"hash: {self._hashmark}, "
            + f"plus: {self._plus}, "
            + f"config: {self._config}, "
            + f"context: {self._context}"
            + f"concatter: {self._concatter}, "
            + f"lister: {self._lister}, "
            + f"filer: {self._filer}, "
            + f"transformer: {self._transformer}, "
            + f"reader: {self._reader}, "
            + f"finder: {self._finder}, "
            + f"pather: {self._pather}"
        )

    def _set_ext(self) -> None:
        ext = self.config.get("defaults", "ext", "xml")
        logging.info(f"cdocs._set_ext 1: {ext}")
        ext = self.config.get("formats", self.rootname, ext)
        logging.info(f"cdocs._set_ext 2: {ext}")
        if ext.find(",") > -1:
            self._exts = ext.split(",")
        else:
            self._exts = [ext]

    def get_doc_root(self) -> FilePath:
        return FilePath(self._docs_path)

    @property
    def concatter(self) -> Concatter:
        return self._concatter

    @concatter.setter
    def concatter(self, c: Concatter) -> None:
        self._concatter = c

    @property
    def reader(self) -> Reader:
        return self._reader

    @reader.setter
    def reader(self, val: Reader) -> None:
        self._reader = val

    @property
    def finder(self) -> Finder:
        return self._finder

    @finder.setter
    def finder(self, val: Finder) -> None:
        self._finder = val

    @property
    def pather(self) -> Pather:
        return self._pather

    @pather.setter
    def pather(self, val: Pather) -> None:
        self._pather = val

    @property
    def lister(self) -> Lister:
        return self._lister

    @lister.setter
    def lister(self, val: Lister) -> None:
        self._lister = val

    @property
    def context(self) -> MultiContextDocs:
        return self._context

    @context.setter
    def context(self, val: MultiContextDocs) -> None:
        self._context = val

    @property
    def transformer(self) -> Transformer:
        return self._transformer

    @transformer.setter
    def transformer(self, val: Transformer) -> None:
        self._transformer = val

    @property
    def filer(self):
        return self._filer

    @filer.setter
    def filer(self, val: Filer) -> None:
        self._filer = val

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, val: Config) -> None:
        self._config = val

    @property
    def rootname(self):
        return self._rootname

    @property
    def exts(self):
        return self._exts

    @property
    def accepts(self):
        if self._accepts is None:
            logging.info(f"Cdocs.accepts: rootname: {self.rootname}")
            a = self.config.get("accepts", self.rootname)
            if a is None:
                self._accepts = ["cdocs"]
            else:
                self._accepts = a.split(",")
            logging.info(f"Cdocs.accepts: accepts: {self._accepts}")
        return self._accepts

    # ===================
    # abc methods
    # ===================

    def get_last_change(self) -> datetime:
        if self.track_last_change:
            lcf = self._get_last_change_file_path()
            if os.path.exists(lcf):
                last = None
                with (open(lcf, "r")) as lc:
                    last = lc.read()
                self._last_change = datetime.fromtimestamp(float(last))
            else:
                self.set_last_change()
            return self._last_change
        else:
            return None

    def _get_last_change_file_path(self):
        if self.track_last_change:
            path = f"{self.get_doc_root()}/.last_change"
            logging.info(f"Cdocs._get_last_change_file_path: path: {path}")
            if not os.path.exists(path):
                try:
                    os.makedirs(self.get_doc_root())
                except Exception as e:
                    logging.error(
                        f"Cdocs._get_last_change_file_path: create root failed: {self.get_doc_root()}: {e}"
                    )
            return path
        else:
            logging.info("Cdocs._get_last_change_file_path: ! self.track_last_change")
            return None

    def set_last_change(self) -> datetime:
        if not self.track_last_change:
            self.track_last_change = True
        self._last_change = datetime.now()
        self._write_last_change()
        return self._last_change

    def _write_last_change(self):
        if self.track_last_change:
            # write the datetime
            seconds = self._last_change.timestamp()
            # write
            lcf = self._get_last_change_file_path()
            with (open(lcf, "w")) as lc:
                try:
                    lc.write(str(seconds))
                except Exception as e:
                    logging.error(
                        f"cdocs._write_last_change: cannot write last change. refusing to crash.  {e}"
                    )

    @property
    def track_last_change(self) -> bool:
        return self._track_last_change

    @track_last_change.setter
    def track_last_change(self, do: bool) -> None:
        self._track_last_change = do

    def reset_last_change(self, dt: datetime, root: Optional[str] = None) -> None:
        if self.track_last_change:
            if root is not None and self.root_name != root:
                logging.info("Cdocs.reset_last_change: not for me: {root}")
                return
            self._last_change = dt
            self._write_last_change()

    def get_tokens(
        self,
        path: DocPath,
        recurse: Optional[bool] = True,
        addlabels: Optional[bool] = True,
    ) -> JsonDict:
        tokens = self._get_dict(path, self._tokens_filename, recurse)
        if addlabels:
            tokens = self._add_labels_to_tokens(path, tokens, recurse)
        return tokens

    def list_docs(self, path: DocPath) -> List[Doc]:
        docs = self.lister.list_docs(path)
        return docs

    def list_next_layer(self, path: DocPath) -> List[Doc]:
        docs = self.lister.list_next_layer(path)
        return docs

    def get_labels(self, path: DocPath, recurse: Optional[bool] = True) -> JsonDict:
        labels = self._get_dict(path, self._labels_filename, recurse)
        return self._transform_labels(path, labels)

    def get_compose_doc(self, path: DocPath) -> Doc:
        if path is None:
            raise DocNotFoundException("path can not be None")
        filepath: FilePath = self._pather.get_full_file_path(path)
        try:
            print(f"Cdocs.get_compose_doc: fp: {filepath}")
            content = self._read_doc(filepath)
            tokens: dict = self.get_tokens(path[0 : path.rindex("/")])
            content = self.transformer.transform(content, path, tokens, True)
            return Doc(content)
        except Exception as e:
            logging.error(f"Cdocs.get_compose_doc: cannot compose {path}: {e}")
            raise ComposeDocException(f"{path} failed to compose")

    def get_concat_doc(self, path: DocPath) -> Doc:
        if path is None:
            raise DocNotFoundException("path can not be None")
        if path.find(".concat") == -1:
            raise BadDocPath("path must have a .concat file extension")
        paths = self._get_concat_paths(path)
        if paths is None:
            raise DocNotFoundException(f"No concat instruction file at {path}")
        content = self.concatter.concat(paths)
        return Doc(content)

    def get_doc(self, path: DocPath, notfound: Optional[bool] = True) -> Doc:
        return self._get_doc(path, notfound)

    def _get_doc(self, path: DocPath, notfound) -> Optional[Doc]:
        logging.info(
            f"Cdocs._get_doc: looking for path: {path} in root: {self.rootname}. notfound: {notfound}"
        )
        if path is None:
            raise DocNotFoundException("path can not be None")
        if path.find(".") > -1:
            if self.filer.get_filetype(path) == "cdocs":
                raise BadDocPath("dots are not allowed in cdoc paths")
        if notfound is None:
            logging.info(
                "Cdocs._get_doc: notfound is None. you should fix this unless you want None returns."
            )
            notfound = False
        logging.info(f"Cdocs._get_doc: path: {path}")
        pluspaths = self._get_plus_paths(path)
        logging.info(f"Cdocs._get_doc: pluspaths to concationate: {pluspaths}")
        root = self.get_doc_root()
        logging.info(f"Cdocs._get_doc: root {root}")
        doc = self._get_doc_for_root(path, pluspaths, root)
        logging.info(f"Cdocs._get_doc: found doc {doc}")
        if doc is None and notfound:
            doc = self.get_404()
        return doc

    # ===================
    # internal methods
    # ===================

    def get_404(self) -> Optional[Doc]:
        config = self.config
        _404 = config.get("notfound", self._rootname, None)
        logging.info(f"Cdocs.get_404: notfound in {self._rootname} is {_404}")
        if _404 is None:
            return None
        doc = self.get_doc(_404, False)
        if doc is None:
            logging.error(
                f"Cdocs.get_404: {self._rootname}'s notfound: {_404} is None. you shouldl fix this."
            )
        logging.info(f"Cdocs.get_404: doc: {doc}")
        return doc

    def _get_doc_for_root(
        self, path: DocPath, pluspaths: List[DocPath], root: FilePath
    ) -> Doc:
        logging.info(
            f"Cdocs._get_doc_for_root: path: {path}. plus paths: {pluspaths}. root: {root}"
        )
        if len(pluspaths) > 0:
            logging.info(
                "Cdocs._get_doc_for_root: stripping down base path from plus path(s)"
            )
            plus = path.find(self._plus)
            path = path[0:plus]
            logging.info(f"Cdocs._get_doc_for_root: base path is now {path}")
        logging.info(
            f"Cdocs._get_doc_for_root: checking pather: {self._pather} for path: {path}"
        )
        filepath = self._pather.get_full_file_path_for_root(path, root)
        logging.info(f"Cdocs._get_doc_for_root: filepath from pather: {filepath}")
        content = self._read_doc(filepath)
        logging.info(
            f"Cdocs._get_doc_for_root: content from {filepath} is {len(content) if content is not None else 0} chars. transforming with: {self.transformer}."
        )
        content = self.transformer.transform(content, path, None, True)
        if len(pluspaths) > 0:
            content = self.concatter.join(content, self.concatter.concat(pluspaths))
        return Doc(content)

    def _transform_labels(self, path: DocPath, labels: JsonDict) -> JsonDict:
        tokens: dict = self.get_tokens(path, addlabels=False)
        ls = {
            k: self.transformer.transform(v, path, tokens, False)
            for k, v in labels.items()
        }
        return JsonDict(ls)

    def _add_labels_to_tokens(
        self, path: DocPath, tokens: JsonDict, recurse: Optional[bool] = True
    ) -> JsonDict:
        apath = path
        if path.find(self._hashmark) > -1:
            apath = apath[0 : apath.find(self._hashmark)]
        if apath.find(self._plus) > -1:
            apath = apath[0 : apath.find(self._plus)]
        labels = self.get_labels(apath, recurse)
        ltokens = {"label__" + k: v for k, v in labels.items()}
        tokens = {**ltokens, **tokens}
        return JsonDict(tokens)

    def _get_plus_paths(self, path: DocPath) -> List[DocPath]:
        lines = path.split(self._plus)
        if len(lines) == 0:
            return lines
        first = lines[0]
        lines = lines[1:]
        mark = first.find(self._hashmark)
        if mark > -1:
            first = first[0 : mark + 1]
        else:
            first += self._hashmark
        lines = [DocPath(first + line) for line in lines]
        return lines

    def _get_concat_paths(self, path: DocPath) -> Optional[List[DocPath]]:
        filepath = self._pather.get_full_file_path(path)
        try:
            content = self._read_doc(filepath)
            lines = [DocPath(line) for line in content.split("\n")]
            return lines
        except DocNotFoundException:
            logging.warn(
                f"Cdocs._get_concat_paths: No such doc {path}. returning None."
            )
            return None

    def _read_doc(self, path: FilePath) -> str:
        content = None
        available = self._reader.is_available(path)
        logging.info(f"Cdocs._read_doc: {path} is available: {available}")
        if available:
            content = self.reader.read(path)
            if self.filer.is_probably_not_binary(path):
                content = content.decode("utf-8")
            if content is None:
                logging.warning(f"Cdocs._read_doc: cannot read {path}. returning None.")
        else:
            logging.debug(f"Cdocs._read_doc: No such doc {path}. returning None.")
        logging.info(f"Cdocs._read_doc: returning: {content}")
        return content

    def _get_dict(
        self, path: str, filename: str, recurse: Optional[bool] = True
    ) -> JsonDict:
        path = path.strip("/\\")
        return JsonDict(self.finder.find_tokens(path, filename, recurse))
