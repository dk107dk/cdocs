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
    """ cdocs gets:
            - get_doc: docs at paths like /x/y/z with the physical file being
              at <root>/x/y/z.[ext]. this is the "default" doc for the path. the result
              text will be treated as a jinja template. the template will receive
              a dict created from all the [tokens].json files from the doc's directory
              up to the root, and the same from the same directory under the internal
              tree.
            - get_labels: labels as json for paths like /x/y/z found as <root>/x/y/z/labels.json
            - get_doc: docs at paths like /x/y/z#name found as <root>/x/y/z/name.[ext].
              these docs are processed in the same way as the default doc.
            - get_concat_doc: docs as concats of files for paths like /x/y/z found as
              <root>/x/y/z/page.txt where page.txt is a list of simple doc names
              to be concationated. simple doc names are the same as docs named
              by the #name path suffix. the files to be concationated must be
              in the directory pointed to by the path.
            - get_compose_doc: docs as jinja files at paths like /x/y/z/page.html that
              compose pages where docs are pulled in using jinja expressions like:
              {{ get_doc('/app/home/teams/todos/assignee#edit_assignee') }}
              get_compose_doc requires the compose template be .xml, .html or .md. a
              compose doc could be referenced by a concat file, or vice versa, but the
              reference will only include the file contents; it will not be transformed.
        TODO:
            - indicate a transformer for default and #name docs. e.g. to transform
              xml > md, md > html, etc.
            - think about if all docs should be able to pull in other docs, not just the
              compose docs.
            - think about if concat and compose docs should be transformed before being
              included in the other type. e.g. if /x/y/z/concat.txt included /x/compose.html
              then compose.html would be rendered before being concatinated.
            - create a flask api for requesting docs and labels
    """
    def __init__(self):
        self._docs_path = Config.get("docs", "public")
        self._internal_path = Config.get("docs", "internal")
        self._ext = Config.get("formats", "ext")
        self._tokens_filename = Config.get("filenames", "tokens")
        self._labels_filename = Config.get("filenames", "labels")

    def get_doc_root(self) -> str:
        return self._docs_path

    def get_internal_root(self) -> str:
        return self._internal_path

    def _get_filename(self, path:str) -> Optional[str]:
        filename = None
        hashmark = path.find("#")
        if hashmark > -1:
            filename = path[hashmark+1:]
        return filename

    def get_compose_doc(self, path:str) -> str:
        if path is None :
            raise DocNotFoundException("path can not be None")
        if path.find('.html') == -1 and path.find('.md') == -1 and path.find('.xml') == -1:
            raise BadDocPath("file at path must be .html, .md or .xml")
        print(f"print concat docs: path is {path}")
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

    def _get_concat_paths(self, path:str) -> Optional[List[str]]:
        docpath = self._get_full_doc_path(path)
        try:
            content = self._read_doc(docpath)
            lines = content.split('\n')
            return lines
        except DocNotFoundException:
            return None

    def get_doc(self, path:str) -> str:
        if path is None :
            raise DocNotFoundException("path can not be None")
        if path.find('.') > -1:
            raise BadDocPath("dots are not allowed in doc paths")
        docpath = self._get_full_doc_path(path)
        content = self._read_doc(docpath)
        content = self._transform(path, content)
        return content

    def _read_doc(self, path:str) -> str:
        try:
            with open(path) as f:
                return f.read()
        except FileNotFoundError as fnfe:
            print(f'cannot read: {fnfe}')
            raise DocNotFoundException(f"unreadable path: {path}")

    def _transform(self, path:str, content:str) -> str:
        tokens:dict = self.get_tokens(path)
        template = Template(content)
        content = template.render(tokens)
        return content

    def get_tokens(self, path:str) -> dict:
        return self._get_dict(path, self._tokens_filename)

    def get_labels(self, path:str) -> dict:
        return self._get_dict(path, self._labels_filename)

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
            path = path[0:path.find('#')]
        root = self.get_doc_root()
        path = os.path.join(root, path)
        if filename is None and path.find(".") == -1:
            path = path + "." + self._ext
        elif filename is None:
            pass
        else:
            path = path + os.path.sep + filename + '.' + self._ext
        return path

