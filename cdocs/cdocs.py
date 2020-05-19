from typing import Optional, List, Dict
from jinja2 import Template
import logging
from cdocs.contextual_docs import Doc, DocPath, FilePath, JsonDict, ContextualDocs
from cdocs.config import Config
from cdocs.pather import Pather
from cdocs.reader import Reader
from cdocs.finder import Finder
from cdocs.simple_config import SimpleConfig
from cdocs.simple_reader import SimpleReader
from cdocs.simple_pather import SimplePather
from cdocs.simple_finder import SimpleFinder
from cdocs.simple_filer import SimpleFiler
from cdocs.physical import Physical

class DocNotFoundException(Exception):
    pass

class BadDocPath(Exception):
    pass

class ComposeDocException(Exception):
    pass


class Cdocs(ContextualDocs, Physical):

    def __init__(self, docspath:str, config:Optional[Config]=None):
        super().__init__()
        cfg = SimpleConfig(None) if config is None else config
        self._config = cfg
        self._docs_path:str = docspath
        self._ext:str  = cfg.get_with_default("formats", "ext", "xml")
        self._filer = SimpleFiler()
        self._tokens_filename:str  = cfg.get_with_default("filenames", "tokens", "tokens.json")
        self._labels_filename:str  = cfg.get_with_default("filenames", "labels", "labels.json")
        self._hashmark:str  = cfg.get_with_default("filenames", "hashmark", "#")
        self._plus:str  = cfg.get_with_default("filenames", "plus", "+")
        self.reader = SimpleReader() if cfg.reader is None else cfg.reader
        self.finder = SimpleFinder(docspath) if cfg.finder is None else cfg.finder
        self.pather = SimplePather(self._docs_path, cfg.get_config_path()) if cfg.pather is None else cfg.pather
        logging.info(f"Cdocs.__init__: path: {self._docs_path}, ext: {self._ext}, \
tokens: {self._tokens_filename}, labels: {self._labels_filename}, \
hash: {self._hashmark}, plus: {self._plus}")


    def get_doc_root(self) -> FilePath:
        return FilePath(self._docs_path)

    def get_tokens(self, path:DocPath) -> JsonDict:
        return self._get_dict(path, self._tokens_filename)

    @property
    def filer(self):
        return self._filer

    @property
    def config(self):
        return self._config

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
            content = self._transform(content, path, tokens, True)
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
        content = self._concat( paths)
        return Doc(content)

    def get_doc(self, path:DocPath) -> Doc:
        return self._get_doc(path, True)

    def _get_doc(self, path:DocPath, notfound:Optional[bool]=False) -> Optional[Doc]:
        if path is None :
            raise DocNotFoundException("path can not be None")
        if path.find('.') > -1:
            if self.filer.get_filetype(path) == 'cdocs':
                raise BadDocPath("dots are not allowed in cdoc paths")
        pluspaths = self._get_plus_paths(path)
        root = self.get_doc_root()
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
        print(f"_get_doc_for_root: {filepath}")
        content = self._read_doc(filepath)
        content = self._transform(content, path, None, True)
        if len(pluspaths) > 0:
            for apath in pluspaths:
                content += " " + self._get_doc_for_root(apath, [], root)
        return Doc(content)

    def _transform_labels(self, path:DocPath, labels:JsonDict) -> JsonDict:
        tokens:dict = self.get_tokens(path)
        ls = { k:self._transform(v, path, tokens, False) for k,v in labels.items() }
        return JsonDict(ls)

    def _transform(self, content:str, path:DocPath=None, tokens:Optional[Dict[str,str]]=None, transform_labels=True) -> str:
        if content is None:
            logging.info("Cdocs._transform: cannot transform None. returning ''")
            return None
        if path is None:
            raise BadDocPath("you must provide the DocPath")
        filetype = self.filer.get_filetype(path)
        if filetype in ['html','concat','cdocs']:
            if tokens is None:
                tokens:JsonDict = self.get_tokens(path)
            if path is not None and transform_labels:
                tokens = self._add_labels_to_tokens(path, tokens)
            tokens["get_doc"] = self.get_doc
            try:
                template = Template(content)
                content = template.render(tokens)
            except Exception as e:
                logging.info(f"couldn't transform content: {e}")
        return content

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

    def _concat(self, paths:List[DocPath]) -> Doc:
        result = ''
        for apath in paths:
            if apath.strip() == '':
                pass
            else:
                doc = self.get_doc(apath)
                result += '\n' + doc
        return Doc(result)

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
            #
            #
            #
            if self.filer.is_probably_not_binary(path):
                content = content.decode('utf-8')
            #
            #
            #
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



