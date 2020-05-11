import os
import json
from pathlib import Path
from typing import Optional, List, Dict
from jinja2 import Template
from cdocs.config import Config
from cdocs.contextual_docs import ContextualDocs
from cdocs.dict_finder import DictFinder
from cdocs.contextual_docs import Doc, DocPath, FilePath, JsonDict
from cdocs.simple_reader import SimpleReader
from cdocs.reader import Reader


class DocNotFoundException(Exception):
    pass

class BadDocPath(Exception):
    pass

class ComposeDocException(Exception):
    pass


class Cdocs(ContextualDocs):

    def __init__(self, configpath:Optional[str]=None):
        cfg = Config(configpath)
        self._docs_path = cfg.get("docs", "public")
        self._internal_path = cfg.get("docs", "internal")
        self._ext = cfg.get_with_default("formats", "ext", "xml")
        self._tokens_filename = cfg.get_with_default("filenames", "tokens", "tokens.json")
        self._labels_filename = cfg.get_with_default("filenames", "labels", "labels.json")
        self._hashmark = cfg.get_with_default("filenames", "hashmark", "#")
        self._plus = cfg.get_with_default("filenames", "plus", "+")
        self._reader = SimpleReader()

    def set_reader(self, reader:Reader) -> None:
        self._reader = reader

    def get_doc_root(self) -> FilePath:
        return FilePath(self._docs_path)

    def get_internal_root(self) -> FilePath:
        return FilePath(self._internal_path)

    def get_tokens(self, path:DocPath) -> JsonDict:
        return self._get_dict(path, self._tokens_filename)

    def get_labels(self, path:DocPath) -> JsonDict:
        labels = self._get_dict(path, self._labels_filename)
        return self._transform_labels(path, labels)

    def get_compose_doc(self, path:DocPath) -> Doc:
        if path is None :
            raise DocNotFoundException("path can not be None")
        if path.find('.html') == -1 and path.find('.md') == -1 and path.find('.xml') == -1:
            raise BadDocPath("file at path must be .html, .md or .xml")
        filepath:FilePath = self._get_full_file_path(path)
        try:
            content = self._read_doc(filepath)
            tokens:dict = self.get_tokens(path[0:path.rindex('/')])
            content = self._transform(content, path, tokens, True)
            return Doc(content)
        except Exception as e:
            print(f"cannot compose {path}: {e}")
            raise ComposeDocException(f'{path} failed to compose')

    def get_concat_doc(self, path:DocPath) -> Doc:
        if path is None :
            raise DocNotFoundException("path can not be None")
        if path.find('.txt') == -1:
            raise BadDocPath("path must have a .txt file extension")
        paths = self._get_concat_paths(path)
        if paths is None:
            raise DocNotFoundException(f'No concat instruction file at {path}')
        content = self._concat( paths)
        return Doc(content)

    def get_doc(self, path:DocPath) -> Doc:
        if path is None :
            raise DocNotFoundException("path can not be None")
        if path.find('.') > -1:
            raise BadDocPath("dots are not allowed in doc paths")
        pluspaths = self._get_plus_paths(path)
        if len(pluspaths) > 0:
            plus = path.find(self._plus)
            path = path[0:plus]
        filepath = self._get_full_file_path(path)
        content = self._read_doc(filepath)
        content = self._transform(content, path, None, True)
        if len(pluspaths) > 0:
            for apath in pluspaths:
                content += " " + self.get_doc(apath)
        return Doc(content)

    def _transform_labels(self, path:DocPath, labels:JsonDict) -> JsonDict:
        tokens:dict = self.get_tokens(path)
        ls = { k:self._transform(v, path, tokens, False) for k,v in labels.items() }
        return JsonDict(ls)

    def _transform(self, content:str, path:Optional[str]=None, tokens:Optional[Dict[str,str]]=None, transform_labels=True) -> str:
        if tokens is None and path is None:
            print(f"Warning: _transform with no path and no tokens")
            tokens = {}
        elif tokens is None:
            tokens:JsonDict = self.get_tokens(path)
        if path is not None and transform_labels:
            tokens = self._add_labels_to_tokens(path, tokens)
        tokens["get_doc"] = self.get_doc
        template = Template(content)
        return template.render(tokens)

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
        filepath = self._get_full_file_path(path)
        try:
            content = self._read_doc(filepath)
            lines = [DocPath(line) for line in content.split('\n')]
            return lines
        except DocNotFoundException:
            return None

    def _read_doc(self, path:FilePath) -> str:
        return self._reader.read(path, None)
        #try:
        #    with open(path) as f:
        #        return f.read()
        #except FileNotFoundError as fnfe:
        #    print(f'cannot read: {fnfe}')
        #    raise DocNotFoundException(f"unreadable path: {path}")

    def _get_filename(self, path:str) -> Optional[str]:
        filename = None
        hashmark = path.find(self._hashmark)
        if hashmark > -1:
            filename = path[hashmark+1:]
        return filename

    def _get_dict(self, path:str, filename:str) -> JsonDict:
        path = path.strip('/\\')
        docroot = self.get_doc_root()
        introot = self.get_internal_root()
        tf = DictFinder(introot, docroot, path, filename)
        return JsonDict(tf.get_tokens())

    def _get_full_file_path(self, path:DocPath) -> FilePath:
        path = path.strip('/\\')
        filename = self._get_filename(path)
        if filename is None:
            pass
        else:
            path = path[0:path.find(self._hashmark)]
        root = self.get_doc_root()
        path = os.path.join(root, path)
        if filename is None and path.find(".") == -1:
            path = path + "." + self._ext
        elif filename is None:
            pass
        else:
            path = path + os.path.sep + filename + '.' + self._ext
        return FilePath(path)

