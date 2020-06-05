from typing import Optional, List, Dict
from jinja2 import Template
import logging
from cdocs.contextual_docs import Doc, DocPath, FilePath, JsonDict, ContextualDocs
from cdocs.config import Config
from cdocs.pather import Pather
from cdocs.reader import Reader
from cdocs.finder import Finder
from cdocs.transformer import Transformer
from cdocs.concatter import Concatter
from cdocs.simple_transformer import SimpleTransformer
from cdocs.simple_concatter import SimpleConcatter
from cdocs.simple_config import SimpleConfig
from cdocs.simple_reader import SimpleReader
from cdocs.simple_pather import SimplePather
from cdocs.simple_finder import SimpleFinder
from cdocs.simple_filer import SimpleFiler
from cdocs.physical import Physical
from cdocs.multi_context_docs import MultiContextDocs
from cdocs.context_metadata import ContextMetadata


class DocNotFoundException(Exception):
    pass

class BadDocPath(Exception):
    pass

class ComposeDocException(Exception):
    pass


class Cdocs(ContextualDocs, Physical):

    def __init__(self, docspath:str, config:Optional[Config]=None, context:Optional[MultiContextDocs]=None):
        super().__init__()
        cfg = SimpleConfig(None) if config is None else config
        self._config = cfg
        self._context:MultiContextDocs = context
        self._docs_path:FilePath = docspath
        self._rootname = cfg.get_matching_key_for_value("docs", docspath)
        self._set_ext()
        self._tokens_filename:str  = cfg.get_with_default("filenames", "tokens", "tokens.json")
        self._labels_filename:str  = cfg.get_with_default("filenames", "labels", "labels.json")
        self._hashmark:str  = cfg.get_with_default("filenames", "hashmark", "#")
        self._plus:str  = cfg.get_with_default("filenames", "plus", "+")
        #
        # these helpers can be swapped in and out as needed
        #
        self._concatter = SimpleConcatter(self)
        self._filer = SimpleFiler()
        self._transformer = SimpleTransformer(self)
        self._reader = SimpleReader() if cfg.reader is None else cfg.reader
        self._finder = SimpleFinder(docspath) if cfg.finder is None else cfg.finder
        if cfg.pather is None:
            metadata = ContextMetadata()
            metadata.config = cfg
            self._pather = SimplePather(metadata, self)
            pass
        else:
            self._pather = cfg.pather
            #self._pather = SimplePather(self._docs_path, cfg.get_config_path()) if cfg.pather is None else cfg.pather
        #
        logging.info(f"Cdocs.__init__: path: {self._docs_path}, exts: {self._exts}, \
tokens: {self._tokens_filename}, labels: {self._labels_filename}, \
hash: {self._hashmark}, plus: {self._plus}")

    def _set_ext(self) -> None:
        ext = self.config.get_with_default("formats", "ext", "xml")
        ext = self.config.get_with_default("formats", self.rootname, ext)
        if ext.find(",") > -1:
            self._exts = ext.split(",")
        else:
            self._exts = [ext]

    def get_doc_root(self) -> FilePath:
        return FilePath(self._docs_path)

    def get_tokens(self, path:DocPath) -> JsonDict:
        return self._get_dict(path, self._tokens_filename)

    @property
    def concatter(self) -> Concatter:
        return self._concatter

    @property
    def reader(self) -> Reader:
        return self._reader

    @property
    def finder(self) -> Finder:
        return self._finder

    @property
    def pather(self) -> Pather:
        return self._pather

    @property
    def context(self) -> MultiContextDocs:
        return self._context

    @property
    def transformer(self) -> Transformer:
        return self._transformer

    @context.setter
    def context(self, ctx:MultiContextDocs) -> None:
        self._context = ctx

    @property
    def filer(self):
        return self._filer

    @property
    def config(self):
        return self._config

    @property
    def rootname(self):
        return self._rootname

    @property
    def exts(self):
        return self._exts

