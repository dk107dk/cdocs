import os
import json
from pathlib import Path
from typing import Optional, List
from jinja2 import Template
from cdocs.config import Config
from cdocs.contextual_docs import ContextualDocs
from cdocs.dict_finder import DictFinder

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

    def get_doc_root(self) -> str:
        return self._docs_path

    def get_internal_root(self) -> str:
        return self._internal_path

    def get_tokens(self, path:str) -> dict:
        return self._get_dict(path, self._tokens_filename)

    def get_labels(self, path:str) -> dict:
        return self._get_dict(path, self._labels_filename)

    def get_compose_doc(self, path:str) -> str:
        if path is None :
            raise DocNotFoundException("path can not be None")
        if path.find('.html') == -1 and path.find('.md') == -1 and path.find('.xml') == -1:
            raise BadDocPath("file at path must be .html, .md or .xml")
        docpath = self._get_full_doc_path(path)
        try:
            content = self._read_doc(docpath)
            tokens:dict = self.get_tokens(path[0:path.rindex('/')])
            tokens["get_doc"] = self.get_doc
            template = Template(content)
            content = template.render(tokens)
            return content
        except Exception as e:
            print(f"cannot compose {path}: {e}")
            raise ComposeDocException(f'{path} failed to compose')

    def get_concat_doc(self, path:str) -> str:
        if path is None :
            raise DocNotFoundException("path can not be None")
        if path.find('.txt') == -1:
            raise BadDocPath("path must have a .txt file extension")
        paths = self._get_concat_paths(path)
        if paths is None:
            raise DocNotFoundException(f'No concat instruction file at {path}')
        result = ''
        for apath in paths:
            if apath.strip() == '':
                pass
            else:
                doc = self.get_doc(apath)
                result += '\n' + doc
        return result

    def get_doc(self, path:str) -> str:
        if path is None :
            raise DocNotFoundException("path can not be None")
        if path.find('.') > -1:
            raise BadDocPath("dots are not allowed in doc paths")
        docpath = self._get_full_doc_path(path)
        content = self._read_doc(docpath)
        content = self._transform(path, content)
        return content

    def _get_concat_paths(self, path:str) -> Optional[List[str]]:
        docpath = self._get_full_doc_path(path)
        try:
            content = self._read_doc(docpath)
            lines = content.split('\n')
            return lines
        except DocNotFoundException:
            return None

    def _read_doc(self, path:str) -> str:
        try:
            with open(path) as f:
                return f.read()
        except FileNotFoundError as fnfe:
            print(f'cannot read: {fnfe}')
            raise DocNotFoundException(f"unreadable path: {path}")

    def _get_filename(self, path:str) -> Optional[str]:
        filename = None
        hashmark = path.find(self._hashmark)
        if hashmark > -1:
            filename = path[hashmark+1:]
        return filename

    def _transform(self, path:str, content:str) -> str:
        tokens:dict = self.get_tokens(path)
        template = Template(content)
        content = template.render(tokens)
        return content

    def _get_dict(self, path:str, filename:str) -> dict:
        path = path.strip('/\\')
        docroot = self.get_doc_root()
        introot = self.get_internal_root()
        tf = DictFinder(introot, docroot, path, filename)
        return tf.get_tokens()

    def _get_full_doc_path(self, path:str) -> str:
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
        return path