# ===================
# abc methods
# ===================

    def get_labels(self, path:DocPath) -> JsonDict:
        labels = self._get_dict(path, self._labels_filename)
        return self._transform_labels(path, labels)

    def get_compose_doc(self, path:DocPath) -> Doc:
        if path is None :
            raise DocNotFoundException("path can not be None")
        filepath:FilePath = self._pather.get_full_file_path(path)
        try:
            content = self._read_doc(filepath)
            tokens:dict = self.get_tokens(path[0:path.rindex('/')])
            content = self.transformer.transform(content, path, tokens, True)
            return Doc(content)
        except Exception as e:
            logging.error(f"Cdocs.get_compose_doc: cannot compose {path}: {e}")
            raise ComposeDocException(f'{path} failed to compose')

    def get_concat_doc(self, path:DocPath) -> Doc:
        if path is None :
            raise DocNotFoundException("path can not be None")
        if path.find('.concat') == -1:
            raise BadDocPath("path must have a .concat file extension")
        paths = self._get_concat_paths(path)
        if paths is None:
            raise DocNotFoundException(f'No concat instruction file at {path}')
        content = self.concatter.concat(paths)
        return Doc(content)

    def get_doc(self, path:DocPath) -> Doc:
        return self._get_doc(path, True)

    def _get_doc(self, path:DocPath, notfound:Optional[bool]=False) -> Optional[Doc]:
        if path is None :
            raise DocNotFoundException("path can not be None")
        if path.find('.') > -1:
            if self.filer.get_filetype(path) == 'cdocs':
                raise BadDocPath("dots are not allowed in cdoc paths")
        logging.info(f"Cdocs._get_doc: path: {path}")
        pluspaths = self._get_plus_paths(path)
        logging.info(f"Cdocs._get_doc: pluspaths {pluspaths}")
        root = self.get_doc_root()
        logging.info(f"Cdocs._get_doc: root {root}")
        doc = self._get_doc_for_root(path, pluspaths, root)
        if doc is None and notfound:
           doc = self.get_404()
        return doc

# ===================
# internal methods
# ===================

    def get_404(self) -> Optional[Doc]:
        config = self.config
        _404 = config.get_with_default("defaults", "notfound", None)
        if _404 is None:
            return None
        index = _404.find("/")
        root = _404[0:index]
        path = _404[index+1:]
        root = config.get("docs", root)
        cdocs = Cdocs(root)
        doc = cdocs._get_doc_for_root(path, [], root)
        return doc

    def _get_doc_for_root(self, path:DocPath, pluspaths:List[DocPath], root:FilePath) -> Doc:
        if len(pluspaths) > 0:
            plus = path.find(self._plus)
            path = path[0:plus]
        filepath = self._pather.get_full_file_path_for_root(path, root)
        logging.info(f"Cdocs._get_doc_for_root: fp {filepath}")
        content = self._read_doc(filepath)
        content = self.transformer.transform(content, path, None, True)
        if len(pluspaths) > 0:
            content = self.concatter.join(content, self.concatter.concat(pluspaths))
        return Doc(content)

    def _transform_labels(self, path:DocPath, labels:JsonDict) -> JsonDict:
        tokens:dict = self.get_tokens(path)
        ls = { k:self.transformer.transform(v, path, tokens, False) for k,v in labels.items() }
        return JsonDict(ls)

    def _add_labels_to_tokens(self, path:DocPath, tokens:JsonDict) -> JsonDict:
        apath = path
        if path.find(self._hashmark):
            apath = apath[0:apath.find(self._hashmark)]
        if apath.find(self._plus):
            apath = apath[0:apath.find(self._plus)]
        labels = self.get_labels(apath)
        ltokens = { "label__"+k:v for k,v in labels.items()}
        tokens  = {**ltokens, **tokens}
        return JsonDict(tokens)

    def _get_plus_paths( self, path:DocPath) -> List[DocPath]:
        lines = path.split(self._plus)
        if len(lines) == 0:
            return lines
        first = lines[0]
        lines = lines[1:]
        mark = first.find(self._hashmark)
        if mark > -1:
            first = first[0:mark+1]
        else:
            first += self._hashmark
        lines = [ DocPath(first+line) for line in lines]
        return lines

    def _get_concat_paths(self, path:DocPath) -> Optional[List[DocPath]]:
        filepath = self._pather.get_full_file_path(path)
        try:
            content = self._read_doc(filepath)
            lines = [DocPath(line) for line in content.split('\n')]
            return lines
        except DocNotFoundException:
            logging.warn(f"Cdocs._get_concat_paths: No such doc {path}. returning None.")
            return None

    def _read_doc(self, path:FilePath) -> str:
        content = None
        available = self._reader.is_available(path)
        logging.info(f"Cdocs._read_doc: {available}")
        if available:
            content = self.reader.read(path)
            if self.filer.is_probably_not_binary(path):
                content = content.decode('utf-8')
            if content is None:
                logging.warning(f"Cdocs._read_doc: cannot read {path}. returning None.")
        else:
            logging.debug(f"Cdocs._read_doc: No such doc {path}. returning None.")
        logging.info(f"Cdocs._read_doc: returning: {content}")
        return content

    def _get_dict(self, path:str, filename:str) -> JsonDict:
        path = path.strip('/\\')
        docroot = self.get_doc_root()
        return JsonDict(self.finder.find_tokens(path, filename))



